#!/usr/bin/env python3
"""
Generate FACT_FRAMEWORK_ADOPTIONS data.

This creates realistic framework adoption patterns based on customer industry,
segment, and compliance maturity, following USA adoption patterns.
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

def load_customers() -> List[Dict[str, Any]]:
    """Load customer data."""
    with open('../data/DIM_CUSTOMERS.json', 'r') as f:
        return json.load(f)

def load_frameworks() -> List[Dict[str, Any]]:
    """Load compliance frameworks data."""
    with open('../data/DIM_COMPLIANCE_FRAMEWORKS.json', 'r') as f:
        return json.load(f)

def parse_date(date_str: str) -> datetime:
    """Parse date from MM/DD/YYYY format."""
    return datetime.strptime(date_str, '%m/%d/%Y')

def format_date(date: datetime) -> str:
    """Format date to MM/DD/YYYY."""
    return date.strftime('%m/%d/%Y')

def get_framework_adoption_probability(customer: Dict[str, Any], framework_name: str) -> float:
    """
    Determine probability of framework adoption based on customer industry and characteristics.
    
    USA adoption patterns from GAMEPLAN.md.
    """
    industry = customer.get('industry', 'other')
    
    # Base adoption rates for USA companies
    base_rates = {
        'SOC2_Type_I': 0.95,      # Universal for B2B SaaS
        'SOC2_Type_II': 0.70,     # More comprehensive audit
        'ISO27001': 0.40,         # International business
        'HIPAA': 0.05,            # Default 5% for non-healthtech
        'GDPR': 0.35,             # European customers/data
        'PCI_DSS': 0.15,          # Default 15% for non-payment
        'FedRAMP': 0.02,          # Default 2% for non-government
        'NIST_CSF': 0.75          # Widely adopted cybersecurity
    }
    
    # Industry-specific adjustments
    industry_multipliers = {
        'healthtech': {
            'HIPAA': 0.95,        # 95% for healthtech
            'SOC2_Type_I': 0.98,  # Even higher for healthcare
            'SOC2_Type_II': 0.85,
            'GDPR': 0.45          # Health data = more GDPR
        },
        'fintech': {
            'PCI_DSS': 0.90,      # 90% for fintech
            'SOC2_Type_I': 0.98,  # Financial services need SOC2
            'SOC2_Type_II': 0.85,
            'FedRAMP': 0.15       # Some fintech serves government
        },
        'ecommerce': {
            'PCI_DSS': 0.90,      # 90% for ecommerce
            'GDPR': 0.50,         # E-commerce often global
            'SOC2_Type_I': 0.95
        },
        'government_contractors': {
            'FedRAMP': 0.80,      # 80% for government contractors
            'NIST_CSF': 0.95,     # Government loves NIST
            'SOC2_Type_I': 0.90
        },
        'saas': {
            'SOC2_Type_I': 0.98,  # SaaS companies need SOC2
            'SOC2_Type_II': 0.80,
            'ISO27001': 0.55,     # SaaS often international
            'GDPR': 0.45
        }
    }
    
    # Get base probability
    probability = base_rates.get(framework_name, 0.10)
    
    # Apply industry-specific multipliers
    if industry in industry_multipliers:
        if framework_name in industry_multipliers[industry]:
            probability = industry_multipliers[industry][framework_name]
    
    # Segment adjustments
    segment = customer.get('segment', 'startup')
    if segment == 'enterprise':
        # Enterprises adopt more frameworks
        probability = min(probability * 1.2, 0.95)
    elif segment == 'startup':
        # Startups adopt fewer frameworks initially
        if framework_name not in ['SOC2_Type_I', 'NIST_CSF']:
            probability = probability * 0.8
    
    # Compliance maturity adjustments
    maturity = customer.get('compliance_maturity', 'intermediate')
    if maturity == 'advanced':
        probability = min(probability * 1.15, 0.95)
    elif maturity == 'beginner':
        if framework_name not in ['SOC2_Type_I']:  # Everyone needs SOC2
            probability = probability * 0.7
    
    return min(probability, 0.95)  # Cap at 95%

def determine_framework_adoptions_for_customer(customer: Dict[str, Any], frameworks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Determine which frameworks a customer adopts based on industry patterns."""
    adoptions = []
    
    # Framework dependency logic - SOC2 Type I usually comes before Type II
    soc2_type_i_adopted = False
    
    for framework in frameworks:
        framework_name = framework['framework_name']
        probability = get_framework_adoption_probability(customer, framework_name)
        
        # Special logic for SOC2 Type II - requires Type I first
        if framework_name == 'SOC2_Type_II':
            if not soc2_type_i_adopted:
                probability = probability * 0.3  # Much lower chance without Type I
        
        # Decide adoption
        if random.random() < probability:
            adoptions.append(framework)
            
            if framework_name == 'SOC2_Type_I':
                soc2_type_i_adopted = True
    
    # Ensure minimum adoptions (everyone needs at least SOC2 Type I and one other)
    if len(adoptions) == 0:
        # Force SOC2 Type I for everyone
        soc2_type_i = next(f for f in frameworks if f['framework_name'] == 'SOC2_Type_I')
        adoptions.append(soc2_type_i)
        
        # Add NIST CSF as common second framework
        nist_csf = next(f for f in frameworks if f['framework_name'] == 'NIST_CSF')
        if random.random() < 0.7:
            adoptions.append(nist_csf)
    
    return adoptions

def generate_adoption_dates(customer: Dict[str, Any], framework: Dict[str, Any]) -> Tuple[datetime, datetime]:
    """Generate start and completion dates for framework adoption."""
    signup_date = parse_date(customer['signup_date'])
    
    # Start date: 0-365 days after signup (most start within first year)
    days_after_signup = random.randint(0, 365)
    start_date = signup_date + timedelta(days=days_after_signup)
    
    # Base completion time from framework
    base_completion_days = framework['avg_completion_days']
    
    # Adjust based on customer compliance maturity
    maturity = customer.get('compliance_maturity', 'intermediate')
    if maturity == 'advanced':
        # Advanced customers complete 20% faster
        completion_days = int(base_completion_days * 0.8)
    elif maturity == 'beginner':
        # Beginner customers take 30% longer
        completion_days = int(base_completion_days * 1.3)
    else:
        # Intermediate customers use baseline
        completion_days = base_completion_days
    
    # Add random variance (±30 days)
    variance = random.randint(-30, 30)
    completion_days = max(completion_days + variance, 30)  # Minimum 30 days
    
    completion_date = start_date + timedelta(days=completion_days)
    
    return start_date, completion_date

def determine_status(completion_date: datetime) -> str:
    """Determine adoption status based on completion date and current time."""
    current_date = datetime.now()
    
    if completion_date > current_date:
        return 'active'  # Still in progress
    else:
        # Completed - decide between completed and certified
        return random.choices(['completed', 'certified'], weights=[0.67, 0.33])[0]

def calculate_audit_score(customer: Dict[str, Any], framework: Dict[str, Any]) -> int:
    """Calculate audit score based on customer maturity and framework complexity."""
    maturity = customer.get('compliance_maturity', 'intermediate')
    complexity = framework.get('complexity_score', 5)
    
    # Base score ranges by maturity
    if maturity == 'advanced':
        base_range = (85, 98)
    elif maturity == 'intermediate':
        base_range = (75, 90)
    else:  # beginner
        base_range = (65, 85)
    
    # Adjust for framework complexity (harder frameworks = lower scores initially)
    complexity_penalty = (complexity - 5) * 2  # -8 to +8 points
    
    min_score = max(base_range[0] - complexity_penalty, 50)
    max_score = max(base_range[1] - complexity_penalty, min_score + 10)
    
    return random.randint(int(min_score), int(max_score))

def calculate_hours_saved(customer: Dict[str, Any], framework: Dict[str, Any]) -> int:
    """Calculate hours saved through automation."""
    segment = customer.get('segment', 'startup')
    complexity = framework.get('complexity_score', 5)
    automation_pct = framework.get('automation_percentage', 50)
    maturity = customer.get('compliance_maturity', 'intermediate')
    
    # Base hours by complexity
    base_hours = complexity * 200  # 200-1800 hours range
    
    # Segment multiplier (larger companies = more hours saved)
    segment_multipliers = {
        'startup': 0.7,
        'mid_market': 1.0,
        'enterprise': 1.5
    }
    
    # Maturity multiplier (advanced companies save more)
    maturity_multipliers = {
        'beginner': 0.8,
        'intermediate': 1.0,
        'advanced': 1.3
    }
    
    # Calculate total hours saved
    total_hours = base_hours * segment_multipliers.get(segment, 1.0)
    total_hours = total_hours * maturity_multipliers.get(maturity, 1.0)
    total_hours = total_hours * (automation_pct / 100)
    
    # Add some variance
    variance = random.uniform(0.8, 1.2)
    total_hours = int(total_hours * variance)
    
    return max(total_hours, 50)  # Minimum 50 hours

def calculate_implementation_cost(customer: Dict[str, Any], framework: Dict[str, Any]) -> int:
    """Calculate implementation cost based on customer segment."""
    segment = customer.get('segment', 'startup')
    base_cost = framework.get('certification_cost_usd', 25000)
    
    # Segment multipliers from GAMEPLAN.md
    segment_multipliers = {
        'startup': random.uniform(0.5, 0.8),      # 50-80% of certification cost
        'mid_market': random.uniform(0.8, 1.2),   # 80-120% of certification cost
        'enterprise': random.uniform(1.0, 2.0)    # 100-200% of certification cost
    }
    
    multiplier = segment_multipliers.get(segment, 1.0)
    cost = int(base_cost * multiplier)
    
    return cost

def calculate_automation_level(customer: Dict[str, Any], framework: Dict[str, Any]) -> int:
    """Calculate automation level achieved by customer."""
    base_automation = framework.get('automation_percentage', 50)
    maturity = customer.get('compliance_maturity', 'intermediate')
    
    # Maturity adjustments from GAMEPLAN.md
    if maturity == 'advanced':
        adjustment = random.uniform(10, 20)  # +10-20%
    elif maturity == 'intermediate':
        adjustment = random.uniform(-5, 5)   # ±5%
    else:  # beginner
        adjustment = random.uniform(-15, -10) # -10-15%
    
    automation_level = base_automation + adjustment
    return int(max(0, min(automation_level, 100)))  # Clamp to 0-100

def generate_framework_adoptions(customers: List[Dict[str, Any]], 
                                frameworks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate all framework adoption records."""
    adoptions = []
    adoption_id_counter = 1
    
    for customer in customers:
        # Determine which frameworks this customer adopts
        customer_frameworks = determine_framework_adoptions_for_customer(customer, frameworks)
        
        for framework in customer_frameworks:
            # Generate dates
            start_date, completion_date = generate_adoption_dates(customer, framework)
            
            # Create adoption record
            adoption = {
                'adoption_id': adoption_id_counter,
                'customer_id': customer['customer_id'],
                'framework_id': framework['framework_id'],
                'start_date': format_date(start_date),
                'completion_date': format_date(completion_date),
                'status': determine_status(completion_date),
                'audit_score': calculate_audit_score(customer, framework),
                'hours_saved': calculate_hours_saved(customer, framework),
                'implementation_cost': calculate_implementation_cost(customer, framework),
                'automation_level': calculate_automation_level(customer, framework)
            }
            
            adoptions.append(adoption)
            adoption_id_counter += 1
    
    return adoptions

def validate_framework_adoptions(adoptions: List[Dict[str, Any]], 
                                customers: List[Dict[str, Any]], 
                                frameworks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate framework adoption data quality."""
    issues = []
    
    # Framework adoption rate analysis
    framework_counts = {}
    for adoption in adoptions:
        framework_id = adoption['framework_id']
        framework_counts[framework_id] = framework_counts.get(framework_id, 0) + 1
    
    total_customers = len(customers)
    framework_adoption_rates = {}
    
    for framework in frameworks:
        framework_id = framework['framework_id']
        framework_name = framework['framework_name']
        count = framework_counts.get(framework_id, 0)
        rate = (count / total_customers) * 100
        framework_adoption_rates[framework_name] = {
            'count': count,
            'rate': rate,
            'expected_min': 0,  # Will be set below
            'expected_max': 100
        }
    
    # Check expected adoption rates
    expected_rates = {
        'SOC2_Type_I': (90, 98),     # Should be 95% ± variance
        'SOC2_Type_II': (60, 80),    # Should be 70% ± variance
        'NIST_CSF': (65, 85),        # Should be 75% ± variance
        'ISO27001': (30, 50),        # Should be 40% ± variance
        'GDPR': (25, 45),            # Should be 35% ± variance
    }
    
    for framework_name, (min_rate, max_rate) in expected_rates.items():
        if framework_name in framework_adoption_rates:
            actual_rate = framework_adoption_rates[framework_name]['rate']
            framework_adoption_rates[framework_name]['expected_min'] = min_rate
            framework_adoption_rates[framework_name]['expected_max'] = max_rate
            
            if actual_rate < min_rate or actual_rate > max_rate:
                issues.append(f"{framework_name} adoption rate {actual_rate:.1f}% outside expected range {min_rate}-{max_rate}%")
    
    # Temporal validation
    temporal_issues = 0
    for adoption in adoptions:
        try:
            start_date = parse_date(adoption['start_date'])
            completion_date = parse_date(adoption['completion_date'])
            
            if completion_date <= start_date:
                temporal_issues += 1
        except ValueError:
            temporal_issues += 1
    
    if temporal_issues > 0:
        issues.append(f"{temporal_issues} adoptions have invalid date sequences")
    
    # Customer coverage
    customers_with_adoptions = len(set(a['customer_id'] for a in adoptions))
    if customers_with_adoptions < total_customers:
        issues.append(f"{total_customers - customers_with_adoptions} customers have no framework adoptions")
    
    # Status distribution
    status_counts = {}
    for adoption in adoptions:
        status = adoption['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    return {
        'total_adoptions': len(adoptions),
        'customers_with_adoptions': customers_with_adoptions,
        'avg_adoptions_per_customer': len(adoptions) / total_customers,
        'framework_adoption_rates': framework_adoption_rates,
        'status_distribution': status_counts,
        'temporal_issues': temporal_issues,
        'issues': issues
    }

def print_validation_summary(validation: Dict[str, Any]) -> None:
    """Print comprehensive validation summary."""
    
    print("📊 FRAMEWORK ADOPTIONS VALIDATION SUMMARY")
    print("=" * 60)
    
    print(f"\n📈 BASIC METRICS:")
    print(f"Total Adoptions: {validation['total_adoptions']}")
    print(f"Customers with Adoptions: {validation['customers_with_adoptions']}")
    print(f"Avg Adoptions per Customer: {validation['avg_adoptions_per_customer']:.1f}")
    
    print(f"\n🏗️ FRAMEWORK ADOPTION RATES:")
    for framework_name, data in validation['framework_adoption_rates'].items():
        count = data['count']
        rate = data['rate']
        expected_min = data.get('expected_min', 0)
        expected_max = data.get('expected_max', 100)
        
        status = "✅" if expected_min <= rate <= expected_max else "⚠️"
        expected_range = f"({expected_min}-{expected_max}%)" if expected_min > 0 else ""
        
        print(f"  {framework_name}: {count} adoptions ({rate:.1f}%) {expected_range} {status}")
    
    print(f"\n📋 STATUS DISTRIBUTION:")
    for status, count in validation['status_distribution'].items():
        percentage = (count / validation['total_adoptions']) * 100
        print(f"  {status}: {count} ({percentage:.1f}%)")
    
    if validation['issues']:
        print(f"\n⚠️  Issues Found ({len(validation['issues'])}):")
        for issue in validation['issues']:
            print(f"  - {issue}")
    else:
        print(f"\n✨ No data quality issues found!")

def main():
    print("🚀 Generating FACT_FRAMEWORK_ADOPTIONS data...")
    
    # Load dependencies
    print("📖 Loading customer and framework data...")
    customers = load_customers()
    frameworks = load_frameworks()
    print(f"Loaded {len(customers)} customers and {len(frameworks)} frameworks")
    
    # Generate adoptions
    print("🔄 Generating framework adoption patterns...")
    adoptions = generate_framework_adoptions(customers, frameworks)
    print(f"Generated {len(adoptions)} framework adoptions")
    
    # Validate
    print("\n✅ Validating framework adoption data...")
    validation = validate_framework_adoptions(adoptions, customers, frameworks)
    print_validation_summary(validation)
    
    # Save data
    output_file = '../data/FACT_FRAMEWORK_ADOPTIONS.json'
    print(f"\n💾 Saving {len(adoptions)} adoptions to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(adoptions, f, indent=2)
    
    print("🎉 FACT_FRAMEWORK_ADOPTIONS generation complete!")

if __name__ == "__main__":
    main()