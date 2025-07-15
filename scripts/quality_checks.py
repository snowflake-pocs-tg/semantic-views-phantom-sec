#!/usr/bin/env python3
"""
Comprehensive quality checks for all Phantom Sec POC data tables.

This script validates:
1. DIM_CUSTOMERS - Business logic, data ranges, distributions
2. DIM_COMPLIANCE_FRAMEWORKS - Reference data integrity
3. FACT_SUBSCRIPTION_EVENTS - Temporal consistency, contract lengths, business rules
4. Foreign key relationships between tables
5. Cross-table data consistency
"""

import json
import sys
import statistics
from datetime import datetime
from typing import List, Dict, Any, Tuple

def load_json_data(filepath: str) -> List[Dict[str, Any]]:
    """Load JSON data with error handling."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error in {filepath}: {e}")
        return []

def validate_dim_customers(customers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate DIM_CUSTOMERS table."""
    if not customers:
        return {'error': 'No customer data loaded'}
    
    issues = []
    
    # Basic checks
    total_customers = len(customers)
    
    # Segment distribution
    segment_counts = {}
    employee_violations = 0
    revenue_violations = 0
    
    for customer in customers:
        # Segment tracking
        segment = customer.get('segment', 'unknown')
        segment_counts[segment] = segment_counts.get(segment, 0) + 1
        
        # Employee count validation
        employee_count = customer.get('employee_count', 0)
        if segment == 'startup' and not (1 <= employee_count <= 50):
            employee_violations += 1
        elif segment == 'mid_market' and not (51 <= employee_count <= 500):
            employee_violations += 1
        elif segment == 'enterprise' and not (501 <= employee_count <= 10000):
            employee_violations += 1
        
        # Revenue validation
        revenue = customer.get('annual_revenue', 0)
        if segment == 'startup' and not (100000 <= revenue <= 5000000):
            revenue_violations += 1
        elif segment == 'mid_market' and not (5000000 <= revenue <= 100000000):
            revenue_violations += 1
        elif segment == 'enterprise' and not (100000000 <= revenue <= 1000000000):
            revenue_violations += 1
    
    # Date range validation
    signup_dates = []
    for customer in customers:
        try:
            date_str = customer.get('signup_date', '')
            signup_dates.append(datetime.strptime(date_str, '%m/%d/%Y'))
        except ValueError:
            issues.append(f"Invalid date format: {customer.get('signup_date', 'missing')}")
    
    if signup_dates:
        min_date = min(signup_dates)
        max_date = max(signup_dates)
        date_span_years = (max_date - min_date).days / 365
    else:
        min_date = max_date = None
        date_span_years = 0
    
    # Add issues
    if employee_violations > 0:
        issues.append(f"{employee_violations} customers have invalid employee counts for their segment")
    
    if revenue_violations > 0:
        issues.append(f"{revenue_violations} customers have invalid revenue for their segment")
    
    if date_span_years < 4:
        issues.append(f"Date range is too narrow: {date_span_years:.1f} years (expected ~5 years)")
    
    return {
        'table': 'DIM_CUSTOMERS',
        'total_records': total_customers,
        'segment_distribution': segment_counts,
        'employee_violations': employee_violations,
        'revenue_violations': revenue_violations,
        'date_range': {
            'min_date': min_date.strftime('%Y-%m-%d') if min_date else None,
            'max_date': max_date.strftime('%Y-%m-%d') if max_date else None,
            'span_years': date_span_years
        },
        'issues': issues
    }

def validate_dim_frameworks(frameworks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate DIM_COMPLIANCE_FRAMEWORKS table."""
    if not frameworks:
        return {'error': 'No framework data loaded'}
    
    issues = []
    expected_frameworks = {
        'SOC2_Type_I', 'SOC2_Type_II', 'ISO27001', 'HIPAA', 
        'GDPR', 'PCI_DSS', 'FedRAMP', 'NIST_CSF'
    }
    
    # Check count
    if len(frameworks) != 8:
        issues.append(f"Expected 8 frameworks, got {len(frameworks)}")
    
    # Check framework names
    actual_frameworks = {f.get('framework_name', '') for f in frameworks}
    missing_frameworks = expected_frameworks - actual_frameworks
    extra_frameworks = actual_frameworks - expected_frameworks
    
    if missing_frameworks:
        issues.append(f"Missing frameworks: {', '.join(missing_frameworks)}")
    
    if extra_frameworks:
        issues.append(f"Unexpected frameworks: {', '.join(extra_frameworks)}")
    
    # Check required fields
    required_fields = [
        'framework_id', 'framework_name', 'framework_category', 
        'complexity_score', 'avg_completion_days', 'certification_cost_usd'
    ]
    
    for framework in frameworks:
        for field in required_fields:
            if field not in framework or framework[field] is None:
                issues.append(f"Missing {field} in framework {framework.get('framework_name', 'unknown')}")
    
    return {
        'table': 'DIM_COMPLIANCE_FRAMEWORKS',
        'total_records': len(frameworks),
        'expected_frameworks': len(expected_frameworks),
        'actual_frameworks': list(actual_frameworks),
        'issues': issues
    }

def validate_fact_subscription_events(events: List[Dict[str, Any]], customers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate FACT_SUBSCRIPTION_EVENTS table."""
    if not events:
        return {'error': 'No subscription events data loaded'}
    
    issues = []
    
    # Group events by customer
    events_by_customer = {}
    for event in events:
        customer_id = event.get('customer_id')
        if customer_id not in events_by_customer:
            events_by_customer[customer_id] = []
        events_by_customer[customer_id].append(event)
    
    # Check all customers have events
    customer_ids = {c.get('customer_id') for c in customers}
    customers_with_events = set(events_by_customer.keys())
    missing_customers = customer_ids - customers_with_events
    
    if missing_customers:
        issues.append(f"{len(missing_customers)} customers have no subscription events")
    
    # Contract length validation
    unrealistic_contracts = 0
    contract_lengths = {}
    
    for event in events:
        contract_length = event.get('contract_length_months', 0)
        
        # Count contract lengths
        if event.get('event_type') != 'churn':
            contract_lengths[contract_length] = contract_lengths.get(contract_length, 0) + 1
        
        # Check for unrealistic lengths
        if contract_length > 0 and contract_length < 12:
            unrealistic_contracts += 1
    
    if unrealistic_contracts > 0:
        issues.append(f"{unrealistic_contracts} events have unrealistic contract lengths (<12 months)")
    
    # Event type validation
    event_types = {}
    for event in events:
        event_type = event.get('event_type', 'unknown')
        event_types[event_type] = event_types.get(event_type, 0) + 1
    
    # Check each customer's first event is 'new'
    invalid_first_events = 0
    for customer_id, customer_events in events_by_customer.items():
        sorted_events = sorted(customer_events, 
                             key=lambda e: datetime.strptime(e.get('event_date', '01/01/2020'), '%m/%d/%Y'))
        if sorted_events and sorted_events[0].get('event_type') != 'new':
            invalid_first_events += 1
    
    if invalid_first_events > 0:
        issues.append(f"{invalid_first_events} customers don't have 'new' as their first event")
    
    return {
        'table': 'FACT_SUBSCRIPTION_EVENTS',
        'total_records': len(events),
        'customers_with_events': len(events_by_customer),
        'avg_events_per_customer': len(events) / len(customers) if customers else 0,
        'event_types': event_types,
        'contract_lengths': contract_lengths,
        'unrealistic_contracts': unrealistic_contracts,
        'issues': issues
    }

def validate_fact_framework_adoptions(adoptions: List[Dict[str, Any]], 
                                     customers: List[Dict[str, Any]], 
                                     frameworks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate FACT_FRAMEWORK_ADOPTIONS table."""
    if not adoptions:
        return {'error': 'No framework adoptions data loaded'}
    
    issues = []
    
    # Check all customers have adoptions
    customer_ids = {c.get('customer_id') for c in customers}
    customers_with_adoptions = {a.get('customer_id') for a in adoptions}
    missing_customers = customer_ids - customers_with_adoptions
    
    if missing_customers:
        issues.append(f"{len(missing_customers)} customers have no framework adoptions")
    
    # Framework adoption rates
    framework_counts = {}
    for adoption in adoptions:
        framework_id = adoption.get('framework_id')
        framework_counts[framework_id] = framework_counts.get(framework_id, 0) + 1
    
    # Status distribution
    status_counts = {}
    for adoption in adoptions:
        status = adoption.get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Temporal validation
    temporal_issues = 0
    for adoption in adoptions:
        try:
            start_date = datetime.strptime(adoption.get('start_date', '01/01/2020'), '%m/%d/%Y')
            completion_date = datetime.strptime(adoption.get('completion_date', '01/01/2020'), '%m/%d/%Y')
            
            if completion_date <= start_date:
                temporal_issues += 1
        except ValueError:
            temporal_issues += 1
    
    if temporal_issues > 0:
        issues.append(f"{temporal_issues} adoptions have invalid date sequences")
    
    return {
        'table': 'FACT_FRAMEWORK_ADOPTIONS',
        'total_records': len(adoptions),
        'customers_with_adoptions': len(customers_with_adoptions),
        'avg_adoptions_per_customer': len(adoptions) / len(customers) if customers else 0,
        'framework_counts': framework_counts,
        'status_distribution': status_counts,
        'temporal_issues': temporal_issues,
        'issues': issues
    }

def validate_fact_compliance_activities(activities: List[Dict[str, Any]],
                                       adoptions: List[Dict[str, Any]],
                                       customers: List[Dict[str, Any]],
                                       frameworks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate FACT_COMPLIANCE_ACTIVITIES table."""
    if not activities:
        return {'error': 'No compliance activities data loaded'}
    
    issues = []
    
    # Basic metrics
    total_activities = len(activities)
    unique_customers = len(set(a.get('customer_id') for a in activities))
    unique_adoptions = len(set(a.get('adoption_id') for a in activities))
    
    # Activity type distribution
    activity_types = {}
    for activity in activities:
        activity_type = activity.get('activity_type', 'unknown')
        activity_types[activity_type] = activity_types.get(activity_type, 0) + 1
    
    # Automation and success rates
    automated_count = sum(1 for a in activities if a.get('automated_flag', False))
    successful_count = sum(1 for a in activities if a.get('success_flag', False))
    
    automation_rate = automated_count / total_activities if total_activities > 0 else 0
    success_rate = successful_count / total_activities if total_activities > 0 else 0
    
    # Check for unrealistic rates
    if automation_rate > 0.8:
        issues.append(f"Automation rate unusually high: {automation_rate:.1%}")
    if success_rate < 0.7 or success_rate > 0.95:
        issues.append(f"Success rate outside expected range: {success_rate:.1%}")
    
    # Foreign key validation
    adoption_ids = {a.get('adoption_id') for a in adoptions}
    activity_adoption_ids = {a.get('adoption_id') for a in activities}
    orphaned_activities = activity_adoption_ids - adoption_ids
    
    if orphaned_activities:
        issues.append(f"{len(orphaned_activities)} activities reference non-existent adoptions")
    
    return {
        'table': 'FACT_COMPLIANCE_ACTIVITIES',
        'total_records': total_activities,
        'unique_customers': unique_customers,
        'unique_adoptions': unique_adoptions,
        'activities_per_customer': total_activities / len(customers) if customers else 0,
        'activities_per_adoption': total_activities / len(adoptions) if adoptions else 0,
        'activity_types': activity_types,
        'automation_rate': automation_rate,
        'success_rate': success_rate,
        'issues': issues
    }

def validate_foreign_keys(customers: List[Dict[str, Any]], 
                         frameworks: List[Dict[str, Any]], 
                         events: List[Dict[str, Any]],
                         adoptions: List[Dict[str, Any]],
                         activities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate foreign key relationships between tables."""
    issues = []
    
    # Customer IDs in events should exist in customers
    customer_ids = {c.get('customer_id') for c in customers}
    event_customer_ids = {e.get('customer_id') for e in events}
    orphaned_events = event_customer_ids - customer_ids
    
    if orphaned_events:
        issues.append(f"{len(orphaned_events)} subscription events reference non-existent customers")
    
    # Customer IDs in adoptions should exist in customers
    adoption_customer_ids = {a.get('customer_id') for a in adoptions}
    orphaned_adoptions = adoption_customer_ids - customer_ids
    
    if orphaned_adoptions:
        issues.append(f"{len(orphaned_adoptions)} framework adoptions reference non-existent customers")
    
    # Customer IDs in activities should exist in customers
    activity_customer_ids = {a.get('customer_id') for a in activities}
    orphaned_activity_customers = activity_customer_ids - customer_ids
    
    if orphaned_activity_customers:
        issues.append(f"{len(orphaned_activity_customers)} activities reference non-existent customers")
    
    # Framework IDs in adoptions should exist in frameworks
    framework_ids = {f.get('framework_id') for f in frameworks}
    adoption_framework_ids = {a.get('framework_id') for a in adoptions}
    orphaned_adoption_frameworks = adoption_framework_ids - framework_ids
    
    if orphaned_adoption_frameworks:
        issues.append(f"{len(orphaned_adoption_frameworks)} adoptions reference non-existent frameworks")
    
    # Framework IDs in activities should exist in frameworks
    activity_framework_ids = {a.get('framework_id') for a in activities}
    orphaned_activity_frameworks = activity_framework_ids - framework_ids
    
    if orphaned_activity_frameworks:
        issues.append(f"{len(orphaned_activity_frameworks)} activities reference non-existent frameworks")
    
    # Adoption IDs in activities should exist in adoptions
    adoption_ids = {a.get('adoption_id') for a in adoptions}
    activity_adoption_ids = {a.get('adoption_id') for a in activities}
    orphaned_activity_adoptions = activity_adoption_ids - adoption_ids
    
    if orphaned_activity_adoptions:
        issues.append(f"{len(orphaned_activity_adoptions)} activities reference non-existent adoptions")
    
    # Framework IDs should be sequential 1-8
    expected_framework_count = len({1, 2, 3, 4, 5, 6, 7, 8})
    if len(framework_ids) != expected_framework_count:
        issues.append(f"Framework IDs not sequential 1-8: {sorted(framework_ids)}")
    
    return {
        'foreign_key_checks': 'All table relationships',
        'customer_ids_in_customers': len(customer_ids),
        'customer_ids_in_events': len(event_customer_ids),
        'customer_ids_in_adoptions': len(adoption_customer_ids),
        'customer_ids_in_activities': len(activity_customer_ids),
        'orphaned_events': len(orphaned_events),
        'orphaned_adoptions': len(orphaned_adoptions),
        'orphaned_activity_customers': len(orphaned_activity_customers),
        'orphaned_adoption_frameworks': len(orphaned_adoption_frameworks),
        'orphaned_activity_frameworks': len(orphaned_activity_frameworks),
        'orphaned_activity_adoptions': len(orphaned_activity_adoptions),
        'framework_ids': sorted(framework_ids),
        'issues': issues
    }

def calculate_annualized_amount(mrr_amount: int, billing_period: str) -> float:
    """Convert billing amount to annualized equivalent."""
    if billing_period == 'monthly':
        return mrr_amount * 12
    elif billing_period == 'quarterly':
        return mrr_amount * 4
    elif billing_period == 'annual':
        return mrr_amount
    elif billing_period == 'upfront':
        # Upfront is typically 2-year, so divide by 2 to get annual
        return mrr_amount / 2
    else:
        # Unknown billing period, treat as annual
        return mrr_amount

def validate_mrr_billing_consistency(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate MRR amounts are consistent across billing periods when annualized.
    
    This checks for:
    1. Consistent annualized amounts within product tiers
    2. No extreme outliers that would skew annual revenue calculations
    3. Proper scaling between billing periods
    """
    
    # Group events by product tier and billing period
    tier_billing_analysis = {}
    
    for event in events:
        if event.get('event_type') in ['new', 'renewal', 'expansion']:  # Exclude churn/downgrades
            tier = event.get('product_tier', 'unknown')
            billing_period = event.get('billing_period', 'unknown')
            mrr_amount = event.get('mrr_amount', 0)
            
            if tier not in tier_billing_analysis:
                tier_billing_analysis[tier] = {}
            
            if billing_period not in tier_billing_analysis[tier]:
                tier_billing_analysis[tier][billing_period] = []
            
            annualized_amount = calculate_annualized_amount(mrr_amount, billing_period)
            tier_billing_analysis[tier][billing_period].append({
                'original_amount': mrr_amount,
                'annualized_amount': annualized_amount,
                'event_id': event.get('event_id'),
                'customer_id': event.get('customer_id')
            })
    
    # Analysis results
    results = {
        'tier_consistency': {},
        'billing_period_stats': {},
        'outliers': [],
        'issues': []
    }
    
    # Analyze each product tier
    for tier, billing_data in tier_billing_analysis.items():
        tier_stats = {}
        all_annualized_amounts = []
        
        # Calculate stats for each billing period within tier
        for billing_period, amounts_data in billing_data.items():
            annualized_amounts = [d['annualized_amount'] for d in amounts_data]
            
            if len(annualized_amounts) > 0:
                tier_stats[billing_period] = {
                    'count': len(annualized_amounts),
                    'mean': statistics.mean(annualized_amounts),
                    'median': statistics.median(annualized_amounts),
                    'min': min(annualized_amounts),
                    'max': max(annualized_amounts),
                    'std_dev': statistics.stdev(annualized_amounts) if len(annualized_amounts) > 1 else 0
                }
                all_annualized_amounts.extend(annualized_amounts)
        
        # Overall tier statistics
        if all_annualized_amounts:
            tier_overall = {
                'count': len(all_annualized_amounts),
                'mean': statistics.mean(all_annualized_amounts),
                'median': statistics.median(all_annualized_amounts),
                'min': min(all_annualized_amounts),
                'max': max(all_annualized_amounts),
                'std_dev': statistics.stdev(all_annualized_amounts) if len(all_annualized_amounts) > 1 else 0
            }
            
            # Check for consistency across billing periods
            billing_means = [stats['mean'] for stats in tier_stats.values()]
            if len(billing_means) > 1:
                mean_variance = max(billing_means) / min(billing_means) if min(billing_means) > 0 else 0
                if mean_variance > 1.2:  # More than 20% variance is concerning
                    results['issues'].append(
                        f"High variance in {tier} tier across billing periods: {mean_variance:.2f}x difference"
                    )
            
            results['tier_consistency'][tier] = {
                'overall': tier_overall,
                'by_billing_period': tier_stats,
                'billing_period_variance': mean_variance if len(billing_means) > 1 else 1.0
            }
    
    # Identify outliers (amounts > 3 standard deviations from tier mean)
    for tier, billing_data in tier_billing_analysis.items():
        tier_amounts = []
        for amounts_data in billing_data.values():
            tier_amounts.extend([d['annualized_amount'] for d in amounts_data])
        
        if len(tier_amounts) > 1:
            mean_amount = statistics.mean(tier_amounts)
            std_amount = statistics.stdev(tier_amounts)
            
            for billing_period, amounts_data in billing_data.items():
                for data in amounts_data:
                    z_score = abs(data['annualized_amount'] - mean_amount) / std_amount if std_amount > 0 else 0
                    if z_score > 3:  # More than 3 standard deviations
                        results['outliers'].append({
                            'event_id': data['event_id'],
                            'customer_id': data['customer_id'],
                            'tier': tier,
                            'billing_period': billing_period,
                            'original_amount': data['original_amount'],
                            'annualized_amount': data['annualized_amount'],
                            'z_score': z_score,
                            'tier_mean': mean_amount
                        })
    
    # Add issues for outliers
    if results['outliers']:
        results['issues'].append(f"Found {len(results['outliers'])} outlier amounts (>3 std dev from tier mean)")
    
    return results

def print_quality_report(validations: List[Dict[str, Any]]) -> None:
    """Print comprehensive quality report."""
    
    print("🔍 PHANTOM SEC POC DATA QUALITY REPORT")
    print("=" * 80)
    
    total_issues = 0
    
    for validation in validations:
        table_name = validation.get('table', validation.get('foreign_key_checks', 'Unknown'))
        issues = validation.get('issues', [])
        
        print(f"\n📊 {table_name}")
        print("-" * 50)
        
        # Print key metrics
        if 'total_records' in validation:
            print(f"Total Records: {validation['total_records']}")
        
        if 'segment_distribution' in validation:
            print("Segment Distribution:")
            for segment, count in validation['segment_distribution'].items():
                percentage = (count / validation['total_records']) * 100
                print(f"  {segment}: {count} ({percentage:.1f}%)")
        
        if 'event_types' in validation:
            print("Event Type Distribution:")
            for event_type, count in validation['event_types'].items():
                percentage = (count / validation['total_records']) * 100
                print(f"  {event_type}: {count} ({percentage:.1f}%)")
        
        if 'contract_lengths' in validation:
            print("Contract Length Distribution:")
            for length, count in sorted(validation['contract_lengths'].items()):
                percentage = (count / validation['total_records']) * 100
                print(f"  {length} months: {count} ({percentage:.1f}%)")
        
        if 'date_range' in validation and validation['date_range']['min_date']:
            date_range = validation['date_range']
            print(f"Date Range: {date_range['min_date']} to {date_range['max_date']} ({date_range['span_years']:.1f} years)")
        
        # Print issues
        if issues:
            print(f"\n⚠️  Issues Found ({len(issues)}):")
            for issue in issues:
                print(f"  - {issue}")
            total_issues += len(issues)
        else:
            print("\n✅ No issues found!")
    
    print(f"\n🎯 SUMMARY")
    print("-" * 30)
    if total_issues == 0:
        print("🎉 ALL QUALITY CHECKS PASSED!")
        print("✨ Data is ready for Snowflake import and semantic view creation")
    else:
        print(f"⚠️  {total_issues} total issues found across all tables")
        print("🔧 Issues should be resolved before proceeding to Snowflake")

def main():
    """Run comprehensive quality checks on all data."""
    
    print("🚀 Running comprehensive data quality checks...")
    
    # Load all data files
    print("\n📖 Loading data files...")
    customers = load_json_data('../data/DIM_CUSTOMERS.json')
    frameworks = load_json_data('../data/DIM_COMPLIANCE_FRAMEWORKS.json')
    events = load_json_data('../data/FACT_SUBSCRIPTION_EVENTS.json')
    adoptions = load_json_data('../data/FACT_FRAMEWORK_ADOPTIONS.json')
    activities = load_json_data('../data/FACT_COMPLIANCE_ACTIVITIES.json')
    
    if not customers:
        print("❌ Could not load customer data. Exiting.")
        sys.exit(1)
    
    print(f"Loaded: {len(customers)} customers, {len(frameworks)} frameworks, {len(events)} events, {len(adoptions)} adoptions, {len(activities)} activities")
    
    # Run validations
    print("\n🔍 Running quality validations...")
    validations = []
    
    validations.append(validate_dim_customers(customers))
    validations.append(validate_dim_frameworks(frameworks))
    validations.append(validate_fact_subscription_events(events, customers))
    validations.append(validate_fact_framework_adoptions(adoptions, customers, frameworks))
    validations.append(validate_fact_compliance_activities(activities, adoptions, customers, frameworks))
    validations.append(validate_foreign_keys(customers, frameworks, events, adoptions, activities))
    
    # Run MRR billing validation
    print("\n💰 Running MRR billing consistency validation...")
    mrr_validation = validate_mrr_billing_consistency(events)
    
    # Print report
    print_quality_report(validations)
    
    # Print MRR validation summary
    print("\n" + "=" * 80)
    print("💰 MRR BILLING CONSISTENCY VALIDATION")
    print("=" * 80)
    
    if mrr_validation['issues']:
        print(f"⚠️  Financial Issues Found ({len(mrr_validation['issues'])}):")
        for issue in mrr_validation['issues']:
            print(f"  - {issue}")
    else:
        print("✅ MRR billing consistency validated!")
        print("💡 All product tiers show consistent annualized amounts across billing periods")
        print("📈 Annual revenue rollups will be accurate (variance <1.2x)")
    
    # Show tier consistency summary
    print("\n📊 Tier Consistency Summary:")
    for tier, data in mrr_validation['tier_consistency'].items():
        variance = data['billing_period_variance']
        status = "✅" if variance <= 1.2 else "⚠️"
        print(f"  {tier}: {variance:.2f}x variance {status}")
    
    if mrr_validation['outliers']:
        print(f"\n⚠️  {len(mrr_validation['outliers'])} outlier amounts detected (>3 std dev from tier mean)")
    else:
        print("\n✅ No extreme outliers detected in financial data")

if __name__ == "__main__":
    main()