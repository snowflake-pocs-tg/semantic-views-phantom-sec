-- =====================================================================================
-- PHANTOM SEC Compliance Analytics POC - Snowflake Setup Script
-- =====================================================================================
-- This script creates the Bronze layer tables and sets up data loading infrastructure
-- for the Phantom Sec Analytics POC demonstrating Snowflake AI functions with compliance data.
--
-- Execute sections in order:
-- 1. Database and Schema Creation
-- 2. Bronze Layer Table Creation  
-- 3. File Format and Stage Setup
-- 4. Data Loading Commands
-- 5. Validation Queries
-- =====================================================================================

-- =====================================================================================
-- 1. CREATE DATABASE, WAREHOUSE, AND SCHEMA
-- =====================================================================================

-- Create database for the POC
CREATE DATABASE IF NOT EXISTS PHANTOM_SEC_POC;
USE DATABASE PHANTOM_SEC_POC;

-- Create warehouse for POC workloads
CREATE WAREHOUSE IF NOT EXISTS PHANTOM_SEC_WH
    WITH 
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    MIN_CLUSTER_COUNT = 1
    MAX_CLUSTER_COUNT = 1
    SCALING_POLICY = 'STANDARD'
    COMMENT = 'Warehouse for Phantom Sec POC analytics and Cortex Analyst queries';

-- Set warehouse context
USE WAREHOUSE PHANTOM_SEC_WH;

-- Create schema for Bronze layer
CREATE SCHEMA IF NOT EXISTS BRONZE;
USE SCHEMA BRONZE;

-- =====================================================================================
-- 2. CREATE BRONZE LAYER TABLES
-- =====================================================================================

-- DIM_CUSTOMERS table (300 records)
-- Core customer data representing Phantom Sec's market distribution
CREATE OR REPLACE TABLE DIM_CUSTOMERS (
    customer_id INTEGER PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    industry VARCHAR(50) NOT NULL,
    segment VARCHAR(20) NOT NULL,
    employee_count INTEGER NOT NULL,
    annual_revenue INTEGER NOT NULL,
    headquarters_state VARCHAR(2) NOT NULL,
    signup_date DATE NOT NULL,
    compliance_maturity VARCHAR(15) NOT NULL
);

-- DIM_COMPLIANCE_FRAMEWORKS table (8 records)  
-- Compliance framework reference data
CREATE OR REPLACE TABLE DIM_COMPLIANCE_FRAMEWORKS (
    framework_id INTEGER PRIMARY KEY,
    framework_name VARCHAR(50) NOT NULL,
    framework_category VARCHAR(30) NOT NULL,
    complexity_score INTEGER NOT NULL,
    avg_completion_days INTEGER NOT NULL,
    industry_relevance VARCHAR(50) NOT NULL,
    geographic_scope VARCHAR(20) NOT NULL,
    automation_percentage INTEGER NOT NULL,
    annual_audit_required BOOLEAN NOT NULL,
    certification_cost_usd INTEGER NOT NULL
);

-- FACT_SUBSCRIPTION_EVENTS table (786 records)
-- Customer subscription lifecycle events
CREATE OR REPLACE TABLE FACT_SUBSCRIPTION_EVENTS (
    event_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    event_date DATE NOT NULL,
    event_type VARCHAR(15) NOT NULL,
    product_tier VARCHAR(20) NOT NULL,
    mrr_amount INTEGER NOT NULL,
    billing_period VARCHAR(15) NOT NULL,
    contract_length_months INTEGER NOT NULL,
    discount_percentage DECIMAL(5,2) NOT NULL,
    sales_channel VARCHAR(20) NOT NULL,
    payment_method VARCHAR(20) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES DIM_CUSTOMERS(customer_id)
);

-- FACT_FRAMEWORK_ADOPTIONS table (1,099 records)
-- Framework adoption implementations
CREATE OR REPLACE TABLE FACT_FRAMEWORK_ADOPTIONS (
    adoption_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    framework_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    completion_date DATE NOT NULL,
    status VARCHAR(15) NOT NULL,
    audit_score INTEGER,
    hours_saved INTEGER NOT NULL,
    implementation_cost INTEGER NOT NULL,
    automation_level INTEGER NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES DIM_CUSTOMERS(customer_id),
    FOREIGN KEY (framework_id) REFERENCES DIM_COMPLIANCE_FRAMEWORKS(framework_id)
);

-- FACT_COMPLIANCE_ACTIVITIES table (103,916 records)
-- Granular compliance work activities
CREATE OR REPLACE TABLE FACT_COMPLIANCE_ACTIVITIES (
    activity_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    framework_id INTEGER NOT NULL,
    adoption_id INTEGER NOT NULL,
    activity_date DATE NOT NULL,
    activity_type VARCHAR(20) NOT NULL,
    control_category VARCHAR(25) NOT NULL,
    automated_flag BOOLEAN NOT NULL,
    duration_minutes INTEGER NOT NULL,
    success_flag BOOLEAN NOT NULL,
    risk_level VARCHAR(10) NOT NULL,
    evidence_collected BOOLEAN NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES DIM_CUSTOMERS(customer_id),
    FOREIGN KEY (framework_id) REFERENCES DIM_COMPLIANCE_FRAMEWORKS(framework_id),
    FOREIGN KEY (adoption_id) REFERENCES FACT_FRAMEWORK_ADOPTIONS(adoption_id)
);

-- =====================================================================================
-- 3. CREATE FILE FORMAT AND STAGE
-- =====================================================================================
-- NOTE: This section is for users running the script in IDE environments like VSCode or Cursor.
-- Users working with POC from Snowflake Notebook will follow a different workflow 
-- and this setup will be configured separately for that environment.

-- Create file format for JSON files
CREATE OR REPLACE FILE FORMAT JSON_FORMAT 
TYPE = 'JSON' 
COMPRESSION = 'AUTO' 
STRIP_OUTER_ARRAY = TRUE;

-- Create internal stage for data loading
CREATE OR REPLACE STAGE PHANTOM_SEC_DATA_STAGE;

-- =====================================================================================
-- 4. DATA LOADING COMMANDS
-- =====================================================================================
-- Execute these commands after uploading JSON files to your local system
-- Replace /Users/tgordonjr/Desktop/Phantom Sec-poc/data/ with actual file paths

-- Load DIM_CUSTOMERS (load first due to foreign key dependencies)
PUT file://data/DIM_CUSTOMERS.json @PHANTOM_SEC_DATA_STAGE;

COPY INTO DIM_CUSTOMERS
FROM (
  SELECT 
    $1:customer_id::INTEGER,
    $1:company_name::VARCHAR(255),
    $1:industry::VARCHAR(50),
    $1:segment::VARCHAR(20),
    $1:employee_count::INTEGER,
    $1:annual_revenue::INTEGER,
    $1:state_province::VARCHAR(2),
    TO_DATE($1:signup_date::VARCHAR, 'MM/DD/YYYY'),
    $1:compliance_maturity::VARCHAR(15)
  FROM @PHANTOM_SEC_DATA_STAGE/DIM_CUSTOMERS.json
)
FILE_FORMAT = (FORMAT_NAME = JSON_FORMAT)
ON_ERROR = 'ABORT_STATEMENT';

-- Load DIM_COMPLIANCE_FRAMEWORKS (depends on nothing)
PUT file://data/DIM_COMPLIANCE_FRAMEWORKS.json @PHANTOM_SEC_DATA_STAGE;

COPY INTO DIM_COMPLIANCE_FRAMEWORKS
FROM (
  SELECT 
    $1:framework_id::INTEGER,
    $1:framework_name::VARCHAR(50),
    $1:framework_category::VARCHAR(30),
    $1:complexity_score::INTEGER,
    $1:avg_completion_days::INTEGER,
    $1:industry_relevance::VARCHAR(50),
    $1:geographic_scope::VARCHAR(20),
    $1:automation_percentage::INTEGER,
    $1:annual_audit_required::BOOLEAN,
    $1:certification_cost_usd::INTEGER
  FROM @PHANTOM_SEC_DATA_STAGE/DIM_COMPLIANCE_FRAMEWORKS.json
)
FILE_FORMAT = (FORMAT_NAME = JSON_FORMAT)
ON_ERROR = 'ABORT_STATEMENT';

-- Load FACT_SUBSCRIPTION_EVENTS (depends on customers)
PUT file://data/FACT_SUBSCRIPTION_EVENTS.json @PHANTOM_SEC_DATA_STAGE OVERWRITE=TRUE;

COPY INTO FACT_SUBSCRIPTION_EVENTS
FROM (
  SELECT 
    $1:event_id::INTEGER,
    $1:customer_id::INTEGER,
    TO_DATE($1:event_date::VARCHAR, 'MM/DD/YYYY'),
    $1:event_type::VARCHAR(15),
    $1:product_tier::VARCHAR(20),
    $1:mrr_amount::INTEGER,
    $1:billing_period::VARCHAR(15),
    $1:contract_length_months::INTEGER,
    $1:discount_percentage::DECIMAL(5,2),
    $1:sales_channel::VARCHAR(20),
    $1:payment_method::VARCHAR(20)
  FROM @PHANTOM_SEC_DATA_STAGE/FACT_SUBSCRIPTION_EVENTS.json
)
FILE_FORMAT = (FORMAT_NAME = JSON_FORMAT)
ON_ERROR = 'ABORT_STATEMENT';

-- Load FACT_FRAMEWORK_ADOPTIONS (depends on customers and frameworks)
PUT file://data/FACT_FRAMEWORK_ADOPTIONS.json @PHANTOM_SEC_DATA_STAGE OVERWRITE=TRUE;

COPY INTO FACT_FRAMEWORK_ADOPTIONS
FROM (
  SELECT 
    $1:adoption_id::INTEGER,
    $1:customer_id::INTEGER,
    $1:framework_id::INTEGER,
    TO_DATE($1:start_date::VARCHAR, 'MM/DD/YYYY'),
    TO_DATE($1:completion_date::VARCHAR, 'MM/DD/YYYY'),
    $1:status::VARCHAR(15),
    $1:audit_score::INTEGER,
    $1:hours_saved::INTEGER,
    $1:implementation_cost::INTEGER,
    $1:automation_level::INTEGER
  FROM @PHANTOM_SEC_DATA_STAGE/FACT_FRAMEWORK_ADOPTIONS.json
)
FILE_FORMAT = (FORMAT_NAME = JSON_FORMAT)
ON_ERROR = 'ABORT_STATEMENT';

-- Load FACT_COMPLIANCE_ACTIVITIES (depends on all previous tables)
PUT file://data/FACT_COMPLIANCE_ACTIVITIES.json @PHANTOM_SEC_DATA_STAGE OVERWRITE=TRUE;

COPY INTO FACT_COMPLIANCE_ACTIVITIES
FROM (
  SELECT 
    $1:activity_id::INTEGER,
    $1:customer_id::INTEGER,
    $1:framework_id::INTEGER,
    $1:adoption_id::INTEGER,
    TO_DATE($1:activity_date::VARCHAR, 'MM/DD/YYYY'),
    $1:activity_type::VARCHAR(20),
    $1:control_category::VARCHAR(25),
    $1:automated_flag::BOOLEAN,
    $1:duration_minutes::INTEGER,
    $1:success_flag::BOOLEAN,
    $1:risk_level::VARCHAR(10),
    $1:evidence_collected::BOOLEAN
  FROM @PHANTOM_SEC_DATA_STAGE/FACT_COMPLIANCE_ACTIVITIES.json
)
FILE_FORMAT = (FORMAT_NAME = JSON_FORMAT)
ON_ERROR = 'ABORT_STATEMENT';

-- =====================================================================================
-- 5. VALIDATION QUERIES
-- =====================================================================================

-- Verify table creation and row counts
SELECT 'DIM_CUSTOMERS' as table_name, COUNT(*) as row_count FROM DIM_CUSTOMERS
UNION ALL
SELECT 'DIM_COMPLIANCE_FRAMEWORKS' as table_name, COUNT(*) as row_count FROM DIM_COMPLIANCE_FRAMEWORKS  
UNION ALL
SELECT 'FACT_SUBSCRIPTION_EVENTS' as table_name, COUNT(*) as row_count FROM FACT_SUBSCRIPTION_EVENTS
UNION ALL
SELECT 'FACT_FRAMEWORK_ADOPTIONS' as table_name, COUNT(*) as row_count FROM FACT_FRAMEWORK_ADOPTIONS
UNION ALL
SELECT 'FACT_COMPLIANCE_ACTIVITIES' as table_name, COUNT(*) as row_count FROM FACT_COMPLIANCE_ACTIVITIES
ORDER BY table_name;

-- =====================================================================================
-- END OF SCRIPT
-- =====================================================================================
