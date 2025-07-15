#!/usr/bin/env python3
"""
Update DIM_CUSTOMERS to use all 300 records with 5-year signup date range.

This script consolidates:
1. Use all 300 customers from MOCK_DATA_ORIGINAL.json
2. Expand signup dates to 5-year range (2020-2024)
3. Fix employee count alignment with segments
4. Fix revenue ranges alignment with segments
5. Add comprehensive quality validation
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

def load_data(filepath: str) -> List[Dict[str, Any]]:
    """Load customer data from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def expand_signup_dates_5_years(customers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Expand signup dates to 5-year range (2020-01-01 to 2024-12-31)."""
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range = (end_date - start_date).days
    
    for customer in customers:
        # Generate random date within 5-year range
        random_days = random.randint(0, date_range)
        signup_date = start_date + timedelta(days=random_days)
        customer['signup_date'] = signup_date.strftime('%m/%d/%Y')
    
    return customers

def fix_employee_count_by_segment(customers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Fix employee counts to align with segment definitions."""
    for customer in customers:
        segment = customer['segment']
        
        if segment == 'startup':
            # 1-50 employees
            customer['employee_count'] = random.randint(1, 50)
        elif segment == 'mid_market':
            # 51-500 employees
            customer['employee_count'] = random.randint(51, 500)
        else:  # enterprise
            # 501-10,000 employees
            customer['employee_count'] = random.randint(501, 10000)
    
    return customers

def fix_revenue_by_segment(customers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Fix revenue ranges to align with segment definitions."""
    for customer in customers:
        segment = customer['segment']
        
        if segment == 'startup':
            # $100K - $5M annual revenue
            customer['annual_revenue'] = random.randint(100000, 5000000)
        elif segment == 'mid_market':
            # $5M - $100M annual revenue
            customer['annual_revenue'] = random.randint(5000000, 100000000)
        else:  # enterprise
            # $100M - $1B annual revenue
            customer['annual_revenue'] = random.randint(100000000, 1000000000)
    
    return customers

def add_sequential_ids(customers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add sequential customer_id field."""
    for i, customer in enumerate(customers, 1):
        customer['customer_id'] = i
    return customers

def validate_customer_data(customers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Comprehensive validation of customer data quality."""
    
    # Segment distribution analysis
    segment_counts = {}
    for customer in customers:
        segment = customer['segment']
        segment_counts[segment] = segment_counts.get(segment, 0) + 1
    
    total_customers = len(customers)
    segment_percentages = {
        segment: (count / total_customers) * 100 
        for segment, count in segment_counts.items()
    }
    
    # Employee count validation by segment
    employee_violations = 0
    for customer in customers:
        segment = customer['segment']
        employee_count = customer['employee_count']
        
        if segment == 'startup' and not (1 <= employee_count <= 50):
            employee_violations += 1
        elif segment == 'mid_market' and not (51 <= employee_count <= 500):
            employee_violations += 1
        elif segment == 'enterprise' and not (501 <= employee_count <= 10000):
            employee_violations += 1
    
    # Revenue validation by segment
    revenue_violations = 0
    for customer in customers:
        segment = customer['segment']
        revenue = customer['annual_revenue']
        
        if segment == 'startup' and not (100000 <= revenue <= 5000000):
            revenue_violations += 1
        elif segment == 'mid_market' and not (5000000 <= revenue <= 100000000):
            revenue_violations += 1
        elif segment == 'enterprise' and not (100000000 <= revenue <= 1000000000):
            revenue_violations += 1
    
    # Date range validation
    signup_dates = [datetime.strptime(c['signup_date'], '%m/%d/%Y') for c in customers]
    min_date = min(signup_dates)
    max_date = max(signup_dates)
    
    # Industry distribution
    industry_counts = {}
    for customer in customers:
        industry = customer['industry']
        industry_counts[industry] = industry_counts.get(industry, 0) + 1
    
    return {
        'total_customers': total_customers,
        'segment_distribution': segment_counts,
        'segment_percentages': segment_percentages,
        'employee_violations': employee_violations,
        'employee_violation_rate': (employee_violations / total_customers) * 100,
        'revenue_violations': revenue_violations,
        'revenue_violation_rate': (revenue_violations / total_customers) * 100,
        'signup_date_range': {
            'min_date': min_date.strftime('%Y-%m-%d'),
            'max_date': max_date.strftime('%Y-%m-%d'),
            'span_days': (max_date - min_date).days
        },
        'industry_distribution': industry_counts,
        'unique_industries': len(industry_counts)
    }

def print_validation_summary(validation: Dict[str, Any]) -> None:
    """Print comprehensive validation summary."""
    
    print("📊 DIM_CUSTOMERS VALIDATION SUMMARY")
    print("=" * 60)
    
    print(f"\n📈 BASIC METRICS:")
    print(f"Total Customers: {validation['total_customers']}")
    print(f"Signup Date Range: {validation['signup_date_range']['min_date']} to {validation['signup_date_range']['max_date']}")
    print(f"Date Span: {validation['signup_date_range']['span_days']} days ({validation['signup_date_range']['span_days']/365:.1f} years)")
    
    print(f"\n🏢 SEGMENT DISTRIBUTION:")
    for segment, count in validation['segment_distribution'].items():
        percentage = validation['segment_percentages'][segment]
        print(f"  {segment}: {count} customers ({percentage:.1f}%)")
    
    print(f"\n🏭 INDUSTRY DISTRIBUTION:")
    for industry, count in sorted(validation['industry_distribution'].items()):
        percentage = (count / validation['total_customers']) * 100
        print(f"  {industry}: {count} ({percentage:.1f}%)")
    
    print(f"\n✅ DATA QUALITY CHECKS:")
    print(f"Employee Count Violations: {validation['employee_violations']} ({validation['employee_violation_rate']:.1f}%)")
    print(f"Revenue Range Violations: {validation['revenue_violations']} ({validation['revenue_violation_rate']:.1f}%)")
    
    if validation['employee_violations'] == 0 and validation['revenue_violations'] == 0:
        print("🎉 All business logic validations PASSED!")
    else:
        print("⚠️  Data quality issues detected")

def main():
    print("🚀 Updating DIM_CUSTOMERS to 300 records with 5-year range...")
    
    # Load original data
    print("📖 Loading original Mockaroo data...")
    customers = load_data('MOCK_DATA_ORIGINAL.json')
    print(f"Loaded {len(customers)} customers")
    
    # Apply updates
    print("📅 Expanding signup dates to 5-year range...")
    customers = expand_signup_dates_5_years(customers)
    
    print("👥 Fixing employee counts by segment...")
    customers = fix_employee_count_by_segment(customers)
    
    print("💰 Fixing revenue ranges by segment...")
    customers = fix_revenue_by_segment(customers)
    
    print("🔢 Adding sequential customer IDs...")
    customers = add_sequential_ids(customers)
    
    # Validate
    print("\n✅ Validating updated customer data...")
    validation = validate_customer_data(customers)
    print_validation_summary(validation)
    
    # Save updated data
    output_file = 'DIM_CUSTOMERS.json'
    print(f"\n💾 Saving {len(customers)} customers to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(customers, f, indent=2)
    
    print("🎉 DIM_CUSTOMERS update complete!")
    print(f"✨ Ready for FACT_SUBSCRIPTION_EVENTS generation with {len(customers)} customers")

if __name__ == "__main__":
    main()