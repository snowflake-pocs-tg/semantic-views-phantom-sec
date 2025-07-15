-- =====================================================================================
-- PHANTOM SEC FINANCIAL ANALYTICS - Semantic View
-- =====================================================================================
-- Purpose: Financial analytics semantic view for revenue, ARR, MRR, and contract metrics
-- Focus: Revenue growth, customer segments, billing patterns, financial performance
-- Target Questions: "What was ARR in Q4 2024?", "Revenue by segment", "Contract performance"
-- =====================================================================================

CREATE OR REPLACE SEMANTIC VIEW PHANTOM_SEC_FINANCIAL_ANALYTICS
  TABLES (
    -- Customer dimension
    customers AS DIM_CUSTOMERS
      PRIMARY KEY (customer_id)
      WITH SYNONYMS ('clients', 'organizations', 'companies', 'accounts')
      COMMENT = 'Customer organizations using Phantom Sec compliance automation platform',
    
    -- Subscription events fact table
    subscriptions AS FACT_SUBSCRIPTION_EVENTS
      PRIMARY KEY (event_id)
      WITH SYNONYMS ('subscription events', 'revenue events', 'contracts', 'deals', 'agreements')
      COMMENT = 'Customer subscription lifecycle events including new subscriptions, renewals, expansions, and churn'
  )
  
  RELATIONSHIPS (
    -- Define relationships between entities
    subscription_to_customer AS
      subscriptions (customer_id) REFERENCES customers
  )
  
  FACTS (
    -- Revenue and financial metrics
    subscriptions.mrr_amount AS subscriptions.mrr_amount,
    subscriptions.contract_length_months AS subscriptions.contract_length_months,
    subscriptions.discount_percentage AS subscriptions.discount_percentage,
    customers.employee_count AS customers.employee_count,
    customers.annual_revenue AS customers.annual_revenue
  )
  
  DIMENSIONS (
    -- Time dimensions
    subscriptions.event_date AS subscriptions.event_date
      WITH SYNONYMS = ('date', 'subscription date', 'contract date', 'deal date')
      COMMENT = 'Date when the subscription event occurred',
    
    -- Customer dimensions
    customers.segment AS customers.segment
      WITH SYNONYMS = ('customer segment', 'tier', 'category', 'customer size', 'company size')
      COMMENT = 'Customer segment classification: startup, mid_market, enterprise',
    customers.industry AS customers.industry
      WITH SYNONYMS = ('vertical', 'sector', 'business type', 'industry vertical')
      COMMENT = 'Customer industry classification',
    customers.compliance_maturity AS customers.compliance_maturity
      WITH SYNONYMS = ('maturity', 'experience level', 'sophistication', 'readiness')
      COMMENT = 'Customer compliance maturity level: beginner, intermediate, advanced',
    customers.headquarters_state AS customers.headquarters_state
      WITH SYNONYMS = ('state', 'location', 'region', 'geography')
      COMMENT = 'Customer headquarters state location',
    customers.company_name AS customers.company_name
      WITH SYNONYMS = ('customer name', 'organization name', 'client name')
      COMMENT = 'Customer organization name',
    
    -- Subscription dimensions
    subscriptions.event_type AS subscriptions.event_type
      WITH SYNONYMS = ('transaction type', 'subscription type', 'event category')
      COMMENT = 'Type of subscription event: new, renewal, expansion, downgrade, churn',
    subscriptions.product_tier AS subscriptions.product_tier
      WITH SYNONYMS = ('plan', 'subscription tier', 'product plan', 'service tier')
      COMMENT = 'Product tier: starter, professional, enterprise, enterprise_plus',
    subscriptions.billing_period AS subscriptions.billing_period
      WITH SYNONYMS = ('billing frequency', 'payment frequency', 'billing cycle')
      COMMENT = 'Billing period: monthly, quarterly, annual, upfront',
    subscriptions.sales_channel AS subscriptions.sales_channel
      WITH SYNONYMS = ('channel', 'sales method', 'acquisition channel')
      COMMENT = 'Sales channel: self_serve, inside_sales, field_sales, partner',
    subscriptions.payment_method AS subscriptions.payment_method
      WITH SYNONYMS = ('payment type', 'payment option')
      COMMENT = 'Payment method: credit_card, ach, wire_transfer, invoice'
  )
  
  METRICS (
    -- Revenue Metrics
    subscriptions.total_mrr AS SUM(mrr_amount)
      COMMENT = 'Total Monthly Recurring Revenue across all customers',
    subscriptions.arr AS SUM(CASE 
      WHEN billing_period = 'monthly' THEN mrr_amount * 12
      WHEN billing_period = 'quarterly' THEN mrr_amount * 4  
      WHEN billing_period = 'annual' THEN mrr_amount
      WHEN billing_period = 'upfront' THEN mrr_amount
      ELSE mrr_amount * 12 END)
      WITH SYNONYMS = ('annual recurring revenue', 'yearly revenue', 'annual revenue')
      COMMENT = 'Annual Recurring Revenue calculated from MRR based on billing period',
    subscriptions.average_mrr AS AVG(mrr_amount)
      COMMENT = 'Average Monthly Recurring Revenue per subscription event',
    subscriptions.median_mrr AS MEDIAN(mrr_amount)
      COMMENT = 'Median Monthly Recurring Revenue per subscription event',
    
    -- Customer Value Metrics
    subscriptions.average_contract_value AS AVG(mrr_amount * contract_length_months)
      WITH SYNONYMS = ('acv', 'average deal size', 'contract value')
      COMMENT = 'Average total contract value over contract length',
    subscriptions.total_contract_value AS SUM(mrr_amount * contract_length_months)
      WITH SYNONYMS = ('tcv', 'total bookings', 'total contract bookings')
      COMMENT = 'Total contract value across all subscriptions',
    
    -- Growth Metrics
    subscriptions.new_customer_arr AS SUM(CASE WHEN event_type = 'new' THEN 
      CASE 
        WHEN billing_period = 'monthly' THEN mrr_amount * 12
        WHEN billing_period = 'quarterly' THEN mrr_amount * 4
        WHEN billing_period = 'annual' THEN mrr_amount
        WHEN billing_period = 'upfront' THEN mrr_amount
        ELSE mrr_amount * 12 END
      ELSE 0 END)
      COMMENT = 'ARR from new customer acquisitions',
    subscriptions.expansion_arr AS SUM(CASE WHEN event_type = 'expansion' THEN 
      CASE 
        WHEN billing_period = 'monthly' THEN mrr_amount * 12
        WHEN billing_period = 'quarterly' THEN mrr_amount * 4
        WHEN billing_period = 'annual' THEN mrr_amount
        WHEN billing_period = 'upfront' THEN mrr_amount
        ELSE mrr_amount * 12 END
      ELSE 0 END)
      COMMENT = 'ARR from customer expansions and upsells',
    subscriptions.churned_arr AS SUM(CASE WHEN event_type = 'churn' THEN 
      CASE 
        WHEN billing_period = 'monthly' THEN mrr_amount * 12
        WHEN billing_period = 'quarterly' THEN mrr_amount * 4
        WHEN billing_period = 'annual' THEN mrr_amount
        WHEN billing_period = 'upfront' THEN mrr_amount
        ELSE mrr_amount * 12 END
      ELSE 0 END)
      COMMENT = 'ARR lost from customer churn',
    
    -- Customer Counts
    subscriptions.total_customers AS COUNT(DISTINCT customer_id)
      COMMENT = 'Total number of unique customers with subscription events',
    subscriptions.new_customers AS COUNT(DISTINCT CASE WHEN event_type = 'new' THEN customer_id END)
      COMMENT = 'Number of new customers acquired',
    subscriptions.churned_customers AS COUNT(DISTINCT CASE WHEN event_type = 'churn' THEN customer_id END)
      COMMENT = 'Number of customers who churned',
    
    -- Event Distribution Metrics
    subscriptions.total_events AS COUNT(event_id)
      COMMENT = 'Total number of subscription events',
    subscriptions.new_event_rate AS AVG(CASE WHEN event_type = 'new' THEN 1 ELSE 0 END)
      COMMENT = 'Percentage of subscription events that are new customers',
    subscriptions.renewal_event_rate AS AVG(CASE WHEN event_type = 'renewal' THEN 1 ELSE 0 END)
      COMMENT = 'Percentage of subscription events that are renewals',
    subscriptions.expansion_event_rate AS AVG(CASE WHEN event_type = 'expansion' THEN 1 ELSE 0 END)
      COMMENT = 'Percentage of subscription events that are expansions',
    subscriptions.churn_event_rate AS AVG(CASE WHEN event_type = 'churn' THEN 1 ELSE 0 END)
      COMMENT = 'Percentage of subscription events that are churn',
    
    -- Contract and Billing Metrics
    subscriptions.average_contract_length AS AVG(contract_length_months)
      COMMENT = 'Average contract length in months',
    subscriptions.annual_contracts_rate AS AVG(CASE WHEN billing_period = 'annual' THEN 1 ELSE 0 END)
      COMMENT = 'Percentage of contracts with annual billing',
    subscriptions.monthly_contracts_rate AS AVG(CASE WHEN billing_period = 'monthly' THEN 1 ELSE 0 END)
      COMMENT = 'Percentage of contracts with monthly billing',
    subscriptions.quarterly_contracts_rate AS AVG(CASE WHEN billing_period = 'quarterly' THEN 1 ELSE 0 END)
      COMMENT = 'Percentage of contracts with quarterly billing',
    subscriptions.upfront_contracts_rate AS AVG(CASE WHEN billing_period = 'upfront' THEN 1 ELSE 0 END)
      COMMENT = 'Percentage of contracts with upfront billing',
    
    -- Discount and Pricing Metrics
    subscriptions.average_discount AS AVG(discount_percentage)
      COMMENT = 'Average discount percentage across all contracts',
    subscriptions.discounted_contracts_rate AS AVG(CASE WHEN discount_percentage > 0 THEN 1 ELSE 0 END)
      COMMENT = 'Percentage of contracts with discounts applied',
    
    -- Segment Performance Metrics
    customers.enterprise_customer_rate AS AVG(CASE WHEN segment = 'enterprise' THEN 1 ELSE 0 END)
      COMMENT = 'Percentage of enterprise customers',
    customers.mid_market_customer_rate AS AVG(CASE WHEN segment = 'mid_market' THEN 1 ELSE 0 END)
      COMMENT = 'Percentage of mid-market customers',
    customers.startup_customer_rate AS AVG(CASE WHEN segment = 'startup' THEN 1 ELSE 0 END)
      COMMENT = 'Percentage of startup customers',
    
    -- Sales Channel Performance
    subscriptions.self_serve_rate AS AVG(CASE WHEN sales_channel = 'self_serve' THEN 1 ELSE 0 END)
      COMMENT = 'Percentage of subscriptions from self-serve channel',
    subscriptions.field_sales_rate AS AVG(CASE WHEN sales_channel = 'field_sales' THEN 1 ELSE 0 END)
      COMMENT = 'Percentage of subscriptions from field sales channel',
    subscriptions.inside_sales_rate AS AVG(CASE WHEN sales_channel = 'inside_sales' THEN 1 ELSE 0 END)
      COMMENT = 'Percentage of subscriptions from inside sales channel',
    subscriptions.partner_sales_rate AS AVG(CASE WHEN sales_channel = 'partner' THEN 1 ELSE 0 END)
      COMMENT = 'Percentage of subscriptions from partner channel',
    
    -- Product Tier Performance
    subscriptions.enterprise_tier_rate AS AVG(CASE WHEN product_tier = 'enterprise' THEN 1 ELSE 0 END)
      COMMENT = 'Percentage of subscriptions on enterprise tier',
    subscriptions.professional_tier_rate AS AVG(CASE WHEN product_tier = 'professional' THEN 1 ELSE 0 END)
      COMMENT = 'Percentage of subscriptions on professional tier',
    subscriptions.starter_tier_rate AS AVG(CASE WHEN product_tier = 'starter' THEN 1 ELSE 0 END)
      COMMENT = 'Percentage of subscriptions on starter tier'
  )
  
  COMMENT = 'Financial analytics semantic view for Phantom Sec compliance automation platform focusing on revenue, ARR, MRR, contract performance, and customer financial metrics';