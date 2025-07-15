-- =====================================================================================
-- PHANTOM SEC CUSTOMER SUCCESS ANALYTICS - Semantic View (Simplified)
-- =====================================================================================
-- Purpose: Customer success semantic view with only fact-based metrics for POC
-- Focus: Customer counts, financial aggregations, compliance value metrics
-- Target Questions: "Customer portfolio size", "Total revenue", "Framework adoption volume"
-- =====================================================================================

CREATE OR REPLACE SEMANTIC VIEW PHANTOM_SEC_CUSTOMER_SUCCESS_ANALYTICS
  TABLES (
    -- Customer dimension
    customers AS DIM_CUSTOMERS
      PRIMARY KEY (customer_id)
      WITH SYNONYMS ('clients', 'organizations', 'companies', 'accounts', 'customer base')
      COMMENT = 'Customer organizations with comprehensive profile and segmentation data',
    
    -- Compliance frameworks dimension
    frameworks AS DIM_COMPLIANCE_FRAMEWORKS
      PRIMARY KEY (framework_id)
      WITH SYNONYMS ('standards', 'compliance programs', 'regulations', 'security frameworks')
      COMMENT = 'Available compliance frameworks and their characteristics',
    
    -- Subscription events fact table
    subscriptions AS FACT_SUBSCRIPTION_EVENTS
      PRIMARY KEY (event_id)
      WITH SYNONYMS ('revenue events', 'contracts', 'deals', 'subscription transactions')
      COMMENT = 'Customer subscription and revenue events showing financial relationship',
    
    -- Framework adoptions fact table
    adoptions AS FACT_FRAMEWORK_ADOPTIONS
      PRIMARY KEY (adoption_id)
      WITH SYNONYMS ('implementations', 'deployments', 'rollouts', 'certifications')
      COMMENT = 'Framework implementations showing compliance journey progress',
    
    -- Compliance activities fact table
    activities AS FACT_COMPLIANCE_ACTIVITIES
      PRIMARY KEY (activity_id)
      WITH SYNONYMS ('compliance work', 'control activities', 'audit tasks', 'compliance operations')
      COMMENT = 'Detailed compliance work activities showing engagement and automation levels'
  )
  
  RELATIONSHIPS (
    -- Define relationships between entities
    subscription_to_customer AS
      subscriptions (customer_id) REFERENCES customers,
    adoption_to_customer AS
      adoptions (customer_id) REFERENCES customers,
    adoption_to_framework AS
      adoptions (framework_id) REFERENCES frameworks,
    activity_to_customer AS
      activities (customer_id) REFERENCES customers,
    activity_to_framework AS
      activities (framework_id) REFERENCES frameworks,
    activity_to_adoption AS
      activities (adoption_id) REFERENCES adoptions
  )
  
  FACTS (
    -- Financial metrics
    subscriptions.mrr_amount AS subscriptions.mrr_amount,
    subscriptions.contract_length_months AS subscriptions.contract_length_months,
    subscriptions.discount_percentage AS subscriptions.discount_percentage,
    
    -- Compliance value metrics
    adoptions.hours_saved AS adoptions.hours_saved,
    adoptions.implementation_cost AS adoptions.implementation_cost,
    adoptions.automation_level AS adoptions.automation_level,
    adoptions.audit_score AS adoptions.audit_score,
    
    -- Framework characteristics
    frameworks.complexity_score AS frameworks.complexity_score,
    frameworks.avg_completion_days AS frameworks.avg_completion_days,
    frameworks.certification_cost_usd AS frameworks.certification_cost_usd,
    
    -- Activity engagement metrics
    activities.duration_minutes AS activities.duration_minutes,
    
    -- Customer profile metrics
    customers.employee_count AS customers.employee_count,
    customers.annual_revenue AS customers.annual_revenue
  )
  
  DIMENSIONS (
    -- Time dimensions
    customers.signup_date AS customers.signup_date
      WITH SYNONYMS = ('onboarding date', 'customer start date', 'registration date')
      COMMENT = 'Date when customer first signed up for Phantom Sec',
    subscriptions.event_date AS subscriptions.event_date
      WITH SYNONYMS = ('transaction date', 'revenue date', 'contract date')
      COMMENT = 'Date of subscription or revenue event',
    adoptions.start_date AS adoptions.start_date
      WITH SYNONYMS = ('implementation start', 'project kickoff', 'rollout start')
      COMMENT = 'Date when framework implementation began',
    adoptions.completion_date AS adoptions.completion_date
      WITH SYNONYMS = ('go-live date', 'certification date', 'project completion')
      COMMENT = 'Date when framework implementation was completed',
    
    -- Customer profile dimensions
    customers.segment AS customers.segment
      WITH SYNONYMS = ('customer tier', 'size category', 'market segment', 'customer classification')
      COMMENT = 'Customer segment: startup, mid_market, enterprise',
    customers.industry AS customers.industry
      WITH SYNONYMS = ('vertical', 'sector', 'business domain', 'industry classification')
      COMMENT = 'Customer industry vertical',
    customers.compliance_maturity AS customers.compliance_maturity
      WITH SYNONYMS = ('maturity level', 'experience level', 'sophistication', 'compliance readiness')
      COMMENT = 'Customer compliance maturity: beginner, intermediate, advanced',
    customers.company_name AS customers.company_name
      WITH SYNONYMS = ('customer name', 'organization name', 'client name', 'business name')
      COMMENT = 'Customer organization name',
    
    -- Financial relationship dimensions
    subscriptions.event_type AS subscriptions.event_type
      WITH SYNONYMS = ('transaction type', 'revenue type', 'subscription action')
      COMMENT = 'Type of subscription event: new, renewal, expansion, downgrade, churn',
    subscriptions.product_tier AS subscriptions.product_tier
      WITH SYNONYMS = ('plan type', 'service level', 'subscription plan')
      COMMENT = 'Product tier: starter, professional, enterprise, enterprise_plus',
    subscriptions.billing_period AS subscriptions.billing_period
      WITH SYNONYMS = ('payment frequency', 'billing cycle', 'payment schedule')
      COMMENT = 'Billing frequency: monthly, quarterly, annual, upfront',
    
    -- Compliance journey dimensions
    frameworks.framework_name AS frameworks.framework_name
      WITH SYNONYMS = ('standard name', 'framework type', 'compliance standard')
      COMMENT = 'Name of compliance framework: SOC2, ISO27001, HIPAA, etc.',
    adoptions.status AS adoptions.status
      WITH SYNONYMS = ('implementation status', 'project phase', 'completion status')
      COMMENT = 'Framework adoption status: active, completed, certified'
  )
  
  METRICS (
    -- Basic Customer Portfolio Metrics
    customers.total_customers AS COUNT(DISTINCT customer_id)
      WITH SYNONYMS = ('customer count', 'total accounts')
      COMMENT = 'Total number of customers',
    
    -- Simple Financial Metrics
    subscriptions.total_mrr AS SUM(subscriptions.mrr_amount)
      WITH SYNONYMS = ('monthly recurring revenue')
      COMMENT = 'Total Monthly Recurring Revenue',
    subscriptions.average_mrr AS AVG(subscriptions.mrr_amount)
      COMMENT = 'Average Monthly Recurring Revenue per subscription',
    
    -- Basic Success Metrics
    adoptions.total_hours_saved AS SUM(adoptions.hours_saved)
      WITH SYNONYMS = ('time savings')
      COMMENT = 'Total hours saved across all customers',
    adoptions.average_automation_level AS AVG(adoptions.automation_level)
      WITH SYNONYMS = ('automation score')
      COMMENT = 'Average automation level achieved',
    
    -- Simple Engagement Metrics
    activities.total_activities AS COUNT(activity_id)
      WITH SYNONYMS = ('total work')
      COMMENT = 'Total number of compliance activities'
  )
  
  COMMENT = 'Customer success analytics semantic view combining financial and compliance data for holistic customer insights, focusing on portfolio metrics, ROI, and engagement for Phantom Sec platform';