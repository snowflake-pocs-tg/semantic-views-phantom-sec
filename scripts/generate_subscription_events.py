#!/usr/bin/env python3
"""
Generate FACT_SUBSCRIPTION_EVENTS data with realistic contract lengths.

Updates:
1. Fix contract lengths to be realistic for B2B SaaS compliance tools
2. Use 300 customers from DIM_CUSTOMERS_300.json
3. Add comprehensive quality validation
4. Maintain proper temporal flow and business logic
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

def load_customers() -> List[Dict[str, Any]]:
    """Load customer data from DIM_CUSTOMERS_300."""
    with open('../data/DIM_CUSTOMERS.json', 'r') as f:
        return json.load(f)

def parse_date(date_str: str) -> datetime:
    """Parse date from MM/DD/YYYY format."""
    return datetime.strptime(date_str, '%m/%d/%Y')

def format_date(date: datetime) -> str:
    """Format date to MM/DD/YYYY."""
    return date.strftime('%m/%d/%Y')

def get_product_tier_for_segment(segment: str, is_new: bool = True) -> str:
    """Determine product tier based on customer segment."""
    if segment == 'startup':
        return 'starter' if is_new or random.random() < 0.7 else 'professional'
    elif segment == 'mid_market':
        if is_new:
            return 'professional' if random.random() < 0.8 else 'enterprise'
        else:
            return random.choices(['professional', 'enterprise'], weights=[0.6, 0.4])[0]
    else:  # enterprise
        if is_new:
            return 'enterprise' if random.random() < 0.8 else 'enterprise_plus'
        else:
            return random.choices(['enterprise', 'enterprise_plus'], weights=[0.7, 0.3])[0]

def get_mrr_for_tier(tier: str, billing_period: str) -> int:
    """Calculate amount based on product tier and billing period."""
    base_monthly_amounts = {
        'starter': random.randint(200, 800),
        'professional': random.randint(800, 3000),
        'enterprise': random.randint(3000, 15000),
        'enterprise_plus': random.randint(15000, 50000)
    }
    
    monthly_amount = base_monthly_amounts[tier]
    
    # Convert to billing period amount
    if billing_period == 'monthly':
        return monthly_amount
    elif billing_period == 'quarterly':
        return monthly_amount * 3
    elif billing_period == 'annual':
        return monthly_amount * 12
    elif billing_period == 'upfront':
        # Multi-year upfront (assume 2-year average)
        return monthly_amount * 24
    
    return monthly_amount

def get_billing_period_for_segment(segment: str) -> str:
    """Determine billing period preference by segment for B2B SaaS compliance tools."""
    if segment == 'startup':
        # Startups prefer monthly for cash flow, some quarterly
        return random.choices(['monthly', 'quarterly', 'annual'], weights=[0.6, 0.3, 0.1])[0]
    elif segment == 'mid_market':
        # Mid-market mix of quarterly and annual
        return random.choices(['monthly', 'quarterly', 'annual'], weights=[0.2, 0.5, 0.3])[0]
    else:  # enterprise
        # Enterprise prefers annual/upfront for budget predictability
        return random.choices(['quarterly', 'annual', 'upfront'], weights=[0.2, 0.6, 0.2])[0]

def get_realistic_contract_length(segment: str) -> int:
    """
    Determine realistic contract length in months for B2B SaaS compliance tools.
    
    Reality: Compliance is long-term, not 1-6 month commitments.
    """
    if segment == 'startup':
        # Startups: Mostly 12-month, some 24-month
        return random.choices([12, 24], weights=[0.8, 0.2])[0]
    elif segment == 'mid_market':
        # Mid-market: Mix of 12 and 24-month contracts
        return random.choices([12, 24], weights=[0.6, 0.4])[0]
    else:  # enterprise
        # Enterprise: Prefer longer contracts for stability
        return random.choices([12, 24, 36], weights=[0.3, 0.5, 0.2])[0]

def get_sales_channel(segment: str, product_tier: str) -> str:
    """Determine sales channel based on segment."""
    if segment == 'startup':
        return random.choices(['self_serve', 'inside_sales'], weights=[0.8, 0.2])[0]
    elif segment == 'mid_market':
        return random.choices(['self_serve', 'inside_sales', 'field_sales'], 
                            weights=[0.3, 0.6, 0.1])[0]
    else:  # enterprise
        return random.choices(['inside_sales', 'field_sales', 'partner'], 
                            weights=[0.3, 0.65, 0.05])[0]

def get_payment_method(segment: str) -> str:
    """Determine payment method based on segment."""
    if segment == 'startup':
        return random.choices(['credit_card', 'ach'], weights=[0.9, 0.1])[0]
    elif segment == 'mid_market':
        return random.choices(['credit_card', 'ach', 'invoice'], 
                            weights=[0.6, 0.3, 0.1])[0]
    else:  # enterprise
        return random.choices(['credit_card', 'ach', 'wire_transfer', 'invoice'], 
                            weights=[0.2, 0.3, 0.2, 0.3])[0]

def calculate_discount(billing_period: str, contract_length: int, segment: str, 
                      event_type: str) -> float:
    """Calculate realistic discount percentage for B2B SaaS compliance tools (≤5%)."""
    discount = 0.0
    
    # Annual/upfront payment discount (2-5%)
    if billing_period in ['annual', 'upfront']:
        discount += random.uniform(2.0, 5.0)
    elif billing_period == 'quarterly':
        discount += random.uniform(1.0, 2.0)  # Small quarterly discount
    
    # Multi-year contract discount (1-3%)
    if contract_length >= 24:
        discount += random.uniform(1.0, 3.0)
    
    # New customer promotional discount (rare, 1-2%)
    if event_type == 'new' and random.random() < 0.15:  # Only 15% get promo
        discount += random.uniform(1.0, 2.0)
    
    # Enterprise volume discount (small, 1-2%)
    if segment == 'enterprise' and random.random() < 0.3:
        discount += random.uniform(1.0, 2.0)
    
    return min(discount, 5.0)  # Cap at 5% - realistic for B2B SaaS

def generate_subscription_lifecycle(customer: Dict[str, Any], 
                                  event_id_counter: int) -> Tuple[List[Dict[str, Any]], int]:
    """Generate all subscription events for a single customer."""
    events = []
    
    signup_date = parse_date(customer['signup_date'])
    current_date = datetime.now()
    segment = customer['segment']
    
    # Determine if customer will churn
    will_churn = random.random() < 0.15  # 15% churn rate
    
    # First event: NEW subscription
    new_event_date = signup_date + timedelta(days=random.randint(0, 30))
    billing_period = get_billing_period_for_segment(segment)
    product_tier = get_product_tier_for_segment(segment, is_new=True)
    contract_length = get_realistic_contract_length(segment)
    
    current_event = {
        'event_id': event_id_counter,
        'customer_id': customer['customer_id'],
        'event_date': format_date(new_event_date),
        'event_type': 'new',
        'product_tier': product_tier,
        'mrr_amount': get_mrr_for_tier(product_tier, billing_period),
        'billing_period': billing_period,
        'contract_length_months': contract_length,
        'discount_percentage': calculate_discount(billing_period, contract_length, segment, 'new'),
        'sales_channel': get_sales_channel(segment, product_tier),
        'payment_method': get_payment_method(segment)
    }
    events.append(current_event)
    event_id_counter += 1
    
    # Track current state
    last_event_date = new_event_date
    current_mrr = current_event['mrr_amount']
    current_tier = product_tier
    current_billing = billing_period
    current_contract_length = contract_length
    
    # Generate renewal/expansion/churn events based on contract cycles
    while last_event_date < current_date:
        # Determine next event timing based on contract length (not billing period)
        # Renewals happen at contract end, not monthly
        if current_billing == 'monthly':
            # Monthly billing but annual contracts = monthly charges until contract renewal
            days_to_next = current_contract_length * 30  # Contract renewal cycle
        else:
            # Annual billing aligns with contract renewal
            days_to_next = current_contract_length * 30
        
        next_event_date = last_event_date + timedelta(days=days_to_next)
        
        # Stop if we've reached present day
        if next_event_date > current_date:
            break
        
        # Check for churn
        if will_churn and (next_event_date - signup_date).days > 365:  # Only after 1 year
            if random.random() < 0.2:  # 20% chance to churn at contract renewal
                churn_event = {
                    'event_id': event_id_counter,
                    'customer_id': customer['customer_id'],
                    'event_date': format_date(next_event_date),
                    'event_type': 'churn',
                    'product_tier': current_tier,
                    'mrr_amount': 0,
                    'billing_period': current_billing,
                    'contract_length_months': 0,
                    'discount_percentage': 0,
                    'sales_channel': current_event['sales_channel'],
                    'payment_method': current_event['payment_method']
                }
                events.append(churn_event)
                event_id_counter += 1
                break  # No more events after churn
        
        # Determine event type at contract renewal
        event_type_weights = {
            'renewal': 0.7,
            'expansion': 0.25,
            'downgrade': 0.05
        }
        
        # Higher expansion rate for growing companies
        if segment in ['mid_market', 'enterprise'] and \
           customer['compliance_maturity'] == 'advanced':
            event_type_weights['expansion'] = 0.35
            event_type_weights['renewal'] = 0.6
            event_type_weights['downgrade'] = 0.05
        
        event_type = random.choices(
            list(event_type_weights.keys()),
            list(event_type_weights.values())
        )[0]
        
        # Calculate new contract terms
        new_contract_length = get_realistic_contract_length(segment)
        
        # Calculate new MRR based on event type
        if event_type == 'expansion':
            new_tier = get_product_tier_for_segment(segment, is_new=False)
            # Ensure tier upgrade
            tier_hierarchy = ['starter', 'professional', 'enterprise', 'enterprise_plus']
            if tier_hierarchy.index(new_tier) <= tier_hierarchy.index(current_tier):
                new_tier = tier_hierarchy[min(tier_hierarchy.index(current_tier) + 1, 3)]
            new_mrr = get_mrr_for_tier(new_tier, current_billing)
            current_tier = new_tier
        elif event_type == 'downgrade':
            new_mrr = int(current_mrr * random.uniform(0.6, 0.8))
        else:  # renewal
            new_mrr = int(current_mrr * random.uniform(1.0, 1.1))  # 0-10% price increase
        
        # Create event
        event = {
            'event_id': event_id_counter,
            'customer_id': customer['customer_id'],
            'event_date': format_date(next_event_date),
            'event_type': event_type,
            'product_tier': current_tier,
            'mrr_amount': new_mrr,
            'billing_period': current_billing,
            'contract_length_months': new_contract_length,
            'discount_percentage': calculate_discount(current_billing, new_contract_length,
                                                    segment, event_type),
            'sales_channel': current_event['sales_channel'],
            'payment_method': current_event['payment_method']
        }
        
        events.append(event)
        event_id_counter += 1
        
        # Update state
        last_event_date = next_event_date
        current_mrr = new_mrr
        current_contract_length = new_contract_length
        current_event = event
    
    return events, event_id_counter

def validate_subscription_data_comprehensive(events: List[Dict[str, Any]], 
                                           customers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Comprehensive validation including contract length analysis."""
    
    # Group events by customer
    events_by_customer = {}
    for event in events:
        customer_id = event['customer_id']
        if customer_id not in events_by_customer:
            events_by_customer[customer_id] = []
        events_by_customer[customer_id].append(event)
    
    # Validation checks
    issues = []
    
    # Check each customer has events
    customer_ids = {c['customer_id'] for c in customers}
    customers_with_events = set(events_by_customer.keys())
    missing_customers = customer_ids - customers_with_events
    
    if missing_customers:
        issues.append(f"{len(missing_customers)} customers have no events")
    
    # Check temporal order and first event is 'new'
    for customer_id, customer_events in events_by_customer.items():
        # Sort by date
        sorted_events = sorted(customer_events, 
                             key=lambda e: parse_date(e['event_date']))
        
        # Check first event is 'new'
        if sorted_events[0]['event_type'] != 'new':
            issues.append(f"Customer {customer_id} first event is not 'new'")
        
        # Check no events after churn
        churn_index = None
        for i, event in enumerate(sorted_events):
            if event['event_type'] == 'churn':
                churn_index = i
                break
        
        if churn_index is not None and churn_index < len(sorted_events) - 1:
            issues.append(f"Customer {customer_id} has events after churn")
    
    # Contract length analysis
    contract_lengths = {}
    for event in events:
        if event['event_type'] != 'churn':  # Exclude churn events
            length = event['contract_length_months']
            contract_lengths[length] = contract_lengths.get(length, 0) + 1
    
    # Check for unrealistic contract lengths
    unrealistic_contracts = 0
    for event in events:
        if event['event_type'] != 'churn':
            length = event['contract_length_months']
            if length < 12:  # Less than 12 months is unrealistic for compliance tools
                unrealistic_contracts += 1
    
    if unrealistic_contracts > 0:
        issues.append(f"{unrealistic_contracts} events have unrealistic contract lengths (<12 months)")
    
    # Calculate summary statistics
    event_types = {}
    billing_periods = {}
    product_tiers = {}
    total_mrr = 0
    
    for event in events:
        event_types[event['event_type']] = event_types.get(event['event_type'], 0) + 1
        billing_periods[event['billing_period']] = billing_periods.get(event['billing_period'], 0) + 1
        product_tiers[event['product_tier']] = product_tiers.get(event['product_tier'], 0) + 1
        
        if event['event_type'] in ['new', 'renewal', 'expansion']:
            total_mrr += event['mrr_amount']
    
    return {
        'total_events': len(events),
        'customers_with_events': len(events_by_customer),
        'avg_events_per_customer': len(events) / len(customers),
        'event_types': event_types,
        'billing_periods': billing_periods,
        'product_tiers': product_tiers,
        'contract_lengths': contract_lengths,
        'unrealistic_contracts': unrealistic_contracts,
        'total_mrr': total_mrr,
        'issues': issues
    }

def main():
    print("🚀 Generating FACT_SUBSCRIPTION_EVENTS with realistic contract lengths...")
    
    # Load customers
    print("📖 Loading customer data...")
    customers = load_customers()
    print(f"Loaded {len(customers)} customers")
    
    # Generate events
    print("🔄 Generating subscription lifecycle events...")
    all_events = []
    event_id_counter = 1
    
    for i, customer in enumerate(customers):
        events, event_id_counter = generate_subscription_lifecycle(customer, event_id_counter)
        all_events.extend(events)
        
        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1}/{len(customers)} customers...")
    
    print(f"Generated {len(all_events)} total events")
    
    # Validate
    print("\n✅ Validating subscription data...")
    validation = validate_subscription_data_comprehensive(all_events, customers)
    
    print(f"\n📊 SUBSCRIPTION EVENTS SUMMARY:")
    print(f"Total Events: {validation['total_events']}")
    print(f"Customers with Events: {validation['customers_with_events']}/{len(customers)}")
    print(f"Avg Events per Customer: {validation['avg_events_per_customer']:.1f}")
    
    print(f"\nEvent Type Distribution:")
    for event_type, count in validation['event_types'].items():
        percentage = (count / validation['total_events']) * 100
        print(f"  {event_type}: {count} ({percentage:.1f}%)")
    
    print(f"\nBilling Period Distribution:")
    for period, count in validation['billing_periods'].items():
        percentage = (count / validation['total_events']) * 100
        print(f"  {period}: {count} ({percentage:.1f}%)")
    
    print(f"\nContract Length Distribution:")
    for length, count in sorted(validation['contract_lengths'].items()):
        percentage = (count / validation['total_events']) * 100
        print(f"  {length} months: {count} ({percentage:.1f}%)")
    
    print(f"\nProduct Tier Distribution:")
    for tier, count in sorted(validation['product_tiers'].items()):
        percentage = (count / validation['total_events']) * 100
        print(f"  {tier}: {count} ({percentage:.1f}%)")
    
    if validation['issues']:
        print(f"\n⚠️  Issues Found:")
        for issue in validation['issues'][:5]:
            print(f"  - {issue}")
        if len(validation['issues']) > 5:
            print(f"  ... and {len(validation['issues']) - 5} more")
    else:
        print(f"\n✨ No data quality issues found!")
    
    # Save data
    output_file = '../data/FACT_SUBSCRIPTION_EVENTS.json'
    print(f"\n💾 Saving {len(all_events)} events to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(all_events, f, indent=2)
    
    print("🎉 FACT_SUBSCRIPTION_EVENTS generation complete!")
    print("📋 Contract lengths are now realistic for B2B SaaS compliance tools!")

if __name__ == "__main__":
    main()