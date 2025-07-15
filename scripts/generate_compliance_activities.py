#!/usr/bin/env python3
"""
Generate FACT_COMPLIANCE_ACTIVITIES data.

This creates granular compliance work events that occur during framework
implementation and ongoing monitoring, with realistic temporal clustering
and business logic.
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import statistics

def load_customers() -> List[Dict[str, Any]]:
    """Load customer data."""
    with open('../data/DIM_CUSTOMERS.json', 'r') as f:
        return json.load(f)

def load_frameworks() -> List[Dict[str, Any]]:
    """Load compliance frameworks data."""
    with open('../data/DIM_COMPLIANCE_FRAMEWORKS.json', 'r') as f:
        return json.load(f)

def load_framework_adoptions() -> List[Dict[str, Any]]:
    """Load framework adoptions data."""
    with open('../data/FACT_FRAMEWORK_ADOPTIONS.json', 'r') as f:
        return json.load(f)

def parse_date(date_str: str) -> datetime:
    """Parse date from MM/DD/YYYY format."""
    return datetime.strptime(date_str, '%m/%d/%Y')

def format_date(date: datetime) -> str:
    """Format date to MM/DD/YYYY."""
    return date.strftime('%m/%d/%Y')

def get_activity_type() -> str:
    """Get activity type based on realistic distribution."""
    return random.choices(
        ['control_check', 'questionnaire', 'remediation', 'training', 'audit'],
        weights=[0.50, 0.20, 0.15, 0.10, 0.05]
    )[0]

def get_control_category() -> str:
    """Get control category based on realistic distribution."""
    return random.choices(
        ['access_control', 'data_protection', 'network_security', 'monitoring', 'incident_response'],
        weights=[0.25, 0.25, 0.20, 0.20, 0.10]
    )[0]

def get_risk_level() -> str:
    """Get risk level based on realistic distribution."""
    return random.choices(
        ['low', 'medium', 'high', 'critical'],
        weights=[0.40, 0.30, 0.20, 0.10]
    )[0]

def calculate_automation_rate(framework: Dict[str, Any], customer: Dict[str, Any]) -> float:
    """Calculate automation rate based on framework and customer maturity."""
    base_automation = framework.get('automation_percentage', 50) / 100
    maturity = customer.get('compliance_maturity', 'intermediate')
    
    # Maturity adjustments
    if maturity == 'advanced':
        automation_rate = base_automation + 0.15  # +15%
    elif maturity == 'beginner':
        automation_rate = base_automation - 0.10  # -10%
    else:  # intermediate
        automation_rate = base_automation
    
    return max(0.0, min(automation_rate, 1.0))  # Clamp to 0-100%

def determine_if_automated(automation_rate: float, activity_type: str) -> bool:
    """Determine if an activity is automated."""
    # Some activities are never automated
    if activity_type in ['audit', 'training']:
        return False
    
    return random.random() < automation_rate

def calculate_duration_minutes(activity_type: str, automated: bool) -> int:
    """Calculate activity duration based on type and automation."""
    duration_ranges = {
        'control_check': {'automated': (5, 30), 'manual': (30, 120)},
        'questionnaire': {'automated': (10, 45), 'manual': (60, 240)},
        'audit': {'automated': (240, 480), 'manual': (240, 480)},  # Always manual
        'remediation': {'automated': (30, 90), 'manual': (120, 480)},
        'training': {'automated': (60, 180), 'manual': (60, 180)}  # Always manual
    }
    
    range_key = 'automated' if automated else 'manual'
    min_duration, max_duration = duration_ranges[activity_type][range_key]
    
    return random.randint(min_duration, max_duration)

def calculate_success_rate(customer: Dict[str, Any], automated: bool) -> float:
    """Calculate success rate based on customer maturity and automation."""
    maturity = customer.get('compliance_maturity', 'intermediate')
    
    # Base success rates by maturity
    base_rates = {
        'advanced': random.uniform(0.90, 0.95),
        'intermediate': random.uniform(0.85, 0.90),
        'beginner': random.uniform(0.75, 0.85)
    }
    
    success_rate = base_rates[maturity]
    
    # Automation bonus
    if automated:
        success_rate += random.uniform(0.05, 0.10)  # +5-10%
    
    return min(success_rate, 0.98)  # Cap at 98%

def determine_success(success_rate: float) -> bool:
    """Determine if activity was successful."""
    return random.random() < success_rate

def determine_evidence_collected(activity_type: str, success: bool) -> bool:
    """Determine if evidence was collected."""
    # Evidence collection rates by activity type
    base_rates = {
        'control_check': 0.90,
        'questionnaire': 0.85,
        'audit': 0.95,
        'remediation': 0.70,
        'training': 0.60
    }
    
    evidence_rate = base_rates.get(activity_type, 0.75)
    
    # Lower rate if activity failed
    if not success:
        evidence_rate *= 0.5
    
    return random.random() < evidence_rate

def generate_activity_dates(adoption: Dict[str, Any], num_activities: int) -> List[datetime]:
    """Generate activity dates with realistic clustering."""
    start_date = parse_date(adoption['start_date'])
    completion_date = parse_date(adoption['completion_date'])
    
    # Extend timeline 90 days past completion for ongoing monitoring
    end_date = completion_date + timedelta(days=90)
    
    total_days = (end_date - start_date).days
    
    # Generate dates with clustering near start and completion
    dates = []
    
    for _ in range(num_activities):
        # Create bias toward start (40%), middle (20%), completion (30%), post-completion (10%)
        phase = random.choices(['start', 'middle', 'completion', 'post'], weights=[0.4, 0.2, 0.3, 0.1])[0]
        
        if phase == 'start':
            # First 20% of timeline
            days_offset = random.randint(0, max(1, int(total_days * 0.2)))
        elif phase == 'middle':
            # Middle 40% of timeline
            start_offset = int(total_days * 0.2)
            end_offset = int(total_days * 0.6)
            # Ensure valid range
            end_offset = max(start_offset + 1, end_offset)
            days_offset = random.randint(start_offset, end_offset)
        elif phase == 'completion':
            # Last 30% before completion
            start_offset = int(total_days * 0.6)
            completion_offset = (completion_date - start_date).days
            # Ensure valid range
            end_offset = max(start_offset + 1, completion_offset)
            days_offset = random.randint(start_offset, end_offset)
        else:  # post-completion
            # 90 days after completion
            completion_offset = (completion_date - start_date).days
            # Ensure valid range
            end_offset = max(completion_offset + 1, total_days)
            days_offset = random.randint(completion_offset, end_offset)
        
        activity_date = start_date + timedelta(days=days_offset)
        dates.append(activity_date)
    
    return sorted(dates)

def calculate_activities_per_adoption(framework: Dict[str, Any], customer: Dict[str, Any]) -> int:
    """Calculate number of activities for a framework adoption."""
    complexity = framework.get('complexity_score', 5)
    segment = customer.get('segment', 'startup')
    
    # Base activities by complexity (10-20 activities per complexity point)
    base_activities = complexity * random.randint(10, 20)
    
    # Segment multipliers
    segment_multipliers = {
        'startup': 0.7,      # Smaller scale
        'mid_market': 1.0,   # Baseline
        'enterprise': 1.4    # More complex processes
    }
    
    multiplier = segment_multipliers.get(segment, 1.0)
    activities = int(base_activities * multiplier)
    
    # Add some variance
    variance = random.uniform(0.8, 1.2)
    activities = int(activities * variance)
    
    return max(activities, 5)  # Minimum 5 activities per adoption

def generate_activities_for_adoption(adoption: Dict[str, Any], 
                                   framework: Dict[str, Any],
                                   customer: Dict[str, Any],
                                   activity_id_counter: int) -> Tuple[List[Dict[str, Any]], int]:
    """Generate all activities for a single framework adoption."""
    activities = []
    
    # Calculate number of activities
    num_activities = calculate_activities_per_adoption(framework, customer)
    
    # Generate activity dates
    activity_dates = generate_activity_dates(adoption, num_activities)
    
    # Calculate automation rate for this customer/framework
    automation_rate = calculate_automation_rate(framework, customer)
    
    for activity_date in activity_dates:
        # Generate activity details
        activity_type = get_activity_type()
        automated = determine_if_automated(automation_rate, activity_type)
        duration = calculate_duration_minutes(activity_type, automated)
        success_rate = calculate_success_rate(customer, automated)
        success = determine_success(success_rate)
        evidence = determine_evidence_collected(activity_type, success)
        
        activity = {
            'activity_id': activity_id_counter,
            'customer_id': adoption['customer_id'],
            'framework_id': adoption['framework_id'],
            'adoption_id': adoption['adoption_id'],
            'activity_date': format_date(activity_date),
            'activity_type': activity_type,
            'control_category': get_control_category(),
            'automated_flag': automated,
            'duration_minutes': duration,
            'success_flag': success,
            'risk_level': get_risk_level(),
            'evidence_collected': evidence
        }
        
        activities.append(activity)
        activity_id_counter += 1
    
    return activities, activity_id_counter

def generate_compliance_activities(adoptions: List[Dict[str, Any]],
                                 frameworks: List[Dict[str, Any]],
                                 customers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate all compliance activities."""
    
    # Create lookup dictionaries
    framework_lookup = {f['framework_id']: f for f in frameworks}
    customer_lookup = {c['customer_id']: c for c in customers}
    
    all_activities = []
    activity_id_counter = 1
    
    print(f"Generating activities for {len(adoptions)} framework adoptions...")
    
    for i, adoption in enumerate(adoptions):
        framework = framework_lookup.get(adoption['framework_id'])
        customer = customer_lookup.get(adoption['customer_id'])
        
        if framework and customer:
            activities, activity_id_counter = generate_activities_for_adoption(
                adoption, framework, customer, activity_id_counter
            )
            all_activities.extend(activities)
        
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(adoptions)} adoptions...")
    
    return all_activities

def validate_compliance_activities(activities: List[Dict[str, Any]],
                                 adoptions: List[Dict[str, Any]],
                                 customers: List[Dict[str, Any]],
                                 frameworks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Comprehensive validation of compliance activities data."""
    issues = []
    
    # Basic metrics
    total_activities = len(activities)
    unique_customers = len(set(a['customer_id'] for a in activities))
    unique_adoptions = len(set(a['adoption_id'] for a in activities))
    
    # Activity distribution analysis
    activity_types = {}
    control_categories = {}
    risk_levels = {}
    automation_stats = {'automated': 0, 'manual': 0}
    success_stats = {'successful': 0, 'failed': 0}
    evidence_stats = {'collected': 0, 'not_collected': 0}
    
    duration_by_type = {}
    
    for activity in activities:
        # Activity type distribution
        activity_type = activity.get('activity_type', 'unknown')
        activity_types[activity_type] = activity_types.get(activity_type, 0) + 1
        
        # Control category distribution
        control_category = activity.get('control_category', 'unknown')
        control_categories[control_category] = control_categories.get(control_category, 0) + 1
        
        # Risk level distribution
        risk_level = activity.get('risk_level', 'unknown')
        risk_levels[risk_level] = risk_levels.get(risk_level, 0) + 1
        
        # Automation stats
        if activity.get('automated_flag', False):
            automation_stats['automated'] += 1
        else:
            automation_stats['manual'] += 1
        
        # Success stats
        if activity.get('success_flag', False):
            success_stats['successful'] += 1
        else:
            success_stats['failed'] += 1
        
        # Evidence stats
        if activity.get('evidence_collected', False):
            evidence_stats['collected'] += 1
        else:
            evidence_stats['not_collected'] += 1
        
        # Duration analysis by type
        duration = activity.get('duration_minutes', 0)
        if activity_type not in duration_by_type:
            duration_by_type[activity_type] = []
        duration_by_type[activity_type].append(duration)
    
    # Temporal validation
    temporal_issues = 0
    for activity in activities:
        try:
            activity_date = parse_date(activity.get('activity_date', '01/01/2020'))
            
            # Find corresponding adoption
            adoption_id = activity.get('adoption_id')
            adoption = next((a for a in adoptions if a['adoption_id'] == adoption_id), None)
            
            if adoption:
                start_date = parse_date(adoption['start_date'])
                completion_date = parse_date(adoption['completion_date'])
                # Allow 90 days post-completion
                end_date = completion_date + timedelta(days=90)
                
                if activity_date < start_date or activity_date > end_date:
                    temporal_issues += 1
            
        except (ValueError, TypeError):
            temporal_issues += 1
    
    if temporal_issues > 0:
        issues.append(f"{temporal_issues} activities have dates outside adoption timeline")
    
    # Foreign key validation
    adoption_ids = {a['adoption_id'] for a in adoptions}
    activity_adoption_ids = {a['adoption_id'] for a in activities}
    orphaned_activities = activity_adoption_ids - adoption_ids
    
    if orphaned_activities:
        issues.append(f"{len(orphaned_activities)} activities reference non-existent adoptions")
    
    # Business logic validation
    automation_rate = automation_stats['automated'] / total_activities
    success_rate = success_stats['successful'] / total_activities
    evidence_rate = evidence_stats['collected'] / total_activities
    
    # Check for unrealistic rates
    if automation_rate > 0.8:
        issues.append(f"Automation rate too high: {automation_rate:.1%}")
    if success_rate < 0.7 or success_rate > 0.95:
        issues.append(f"Success rate outside expected range: {success_rate:.1%}")
    
    # Duration validation
    duration_issues = 0
    for activity_type, durations in duration_by_type.items():
        if durations:
            avg_duration = statistics.mean(durations)
            # Check for unrealistic averages
            if activity_type == 'control_check' and avg_duration > 150:
                duration_issues += 1
            elif activity_type == 'audit' and avg_duration < 200:
                duration_issues += 1
    
    if duration_issues > 0:
        issues.append(f"{duration_issues} activity types have unrealistic average durations")
    
    return {
        'total_activities': total_activities,
        'unique_customers': unique_customers,
        'unique_adoptions': unique_adoptions,
        'activities_per_customer': total_activities / len(customers) if customers else 0,
        'activities_per_adoption': total_activities / len(adoptions) if adoptions else 0,
        'activity_types': activity_types,
        'control_categories': control_categories,
        'risk_levels': risk_levels,
        'automation_rate': automation_rate,
        'success_rate': success_rate,
        'evidence_rate': evidence_rate,
        'duration_by_type': {k: statistics.mean(v) for k, v in duration_by_type.items()},
        'temporal_issues': temporal_issues,
        'issues': issues
    }

def print_validation_summary(validation: Dict[str, Any]) -> None:
    """Print comprehensive validation summary."""
    
    print("📊 COMPLIANCE ACTIVITIES VALIDATION SUMMARY")
    print("=" * 60)
    
    print(f"\n📈 BASIC METRICS:")
    print(f"Total Activities: {validation['total_activities']:,}")
    print(f"Unique Customers: {validation['unique_customers']}")
    print(f"Unique Adoptions: {validation['unique_adoptions']}")
    print(f"Activities per Customer: {validation['activities_per_customer']:.1f}")
    print(f"Activities per Adoption: {validation['activities_per_adoption']:.1f}")
    
    print(f"\n🎯 ACTIVITY TYPE DISTRIBUTION:")
    for activity_type, count in validation['activity_types'].items():
        percentage = (count / validation['total_activities']) * 100
        print(f"  {activity_type}: {count:,} ({percentage:.1f}%)")
    
    print(f"\n🔒 CONTROL CATEGORY DISTRIBUTION:")
    for category, count in validation['control_categories'].items():
        percentage = (count / validation['total_activities']) * 100
        print(f"  {category}: {count:,} ({percentage:.1f}%)")
    
    print(f"\n⚠️  RISK LEVEL DISTRIBUTION:")
    for risk_level, count in validation['risk_levels'].items():
        percentage = (count / validation['total_activities']) * 100
        print(f"  {risk_level}: {count:,} ({percentage:.1f}%)")
    
    print(f"\n🤖 BUSINESS METRICS:")
    print(f"Automation Rate: {validation['automation_rate']:.1%}")
    print(f"Success Rate: {validation['success_rate']:.1%}")
    print(f"Evidence Collection Rate: {validation['evidence_rate']:.1%}")
    
    print(f"\n⏱️  AVERAGE DURATION BY TYPE:")
    for activity_type, avg_duration in validation['duration_by_type'].items():
        print(f"  {activity_type}: {avg_duration:.0f} minutes")
    
    if validation['issues']:
        print(f"\n⚠️  Issues Found ({len(validation['issues'])}):")
        for issue in validation['issues']:
            print(f"  - {issue}")
    else:
        print(f"\n✨ No data quality issues found!")

def main():
    print("🚀 Generating FACT_COMPLIANCE_ACTIVITIES data...")
    
    # Load dependencies
    print("📖 Loading dependency data...")
    customers = load_customers()
    frameworks = load_frameworks()
    adoptions = load_framework_adoptions()
    
    print(f"Loaded: {len(customers)} customers, {len(frameworks)} frameworks, {len(adoptions)} adoptions")
    
    # Generate activities
    print("\n🔄 Generating compliance activities...")
    activities = generate_compliance_activities(adoptions, frameworks, customers)
    print(f"Generated {len(activities):,} compliance activities")
    
    # Validate
    print("\n✅ Validating compliance activities data...")
    validation = validate_compliance_activities(activities, adoptions, customers, frameworks)
    print_validation_summary(validation)
    
    # Save data
    output_file = '../data/FACT_COMPLIANCE_ACTIVITIES.json'
    print(f"\n💾 Saving {len(activities):,} activities to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(activities, f, indent=2)
    
    print("🎉 FACT_COMPLIANCE_ACTIVITIES generation complete!")

if __name__ == "__main__":
    main()