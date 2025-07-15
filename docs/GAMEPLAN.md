# GAMEPLAN: Phantom Sec POC - Snowflake Semantic Views with Cortex Analyst

## Executive Summary

This hands-on lab demonstrates how Phantom Sec could leverage Snowflake Semantic Views and Cortex Analyst integration through Snowflake Intelligence to enable natural language queries across compliance automation metrics. The demo uses synthetic data modeling Phantom Sec's business operations to showcase analytics capabilities that would support both operational teams and C-suite executives.

## Business Context & Alignment

### Phantom Sec's Business Model
- **Revenue**: $100M+ ARR (2024), valued at $2.45B
- **Customer Base**: 8,000+ companies across 58 countries
- **Market Segments**: Startups, mid-market, enterprise
- **Core Value**: 526% ROI, 129% productivity boost, 50% faster audit prep

### Target Use Cases Alignment
The POC addresses Phantom Sec's stated goal: *"integrate a cortex analyst/agent that will enable users asking questions like 'What was the ARR in Jan 2025' and then they get a natural language response and also the corresponding sql."*

## Mock Problem Statements

### 1. Executive Dashboard Queries
- "What was our ARR growth by customer segment in Q4 2024?"
- "Which compliance frameworks are driving the highest customer retention?"
- "How does time-to-compliance vary across enterprise vs startup customers?"

### 2. Operational Analytics
- "What's the average ROI our customers achieve by framework type?"
- "Which integrations correlate with fastest compliance achievement?"
- "How many security questionnaires were automated this month?"

### 3. Customer Success Insights
- "Which customer segments have the highest compliance framework adoption rates?"
- "What's the relationship between number of frameworks and customer expansion?"
- "How do audit completion rates vary by industry vertical?"

## Synthetic Data Model Architecture

### Core Business Entities (Simplified for POC)

#### 1. DIM_CUSTOMERS Table (Detailed for Mockaroo)
```sql
customers (
  customer_id,           -- UUID or sequential integer
  company_name,          -- Company names (can use Mockaroo's company name generator)
  segment,               -- Categorical: 'startup', 'mid_market', 'enterprise'
  industry,              -- Categorical: 'saas', 'fintech', 'healthtech', 'ecommerce', 'edtech', 'manufacturing', 'logistics', 'media', 'other'
  signup_date,           -- Date range: 2021-01-01 to 2024-12-31 (4 years of customer history)
  employee_count,        -- Numeric ranges by segment:
                        -- startup: 1-50 employees
                        -- mid_market: 51-500 employees  
                        -- enterprise: 501-10000 employees
  annual_revenue,        -- Numeric ranges by segment (in USD):
                        -- startup: $100K - $5M
                        -- mid_market: $5M - $100M
                        -- enterprise: $100M - $1B
  country,               -- Categorical: 'USA'
  state_province,        -- State codes: CA, NY, TX, FL, WA, IL, PA, OH, GA, NC, etc.
  compliance_maturity,   -- Categorical: 'beginner', 'intermediate', 'advanced'
                        -- Influences how quickly they adopt frameworks
  primary_cloud_provider -- Categorical: 'AWS', 'Azure', 'GCP', 'Multi-cloud', 'On-premise'
                        -- Relevant for integration patterns
)
```

```python
"""
Mockaroo Field Configuration Guide for Customers Table

Field specifications for generating synthetic customer data in Mockaroo.
Each field includes data type, possible values, and distribution weights.

customer_id:
    - Type: Row Number or UUID
    - Sequential starting from 1 or unique identifier

company_name:
    - Type: Company Name
    - Use Mockaroo's built-in company name generator

segment:
    - Type: Custom List
    - All possible values: 'startup', 'mid_market', 'enterprise'
    - Values and weights:
        - 'startup': 50% (100 records)
        - 'mid_market': 37.5% (75 records)
        - 'enterprise': 12.5% (25 records)

industry:
    - Type: Custom List
    - All possible values: 'saas', 'fintech', 'healthtech', 'ecommerce', 'edtech', 'manufacturing', 'logistics', 'media', 'other'
    - Values and weights:
        - 'saas': 30%
        - 'fintech': 20%
        - 'healthtech': 15%
        - 'ecommerce': 10%
        - 'edtech': 8%
        - 'manufacturing': 7%
        - 'logistics': 5%
        - 'media': 3%
        - 'other': 2%

signup_date:
    - Type: Date
    - Range: 2021-01-01 to 2024-12-31
    - Distribution: More recent dates should be weighted higher (growth trend)

employee_count:
    - Type: Number
    - Formula based on segment:
        - If segment == 'startup': random integer between 1-50
        - If segment == 'mid_market': random integer between 51-500
        - If segment == 'enterprise': random integer between 501-10000

annual_revenue:
    - Type: Number
    - Formula based on segment:
        - If segment == 'startup': random between 100000-5000000
        - If segment == 'mid_market': random between 5000000-100000000
        - If segment == 'enterprise': random between 100000000-1000000000

country:
    - Type: Custom List
    - All possible values: 'USA'
    - Values and weights:
        - 'USA': 100%

state_province:
    - Type: State (US)
    - Use Mockaroo's built-in US state generator

compliance_maturity:
    - Type: Custom List
    - All possible values: 'beginner', 'intermediate', 'advanced'
    - Values and weights:
        - 'beginner': 40%
        - 'intermediate': 45%
        - 'advanced': 15%
    - Note: This affects framework adoption speed and automation levels

primary_cloud_provider:
    - Type: Custom List
    - All possible values: 'AWS', 'Azure', 'GCP', 'Multi-cloud', 'On-premise'
    - Values and weights:
        - 'AWS': 45%
        - 'Azure': 25%
        - 'GCP': 15%
        - 'Multi-cloud': 10%
        - 'On-premise': 5%
"""
```

#### 2. FACT_SUBSCRIPTION_EVENTS Table (Detailed for Mockaroo)
```sql
subscription_events (
  event_id,              -- UUID or sequential integer
  customer_id,           -- Foreign key reference to customers table
  event_date,            -- Date range: customer.signup_date to 2024-12-31
  event_type,            -- Categorical: 'new', 'renewal', 'expansion', 'downgrade', 'churn'
  product_tier,          -- Categorical: 'starter', 'professional', 'enterprise', 'enterprise_plus'
  mrr_amount,            -- Numeric: based on segment and product tier
  billing_period,        -- Categorical: 'monthly', 'annual'
  contract_length_months,-- Numeric: 1, 12, 24, 36 (based on billing period and customer segment)
  discount_percentage,   -- Numeric: 0-30% (higher for annual billing and enterprise)
  sales_channel,         -- Categorical: 'self_serve', 'inside_sales', 'field_sales', 'partner'
  payment_method         -- Categorical: 'credit_card', 'ach', 'wire_transfer', 'invoice'
)
```

```python
"""
Mockaroo Field Configuration Guide for Subscription Events Table

Field specifications for generating subscription events that create realistic
customer lifecycle patterns including growth, renewals, and churn scenarios.

event_id:
    - Type: Row Number or UUID
    - Sequential starting from 1 or unique identifier

customer_id:
    - Type: Custom List
    - Values: Reference to generated customer_ids from customers table
    - Distribution: Each customer should have 3-8 events over their lifecycle

event_date:
    - Type: Date
    - Logic: Must be >= customer.signup_date and <= 2024-12-31
    - Pattern: 
        - First event: Within 30 days of signup_date (new subscription)
        - Subsequent events: Spread across customer lifecycle
        - Annual renewals: ~12 months after previous renewal
        - Monthly renewals: Monthly intervals
        - Expansions: Random timing, more likely for successful customers

event_type:
    - Type: Custom List
    - All possible values: 'new', 'renewal', 'expansion', 'downgrade', 'churn'
    - Values and typical sequence weights:
        - 'new': 100% (every customer starts here)
        - 'renewal': 70% (most customers renew)
        - 'expansion': 30% (upsell/cross-sell)
        - 'downgrade': 10% (some customers reduce)
        - 'churn': 15% (customer loss rate)
    - Business rules:
        - First event must always be 'new'
        - 'churn' should be final event for that customer
        - 'renewal' more likely for enterprise, less for startup
        - 'expansion' more likely for mid_market and enterprise

product_tier:
    - Type: Custom List
    - All possible values: 'starter', 'professional', 'enterprise', 'enterprise_plus'
    - Values and weights by segment:
        - Startup customers: 'starter' 70%, 'professional' 30%
        - Mid-market customers: 'professional' 60%, 'enterprise' 40%
        - Enterprise customers: 'enterprise' 70%, 'enterprise_plus' 30%
    - Expansion events typically move up tiers

mrr_amount:
    - Type: Number
    - Calculation based on segment + product_tier:
        - starter: $200-800/month
        - professional: $800-3000/month  
        - enterprise: $3000-15000/month
        - enterprise_plus: $15000-50000/month
    - Event type modifiers:
        - 'new': Base amount
        - 'expansion': 1.2x to 3x previous amount
        - 'renewal': Same or slight increase (1.0x to 1.1x)
        - 'downgrade': 0.5x to 0.8x previous amount

billing_period:
    - Type: Custom List
    - All possible values: 'monthly', 'annual'
    - Values and weights by segment:
        - Startup: 'monthly' 80%, 'annual' 20%
        - Mid-market: 'monthly' 60%, 'annual' 40%
        - Enterprise: 'monthly' 30%, 'annual' 70%
    - Annual billing often correlates with higher contract values

contract_length_months:
    - Type: Number
    - Logic based on billing_period and segment:
        - If billing_period == 'monthly': 1, 3, or 6 months
        - If billing_period == 'annual': 12, 24, or 36 months
        - Enterprise customers more likely to have longer contracts
        - Startup customers typically shorter commitments

discount_percentage:
    - Type: Number
    - Range: 0-30%
    - Logic:
        - Annual billing: 10-20% discount
        - Monthly billing: 0-5% discount
        - Enterprise customers: Higher discounts possible (up to 30%)
        - Multi-year contracts: Additional 5-10% discount
        - New customers: Possible promotional discounts

sales_channel:
    - Type: Custom List
    - All possible values: 'self_serve', 'inside_sales', 'field_sales', 'partner'
    - Values and weights by segment:
        - Startup: 'self_serve' 80%, 'inside_sales' 20%
        - Mid-market: 'self_serve' 30%, 'inside_sales' 60%, 'field_sales' 10%
        - Enterprise: 'inside_sales' 30%, 'field_sales' 65%, 'partner' 5%

payment_method:
    - Type: Custom List
    - All possible values: 'credit_card', 'ach', 'wire_transfer', 'invoice'
    - Values and weights by segment:
        - Startup: 'credit_card' 90%, 'ach' 10%
        - Mid-market: 'credit_card' 60%, 'ach' 30%, 'invoice' 10%
        - Enterprise: 'credit_card' 20%, 'ach' 30%, 'wire_transfer' 20%, 'invoice' 30%

Notes for realistic event generation:
- Generate 5-15 events per customer depending on their tenure
- Maintain chronological order within each customer
- Consider customer lifecycle patterns (new -> renewals -> possible expansion/churn)
- Apply business logic for realistic MRR progression
- Weight expansion events higher for customers with good compliance_maturity

TEMPORAL FLOW REQUIREMENTS for data generation functions:
- First event MUST always be 'new' within 30 days of customer.signup_date
- Renewal events should occur at logical intervals based on billing_period:
  * Monthly: ~28-32 days after previous event
  * Annual: ~360-370 days after previous event
- Expansion events can occur randomly but more likely 6+ months after signup
- Downgrade events typically follow failed renewals or economic stress
- Churn events should be final event for customer, no subsequent events
- Add realistic variance: ±5-15 days for renewals, ±30-60 days for expansions
- Consider business seasonality: more enterprise deals in Q4, fewer in summer
- Events should respect customer lifecycle stage and tenure length
"""
```

#### 3. DIM_COMPLIANCE_FRAMEWORKS Table (Detailed for Mockaroo)
```sql
compliance_frameworks (
  framework_id,           -- Sequential integer 1-8
  framework_name,         -- Categorical: 'SOC2_Type_I', 'SOC2_Type_II', 'ISO27001', 'HIPAA', 'GDPR', 'PCI_DSS', 'FedRAMP', 'NIST_CSF'
  framework_category,     -- Categorical: 'security_audit', 'security_management', 'healthcare_privacy', 'data_privacy', 'payment_security', 'government_cloud', 'cybersecurity_framework'
  complexity_score,       -- Numeric: 1-10 scale of implementation difficulty
  avg_completion_days,    -- Numeric: typical days to achieve compliance
  industry_relevance,     -- Categorical: 'all_industries', 'healthtech', 'ecommerce_fintech', 'government_contractors'
  geographic_scope,       -- Categorical: 'global', 'usa', 'eu_global', 'usa_global'
  automation_percentage,  -- Numeric: 0-100 (% of framework that can be automated)
  annual_audit_required,  -- Boolean: true/false
  certification_cost_usd  -- Numeric: typical cost range for certification
)
```

```python
"""
Mockaroo Field Configuration Guide for Compliance Frameworks Table

Reference data for compliance frameworks that Phantom Sec customers adopt.
This is a small lookup table with 8-10 frameworks total.

framework_id:
    - Type: Row Number
    - Sequential: 1, 2, 3, 4, 5, 6, 7, 8

framework_name:
    - Type: Custom List (static values, no weights needed)
    - Values: 
        - 'SOC2_Type_I'
        - 'SOC2_Type_II' 
        - 'ISO27001'
        - 'HIPAA'
        - 'GDPR'
        - 'PCI_DSS'
        - 'FedRAMP'
        - 'NIST_CSF'

framework_category:
    - Type: Custom List
    - All possible values: 'security_audit', 'security_management', 'healthcare_privacy', 'data_privacy', 'payment_security', 'government_cloud', 'cybersecurity_framework'
    - Values by framework_name:
        - SOC2_Type_I: 'security_audit'
        - SOC2_Type_II: 'security_audit'
        - ISO27001: 'security_management'
        - HIPAA: 'healthcare_privacy'
        - GDPR: 'data_privacy'
        - PCI_DSS: 'payment_security'
        - FedRAMP: 'government_cloud'
        - NIST_CSF: 'cybersecurity_framework'

complexity_score:
    - Type: Number (1-10 scale)
    - Values by framework_name:
        - SOC2_Type_I: 4
        - SOC2_Type_II: 7
        - ISO27001: 8
        - HIPAA: 6
        - GDPR: 7
        - PCI_DSS: 5
        - FedRAMP: 9
        - NIST_CSF: 6

avg_completion_days:
    - Type: Number
    - Values by framework_name:
        - SOC2_Type_I: 90
        - SOC2_Type_II: 180
        - ISO27001: 240
        - HIPAA: 150
        - GDPR: 120
        - PCI_DSS: 90
        - FedRAMP: 365
        - NIST_CSF: 180

industry_relevance:
    - Type: Custom List
    - All possible values: 'all_industries', 'healthtech', 'ecommerce_fintech', 'government_contractors'
    - Values by framework_name:
        - SOC2_Type_I: 'all_industries'
        - SOC2_Type_II: 'all_industries'
        - ISO27001: 'all_industries'
        - HIPAA: 'healthtech'
        - GDPR: 'all_industries'
        - PCI_DSS: 'ecommerce_fintech'
        - FedRAMP: 'government_contractors'
        - NIST_CSF: 'all_industries'

geographic_scope:
    - Type: Custom List
    - All possible values: 'global', 'usa', 'eu_global', 'usa_global'
    - Values by framework_name:
        - SOC2_Type_I: 'global'
        - SOC2_Type_II: 'global'
        - ISO27001: 'global'
        - HIPAA: 'usa'
        - GDPR: 'eu_global'
        - PCI_DSS: 'global'
        - FedRAMP: 'usa'
        - NIST_CSF: 'usa_global'

automation_percentage:
    - Type: Number (0-100)
    - Values by framework_name:
        - SOC2_Type_I: 75
        - SOC2_Type_II: 65
        - ISO27001: 60
        - HIPAA: 70
        - GDPR: 55
        - PCI_DSS: 80
        - FedRAMP: 45
        - NIST_CSF: 70

annual_audit_required:
    - Type: Boolean
    - Values by framework_name:
        - SOC2_Type_I: false
        - SOC2_Type_II: true
        - ISO27001: true
        - HIPAA: false
        - GDPR: false
        - PCI_DSS: true
        - FedRAMP: true
        - NIST_CSF: false

certification_cost_usd:
    - Type: Number
    - Values by framework_name (typical ranges):
        - SOC2_Type_I: 25000
        - SOC2_Type_II: 45000
        - ISO27001: 35000
        - HIPAA: 15000
        - GDPR: 20000
        - PCI_DSS: 30000
        - FedRAMP: 150000
        - NIST_CSF: 25000

Notes:
- This is reference data, so generate exactly 8 rows with the specific values above
- No randomization needed - these are real framework characteristics
- Use conditional logic in Mockaroo to map framework_name to other fields
- This table will be referenced by framework_adoptions and compliance_activities

Framework adoption patterns for USA companies (for framework_adoptions table):
- SOC2_Type_I: 95% of all companies (universal requirement for B2B SaaS)
- SOC2_Type_II: 70% of all companies (more comprehensive audit)
- HIPAA: 95% if healthtech industry, 5% others
- FedRAMP: 80% if government_contractors industry, 2% others
- NIST_CSF: 75% of all companies (widely adopted cybersecurity framework)
- PCI_DSS: 90% if ecommerce/fintech industries, 15% others (any payment processing)
- ISO27001: 40% of all companies (international business)
- GDPR: 35% of all companies (European customers/data)
"""
```

#### 4. FACT_FRAMEWORK_ADOPTIONS Table (Detailed for Mockaroo)
```sql
framework_adoptions (
  adoption_id,           -- UUID or sequential integer
  customer_id,           -- Foreign key reference to customers table
  framework_id,          -- Foreign key reference to compliance_frameworks table
  start_date,            -- Date: customer.signup_date + random days (0-365 after signup)
  completion_date,       -- Date: start_date + framework.avg_completion_days (±30 days variation)
  status,                -- Categorical: 'active', 'completed', 'certified'
  audit_score,           -- Numeric: 1-100 (compliance assessment score)
  hours_saved,           -- Numeric: time saved through automation (varies by framework)
  implementation_cost,   -- Numeric: actual cost spent on implementation
  automation_level       -- Numeric: 0-100 (% of framework automated for this customer)
)
```

```python
"""
Mockaroo Field Configuration Guide for Framework Adoptions Table

Field specifications for generating realistic framework adoption patterns
based on customer industry, segment, and compliance maturity.

adoption_id:
    - Type: Row Number or UUID
    - Sequential starting from 1 or unique identifier

customer_id:
    - Type: Custom List
    - Values: Reference to generated customer_ids from customers table
    - Distribution: Each customer should adopt 2-4 frameworks on average
    - Business logic: Industry-specific adoption patterns (see below)

framework_id:
    - Type: Custom List
    - Values: Reference to framework_ids from compliance_frameworks table (1-8)
    - Distribution based on USA adoption patterns:
        - SOC2_Type_I (id=1): 95% of all companies
        - SOC2_Type_II (id=2): 70% of all companies  
        - ISO27001 (id=3): 40% of all companies
        - HIPAA (id=4): 95% if healthtech, 5% others
        - GDPR (id=5): 35% of all companies
        - PCI_DSS (id=6): 90% if ecommerce/fintech, 15% others
        - FedRAMP (id=7): 80% if government_contractors, 2% others
        - NIST_CSF (id=8): 75% of all companies

start_date:
    - Type: Date
    - Logic: customer.signup_date + random(0, 365) days
    - Pattern: Companies typically start compliance journey within first year

completion_date:
    - Type: Date
    - Logic: start_date + framework.avg_completion_days + random(-30, +30) days
    - Consider customer.compliance_maturity:
        - 'advanced': -20% time reduction
        - 'intermediate': baseline time
        - 'beginner': +30% time increase

status:
    - Type: Custom List
    - All possible values: 'active', 'completed', 'certified'
    - Values and weights:
        - 'completed': 60% (finished implementation)
        - 'certified': 30% (passed audit/certification)
        - 'active': 10% (still in progress)

audit_score:
    - Type: Number (1-100)
    - Logic based on customer.compliance_maturity and framework complexity:
        - 'advanced' customers: 85-98 range
        - 'intermediate' customers: 75-90 range
        - 'beginner' customers: 65-85 range
        - Higher complexity frameworks tend to have lower initial scores

hours_saved:
    - Type: Number
    - Calculation based on framework.automation_percentage and customer.segment:
        - Base hours by framework complexity (100-2000 hours)
        - Multiply by framework.automation_percentage
        - Enterprise customers save more hours (larger scale)
        - Advanced maturity customers save more (better processes)

implementation_cost:
    - Type: Number
    - Range based on customer.segment and framework.certification_cost_usd:
        - Startup: 50-80% of framework.certification_cost_usd
        - Mid-market: 80-120% of framework.certification_cost_usd
        - Enterprise: 100-200% of framework.certification_cost_usd

automation_level:
    - Type: Number (0-100)
    - Base on framework.automation_percentage with customer variation:
        - Advanced maturity: +10-20% above framework baseline
        - Intermediate maturity: ±5% of framework baseline
        - Beginner maturity: -10-15% below framework baseline

USA compliance requirements (for framework adoption logic):
- SOC2_Type_I/II: Nearly universal for B2B SaaS companies
- HIPAA: Mandatory for healthcare, optional for others
- FedRAMP: Required for government contractors, rare otherwise
- NIST_CSF: Widely adopted cybersecurity framework across industries
- PCI_DSS: Required for payment processing (ecommerce/fintech focus)
- ISO27001: Common for companies with international customers
- GDPR: Needed for companies handling European customer data

Industry-specific adoption patterns:
- healthtech: SOC2 (95%), HIPAA (95%), NIST_CSF (85%), ISO27001 (50%)
- fintech: SOC2 (98%), PCI_DSS (95%), NIST_CSF (90%), ISO27001 (60%)
- ecommerce: SOC2 (90%), PCI_DSS (95%), NIST_CSF (70%), GDPR (50%)
- saas: SOC2 (98%), NIST_CSF (80%), ISO27001 (45%), GDPR (40%)
- government_contractors: SOC2 (85%), FedRAMP (80%), NIST_CSF (95%)

Notes for realistic adoption generation:
- Generate 400-600 total adoptions across 200 customers
- Weight adoptions based on industry requirements
- Ensure SOC2 is most common across all industries
- Consider customer maturity affecting implementation success
- Larger customers tend to adopt more frameworks

TEMPORAL FLOW REQUIREMENTS for data generation functions:
- start_date must be >= customer.signup_date (customers can't adopt before signing up)
- Most adoptions start within first 12 months after signup (compliance urgency)
- Advanced maturity customers start compliance earlier (0-6 months after signup)
- Beginner maturity customers delay compliance (6-18 months after signup)
- completion_date = start_date + framework.avg_completion_days ± realistic variance
- Apply customer maturity time adjustments:
  * Advanced: -20% of framework.avg_completion_days
  * Intermediate: baseline framework.avg_completion_days
  * Beginner: +30% of framework.avg_completion_days
- SOC2_Type_I typically comes before SOC2_Type_II (prerequisite relationship)
- Industry-specific frameworks often adopted together (HIPAA + SOC2 for healthtech)
- Add seasonal variance: compliance projects often start in Q1/Q2, complete by Q4
- Enterprise customers have longer implementation cycles but more resources
"""
```

#### 5. FACT_COMPLIANCE_ACTIVITIES Table (Detailed for Mockaroo)
```sql
compliance_activities (
  activity_id,           -- UUID or sequential integer
  customer_id,           -- Foreign key reference to customers table
  framework_id,          -- Foreign key reference to compliance_frameworks table
  adoption_id,           -- Foreign key reference to framework_adoptions table
  activity_date,         -- Date: between adoption.start_date and adoption.completion_date
  activity_type,         -- Categorical: 'control_check', 'questionnaire', 'audit', 'remediation', 'training'
  control_category,      -- Categorical: 'access_control', 'data_protection', 'network_security', 'monitoring', 'incident_response'
  automated_flag,        -- Boolean: true/false (based on framework automation_percentage)
  duration_minutes,      -- Numeric: time spent on activity (varies by type and automation)
  success_flag,          -- Boolean: true/false (activity completed successfully)
  risk_level,            -- Categorical: 'low', 'medium', 'high', 'critical'
  evidence_collected     -- Boolean: true/false (whether evidence was gathered)
)
```

```python
"""
Mockaroo Field Configuration Guide for Compliance Activities Table

Field specifications for generating granular compliance work events
that occur during framework implementation and ongoing monitoring.

activity_id:
    - Type: Row Number or UUID
    - Sequential starting from 1 or unique identifier

customer_id:
    - Type: Custom List
    - Values: Reference to generated customer_ids from customers table
    - Distribution: Each customer should have 50-200 activities depending on frameworks adopted

framework_id:
    - Type: Custom List
    - Values: Reference to framework_ids from compliance_frameworks table (1-8)
    - Distribution: Correlate with customer's framework adoptions

adoption_id:
    - Type: Custom List
    - Values: Reference to adoption_ids from framework_adoptions table
    - Logic: Must match customer_id and framework_id from adoptions

activity_date:
    - Type: Date
    - Logic: Between adoption.start_date and adoption.completion_date + 90 days
    - Pattern: More activities closer to start_date and completion_date

activity_type:
    - Type: Custom List
    - All possible values: 'control_check', 'questionnaire', 'audit', 'remediation', 'training'
    - Values and weights:
        - 'control_check': 50% (regular compliance checks)
        - 'questionnaire': 20% (security questionnaires)
        - 'remediation': 15% (fixing compliance gaps)
        - 'training': 10% (staff compliance training)
        - 'audit': 5% (formal audits)

control_category:
    - Type: Custom List
    - All possible values: 'access_control', 'data_protection', 'network_security', 'monitoring', 'incident_response'
    - Values and weights:
        - 'access_control': 25%
        - 'data_protection': 25%
        - 'network_security': 20%
        - 'monitoring': 20%
        - 'incident_response': 10%

automated_flag:
    - Type: Boolean
    - Logic: Based on framework.automation_percentage and customer.compliance_maturity
        - Use framework baseline automation rate
        - Advanced customers: +15% automation
        - Intermediate customers: baseline
        - Beginner customers: -10% automation

duration_minutes:
    - Type: Number
    - Range by activity_type and automated_flag:
        - control_check: automated=5-30min, manual=30-120min
        - questionnaire: automated=10-45min, manual=60-240min
        - audit: 240-480min (always manual)
        - remediation: automated=30-90min, manual=120-480min
        - training: 60-180min (always manual)

success_flag:
    - Type: Boolean
    - Logic: Based on customer.compliance_maturity and activity complexity
        - Advanced customers: 90-95% success rate
        - Intermediate customers: 85-90% success rate
        - Beginner customers: 75-85% success rate
        - Automated activities have higher success rates (+5-10%)

risk_level:
    - Type: Custom List
    - All possible values: 'low', 'medium', 'high', 'critical'
    - Values and weights:
        - 'low': 40%
        - 'medium': 35%
        - 'high': 20%
        - 'critical': 5%
    - Logic: Failed activities more likely to be high/critical risk

evidence_collected:
    - Type: Boolean
    - Logic: 
        - control_check: 95% true
        - questionnaire: 85% true
        - audit: 100% true
        - remediation: 90% true
        - training: 60% true

Activity patterns by framework type:
- SOC2: Heavy focus on access_control and monitoring activities
- HIPAA: Emphasis on data_protection and access_control
- PCI_DSS: Network_security and data_protection focus
- ISO27001: Balanced across all control categories
- GDPR: Strong data_protection and incident_response focus
- FedRAMP: High monitoring and network_security emphasis
- NIST_CSF: Balanced approach with incident_response focus

Notes for realistic activity generation:
- Generate 8,000-12,000 total activities across all customers
- Weight activity types based on framework requirements
- Cluster activities around key implementation milestones
- Higher automation rates for mature customers and simpler frameworks
- Consider seasonal patterns (more audits in Q4)
- Failed activities should trigger remediation activities

TEMPORAL FLOW REQUIREMENTS for data generation functions:
- activity_date MUST be between adoption.start_date and adoption.completion_date + 90 days
- Activities should follow logical sequence within framework implementation:
  * Week 1-2: Initial training and setup activities
  * Weeks 3-8: Heavy control_check and questionnaire activities
  * Weeks 6-12: Remediation activities for failed checks
  * Final weeks: Audit activities before completion
- Failed activities (success_flag=false) should trigger remediation within 1-7 days
- Evidence collection typically happens throughout implementation, heavier near completion
- Automated activities can occur more frequently (daily/weekly vs monthly for manual)
- Add realistic clustering: 
  * More activities on weekdays vs weekends
  * Avoid major holidays for audit activities
  * Q4 audit rush (October-December)
- Activity intensity should increase as adoption.completion_date approaches
- Post-completion activities (monitoring) continue for 90 days after completion
- Risk level often correlates with timeline pressure (higher risk near deadlines)
"""
```

### Relationship Model
- Customers → Subscription Events (1:M)
- Customers → Framework Adoptions (1:M)
- Compliance Frameworks → Framework Adoptions (1:M)
- Framework Adoptions → Compliance Activities (1:M)
- Customers → Compliance Activities (1:M) [via Framework Adoptions]
- Compliance Frameworks → Compliance Activities (1:M) [via Framework Adoptions]

## Semantic View Design

### Key Dimensions
- **Customer Segment**: startup, mid_market, enterprise
- **Industry Vertical**: saas, fintech, healthtech, ecommerce, edtech, manufacturing, logistics, media, other
- **Framework Type**: SOC2_Type_I, SOC2_Type_II, ISO27001, HIPAA, GDPR, PCI_DSS, FedRAMP, NIST_CSF
- **Framework Category**: security_audit, security_management, healthcare_privacy, data_privacy, payment_security, government_cloud, cybersecurity_framework
- **Time Period**: monthly, quarterly, yearly aggregations
- **Geographic Scope**: USA-focused (with state-level analysis)
- **Compliance Maturity**: beginner, intermediate, advanced
- **Activity Types**: control_check, questionnaire, audit, remediation, training
- **Control Categories**: access_control, data_protection, network_security, monitoring, incident_response

### Key Metrics
- **Revenue Metrics**: total_arr, current_mrr, revenue_growth_rate, customer_ltv
- **Compliance Metrics**: avg_time_to_compliance, automation_percentage, audit_success_rate, frameworks_per_customer
- **Cost & ROI Metrics**: implementation_cost_per_framework, hours_saved_through_automation, cost_per_compliance_activity
- **Operational Metrics**: activity_success_rate, automation_adoption_rate, evidence_collection_rate
- **Risk Metrics**: high_risk_activity_percentage, remediation_response_time, compliance_gap_duration

### Sample Semantic View Structure
```sql
CREATE SEMANTIC VIEW Phantom Sec_analytics
  TABLES (
    customers AS customers PRIMARY KEY (customer_id),
    subscriptions AS subscription_events PRIMARY KEY (event_id),
    frameworks AS compliance_frameworks PRIMARY KEY (framework_id),
    adoptions AS framework_adoptions PRIMARY KEY (adoption_id),
    activities AS compliance_activities PRIMARY KEY (activity_id)
  )
  RELATIONSHIPS (
    subscriptions (customer_id) REFERENCES customers,
    adoptions (customer_id) REFERENCES customers,
    adoptions (framework_id) REFERENCES frameworks,
    activities (customer_id) REFERENCES customers,
    activities (framework_id) REFERENCES frameworks,
    activities (adoption_id) REFERENCES adoptions
  )
  DIMENSIONS (
    -- Customer Dimensions
    customers.segment AS customer_segment,
    customers.industry AS customer_industry,
    customers.compliance_maturity AS customer_maturity,
    customers.primary_cloud_provider AS cloud_provider,
    customers.state_province AS customer_state,
    
    -- Framework Dimensions
    frameworks.framework_name AS framework_name,
    frameworks.framework_category AS framework_category,
    frameworks.industry_relevance AS framework_industry_focus,
    frameworks.geographic_scope AS framework_scope,
    
    -- Subscription Dimensions
    subscriptions.event_type AS subscription_event_type,
    subscriptions.product_tier AS product_tier,
    subscriptions.billing_period AS billing_period,
    subscriptions.sales_channel AS sales_channel,
    
    -- Adoption Dimensions
    adoptions.status AS adoption_status,
    
    -- Activity Dimensions
    activities.activity_type AS activity_type,
    activities.control_category AS control_category,
    activities.risk_level AS risk_level,
    
    -- Time Dimensions
    DATE_PART('year', subscriptions.event_date) AS revenue_year,
    DATE_PART('quarter', subscriptions.event_date) AS revenue_quarter,
    DATE_PART('month', subscriptions.event_date) AS revenue_month,
    DATE_PART('year', adoptions.start_date) AS adoption_year,
    DATE_PART('quarter', adoptions.start_date) AS adoption_quarter
  )
  METRICS (
    -- Revenue Metrics
    customers.total_arr AS 
      SUM(CASE 
        WHEN subscriptions.event_type IN ('new', 'expansion', 'renewal') 
        THEN CASE 
          WHEN subscriptions.billing_period = 'monthly' THEN subscriptions.mrr_amount * 12
          WHEN subscriptions.billing_period = 'annual' THEN subscriptions.mrr_amount
        END
        ELSE 0 
      END),
    customers.current_mrr AS 
      SUM(CASE 
        WHEN subscriptions.billing_period = 'monthly' THEN subscriptions.mrr_amount
        WHEN subscriptions.billing_period = 'annual' THEN subscriptions.mrr_amount / 12
      END),
    subscriptions.avg_contract_value AS
      AVG(subscriptions.mrr_amount * subscriptions.contract_length_months),
    
    -- Compliance Implementation Metrics
    adoptions.avg_time_to_compliance AS 
      AVG(DATEDIFF('day', adoptions.start_date, adoptions.completion_date)),
    adoptions.total_hours_saved AS 
      SUM(adoptions.hours_saved),
    adoptions.avg_implementation_cost AS
      AVG(adoptions.implementation_cost),
    adoptions.avg_automation_level AS
      AVG(adoptions.automation_level),
    
    -- Activity Performance Metrics
    activities.automation_rate AS 
      (SUM(CASE WHEN activities.automated_flag THEN 1 ELSE 0 END) * 100.0 / COUNT(activities.activity_id)),
    activities.success_rate AS
      (SUM(CASE WHEN activities.success_flag THEN 1 ELSE 0 END) * 100.0 / COUNT(activities.activity_id)),
    activities.evidence_collection_rate AS
      (SUM(CASE WHEN activities.evidence_collected THEN 1 ELSE 0 END) * 100.0 / COUNT(activities.activity_id)),
    activities.avg_duration_minutes AS 
      AVG(activities.duration_minutes),
    
    -- Customer Success Metrics
    customers.frameworks_adopted AS 
      COUNT(DISTINCT adoptions.framework_id),
    adoptions.avg_audit_score AS 
      AVG(adoptions.audit_score),
    customers.total_compliance_investment AS
      SUM(adoptions.implementation_cost),
    
    -- Risk & Efficiency Metrics
    activities.high_risk_activity_rate AS
      (SUM(CASE WHEN activities.risk_level IN ('high', 'critical') THEN 1 ELSE 0 END) * 100.0 / COUNT(activities.activity_id)),
    activities.remediation_rate AS
      (SUM(CASE WHEN activities.activity_type = 'remediation' THEN 1 ELSE 0 END) * 100.0 / COUNT(activities.activity_id)),
    frameworks.avg_framework_automation AS
      AVG(frameworks.automation_percentage)
  );
```

## Implementation Strategy

### Phase 1: Data Generation
1. Generate 200 synthetic USA customers across segments:
   - 100 startups (50%)
   - 75 mid-market (37.5%) 
   - 25 enterprise (12.5%)
2. Create 8 compliance framework reference records with realistic characteristics
3. Generate subscription events spanning 24-month history:
   - 800-1,200 total subscription events
   - Maintain temporal flow (signup → new → renewals/expansions)
4. Generate framework adoptions based on industry requirements:
   - 400-600 total adoptions across customers
   - Weight by USA compliance patterns and industry needs
5. Populate granular compliance activities:
   - 8,000-12,000 total activities
   - Respect adoption timelines and implementation phases

### Phase 2: Semantic View Development
1. Create base tables in Snowflake
2. Implement semantic view with business logic
3. Validate metric calculations
4. Test relationship integrity

### Phase 3: Cortex Analyst Integration
1. Configure Cortex Analyst with semantic view
2. Test natural language query patterns
3. Validate SQL generation accuracy
4. Optimize for Snowflake Intelligence interface

### Phase 4: Demo Preparation
1. Prepare realistic business scenarios
2. Create compelling narrative around metrics
3. Demonstrate ROI calculation capabilities
4. Show scalability for enterprise use cases

## Sample Demo Queries

### Natural Language Queries for Cortex Analyst:
1. "What was our total ARR in Q4 2024?"
2. "Which industry vertical has the highest average compliance automation rate?"
3. "How much time did enterprise customers save on SOC 2 compliance implementations in 2024?"
4. "What's the correlation between number of frameworks adopted and customer ARR?"
5. "Which customer segment shows the fastest time-to-compliance for HIPAA?"
6. "What percentage of control checks are automated for fintech customers?"
7. "How does audit success rate vary by customer compliance maturity level?"
8. "Which frameworks require the most remediation activities?"
9. "What's the average implementation cost for SOC 2 Type II by customer segment?"
10. "How many high-risk compliance activities occurred in the last quarter?"

### Expected Business Value Demonstration:
- **Operational Efficiency**: Show how natural language queries eliminate need for custom dashboards
- **Executive Insights**: Demonstrate C-suite level analytics without technical expertise
- **Scalability**: Prove system can handle complex multi-dimensional analysis
- **ROI Validation**: Calculate and display customer success metrics in real-time

## Success Metrics for POC

### Technical Success:
- Semantic view correctly handles all relationship joins
- Cortex Analyst generates accurate SQL for 90%+ of queries
- Query response time under 10 seconds for all scenarios
- Natural language interface intuitive for business users

### Business Success:
- Demonstrates clear value for Phantom Sec's specific use cases
- Shows measurable improvement over manual dashboard creation
- Proves scalability for enterprise-wide deployment
- Validates ROI calculation for Snowflake Intelligence investment

## Next Steps After POC

1. **Production Planning**: Scale data model to handle Phantom Sec's actual volume
2. **Security Implementation**: Ensure compliance with Phantom Sec's security standards
3. **Integration Strategy**: Plan connection with Phantom Sec's existing data infrastructure
4. **Training Program**: Develop user adoption strategy for company-wide rollout
5. **Performance Optimization**: Fine-tune for Phantom Sec's specific query patterns