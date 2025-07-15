-- =====================================================================================
-- PHANTOM SEC COMPLIANCE OPERATIONS - Semantic View
-- =====================================================================================
-- Purpose: Compliance operations semantic view for framework adoptions, implementation efficiency, and automation
-- Focus: Framework adoption rates, time-to-compliance, automation effectiveness, risk management
-- Target Questions: "Framework adoption rates", "Time-to-compliance by segment", "Automation effectiveness"
-- =====================================================================================

CREATE OR REPLACE SEMANTIC VIEW PHANTOM_SEC_COMPLIANCE_OPERATIONS
  TABLES (
    -- Customer dimension
    customers AS DIM_CUSTOMERS
      PRIMARY KEY (customer_id)
      WITH SYNONYMS ('clients', 'organizations', 'companies', 'accounts')
      COMMENT = 'Customer organizations implementing compliance frameworks',
    
    -- Compliance frameworks dimension
    frameworks AS DIM_COMPLIANCE_FRAMEWORKS
      PRIMARY KEY (framework_id)
      WITH SYNONYMS ('standards', 'compliance programs', 'regulations', 'security frameworks')
      COMMENT = 'Compliance frameworks and standards available for implementation',
    
    -- Framework adoptions fact table
    adoptions AS FACT_FRAMEWORK_ADOPTIONS
      PRIMARY KEY (adoption_id)
      WITH SYNONYMS ('implementations', 'deployments', 'rollouts', 'certifications', 'adoptions')
      COMMENT = 'Framework adoption implementations showing customer compliance journey',
    
    -- Compliance activities fact table
    activities AS FACT_COMPLIANCE_ACTIVITIES
      PRIMARY KEY (activity_id)
      WITH SYNONYMS ('compliance work', 'control activities', 'audit work', 'compliance tasks')
      COMMENT = 'Granular compliance work activities and control implementations'
  )
  
  RELATIONSHIPS (
    -- Define relationships between entities
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
    -- Framework implementation metrics
    adoptions.hours_saved AS adoptions.hours_saved,
    adoptions.implementation_cost AS adoptions.implementation_cost,
    adoptions.automation_level AS adoptions.automation_level,
    adoptions.audit_score AS adoptions.audit_score,
    frameworks.complexity_score AS frameworks.complexity_score,
    frameworks.avg_completion_days AS frameworks.avg_completion_days,
    frameworks.automation_percentage AS frameworks.automation_percentage,
    frameworks.certification_cost_usd AS frameworks.certification_cost_usd,
    activities.duration_minutes AS activities.duration_minutes,
    customers.employee_count AS customers.employee_count,
    customers.annual_revenue AS customers.annual_revenue
  )
  
  DIMENSIONS (
    -- Time dimensions
    adoptions.start_date AS adoptions.start_date
      WITH SYNONYMS = ('implementation start', 'project start', 'adoption start', 'rollout date')
      COMMENT = 'Date when framework implementation began',
    adoptions.completion_date AS adoptions.completion_date
      WITH SYNONYMS = ('implementation completion', 'go-live date', 'certification date', 'finish date')
      COMMENT = 'Date when framework implementation was completed',
    activities.activity_date AS activities.activity_date
      WITH SYNONYMS = ('work date', 'task date', 'compliance date')
      COMMENT = 'Date when compliance activity was performed',
    
    -- Customer dimensions
    customers.segment AS customers.segment
      WITH SYNONYMS = ('customer segment', 'tier', 'category', 'customer size', 'company size')
      COMMENT = 'Customer segment: startup, mid_market, enterprise',
    customers.industry AS customers.industry
      WITH SYNONYMS = ('vertical', 'sector', 'business type', 'industry vertical')
      COMMENT = 'Customer industry classification',
    customers.compliance_maturity AS customers.compliance_maturity
      WITH SYNONYMS = ('maturity', 'experience level', 'sophistication', 'readiness', 'compliance experience')
      COMMENT = 'Customer compliance maturity: beginner, intermediate, advanced',
    customers.headquarters_state AS customers.headquarters_state
      WITH SYNONYMS = ('state', 'location', 'region', 'geography')
      COMMENT = 'Customer headquarters state location',
    customers.company_name AS customers.company_name
      WITH SYNONYMS = ('customer name', 'organization name', 'client name')
      COMMENT = 'Customer organization name',
    
    -- Framework dimensions
    frameworks.framework_name AS frameworks.framework_name
      WITH SYNONYMS = ('standard name', 'certification name', 'framework type', 'compliance standard')
      COMMENT = 'Name of compliance framework: SOC2, ISO27001, HIPAA, etc.',
    frameworks.framework_category AS frameworks.framework_category
      WITH SYNONYMS = ('framework type', 'standard category', 'compliance category')
      COMMENT = 'Category of compliance framework',
    frameworks.industry_relevance AS frameworks.industry_relevance
      WITH SYNONYMS = ('applicable industries', 'relevant sectors', 'target industries')
      COMMENT = 'Industries where this framework is most relevant',
    frameworks.geographic_scope AS frameworks.geographic_scope
      WITH SYNONYMS = ('geographic coverage', 'regional scope', 'jurisdiction')
      COMMENT = 'Geographic scope of framework applicability',
    frameworks.annual_audit_required AS frameworks.annual_audit_required
      WITH SYNONYMS = ('audit required', 'annual review', 'yearly audit')
      COMMENT = 'Whether framework requires annual audits',
    
    -- Adoption dimensions
    adoptions.status AS adoptions.status
      WITH SYNONYMS = ('implementation status', 'project status', 'adoption state')
      COMMENT = 'Current status of framework adoption: active, completed, certified',
    
    -- Activity dimensions
    activities.activity_type AS activities.activity_type
      WITH SYNONYMS = ('work type', 'task type', 'compliance activity type')
      COMMENT = 'Type of compliance activity: control_check, questionnaire, audit, remediation, training',
    activities.control_category AS activities.control_category
      WITH SYNONYMS = ('control type', 'security domain', 'compliance domain')
      COMMENT = 'Category of security control: access_control, data_protection, network_security, monitoring, incident_response',
    activities.risk_level AS activities.risk_level
      WITH SYNONYMS = ('risk category', 'threat level', 'priority level')
      COMMENT = 'Risk level of compliance activity: low, medium, high, critical',
    activities.automated_flag AS activities.automated_flag
      WITH SYNONYMS = ('automation status', 'automated', 'manual vs automated')
      COMMENT = 'Whether the compliance activity was automated',
    activities.success_flag AS activities.success_flag
      WITH SYNONYMS = ('success status', 'completion status', 'passed')
      COMMENT = 'Whether the compliance activity was successful',
    activities.evidence_collected AS activities.evidence_collected
      WITH SYNONYMS = ('evidence status', 'documentation', 'proof collected')
      COMMENT = 'Whether evidence was collected for the activity'
  )
  
  METRICS (
    -- Basic Framework Adoption Metrics
    adoptions.total_adoptions AS COUNT(adoption_id)
      COMMENT = 'Total number of framework adoptions',
    adoptions.total_customers AS COUNT(DISTINCT customer_id)
      COMMENT = 'Number of customers with framework adoptions',
    
    -- Simple Cost and Value Metrics
    adoptions.total_hours_saved AS SUM(hours_saved)
      WITH SYNONYMS = ('time savings', 'efficiency gains')
      COMMENT = 'Total hours saved across all implementations',
    adoptions.average_hours_saved AS AVG(hours_saved)
      COMMENT = 'Average hours saved per implementation',
    adoptions.total_cost AS SUM(implementation_cost)
      COMMENT = 'Total implementation cost',
    adoptions.average_cost AS AVG(implementation_cost)
      COMMENT = 'Average implementation cost',
    
    -- Simple Automation Metrics
    adoptions.average_automation_level AS AVG(automation_level)
      WITH SYNONYMS = ('automation score')
      COMMENT = 'Average automation level achieved',
    adoptions.average_audit_score AS AVG(audit_score)
      WITH SYNONYMS = ('compliance score')
      COMMENT = 'Average audit score achieved',
    
    -- Basic Activity Metrics
    activities.total_activities AS COUNT(activity_id)
      COMMENT = 'Total compliance activities performed',
    activities.average_duration AS AVG(duration_minutes)
      COMMENT = 'Average activity duration in minutes'
  )
  
  COMMENT = 'Compliance operations semantic view for Phantom Sec focusing on framework adoptions, implementation efficiency, automation levels, and risk management across the compliance automation platform';