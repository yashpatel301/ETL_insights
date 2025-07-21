CREATE TABLE COMPANY (
    company_id UUID PRIMARY KEY,
    name VARCHAR(255),
    website VARCHAR(255),
    location VARCHAR(255),
    description TEXT,
    contact_name VARCHAR(255),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    contact_position VARCHAR(255)
);

CREATE TABLE COMPANY_PROFILE (
    company_id UUID PRIMARY KEY,
    legal_entity_name VARCHAR(255),
    jurisdiction VARCHAR(255),
    registered_address TEXT,
    date_of_incorporation DATE,
    business_stage VARCHAR(255),
    founders TEXT,
    key_milestones TEXT,
    board_members TEXT,
    FOREIGN KEY (company_id) REFERENCES COMPANY(company_id)
);

CREATE TABLE FINANCIALS (
    company_id UUID PRIMARY KEY,
    total_funding NUMERIC,
    recent_revenue NUMERIC,
    projection NUMERIC,
    arr NUMERIC,
    burn_rate_monthly NUMERIC,
    cash_on_hand NUMERIC,
    ebitda NUMERIC,
    ebitda_margin NUMERIC,
    fcf NUMERIC,
    gross_margin_percent NUMERIC,
    nrr NUMERIC,
    sensitivity_scenarios TEXT,
    currency VARCHAR,
    notes TEXT,
    FOREIGN KEY (company_id) REFERENCES COMPANY(company_id)
);

CREATE TABLE FUNDING_ROUNDS (
    funding_round_id SERIAL PRIMARY KEY,
    company_id UUID,
    stage VARCHAR(255),
    amount DECIMAL,
    status VARCHAR(255),
    notes TEXT,
    FOREIGN KEY (company_id) REFERENCES COMPANY(company_id)
);

CREATE TABLE FUNDING_CONTRIBUTERS (
    funding_round_id INT,
    name VARCHAR(255),
    type VARCHAR(100),
    contribution DECIMAL,
    FOREIGN KEY (funding_round_id) REFERENCES FUNDING_ROUNDS(funding_round_id)
);

CREATE TABLE FUTURE_FUNDING_PLANS (
    company_id UUID PRIMARY KEY,
    purpose TEXT,
    planned_stage VARCHAR(255),
    target_amount DECIMAL,
    status VARCHAR(255),
    FOREIGN KEY (company_id) REFERENCES COMPANY(company_id)
);

CREATE TABLE PRODUCT_SERVICE (
    company_id UUID,
    overview TEXT,
    features TEXT,
    value_proposition TEXT,
    technology_stack_hardware TEXT,
    technology_stack_software TEXT,
    technology_stack_other TEXT,
    FOREIGN KEY (company_id) REFERENCES COMPANY(company_id)
);

CREATE TABLE COMPETITION (
    company_id UUID,
    name VARCHAR(255),
    location VARCHAR(255),
    last_raised_date DATE,
    employees INT,
    post_valuation DECIMAL,
    total_funding DECIMAL,
    FOREIGN KEY (company_id) REFERENCES COMPANY(company_id)
);

CREATE TABLE MARKET_AND_INDUSTRY (
    company_id UUID PRIMARY KEY,
    target_customers TEXT,
    target_industries TEXT,
    go_to_market_strategy TEXT,
    total_addressable_market DECIMAL,
    expansion_plan TEXT,
    FOREIGN KEY (company_id) REFERENCES COMPANY(company_id)
);

CREATE TABLE BUSINESS_MODEL (
    company_id UUID PRIMARY KEY,
    revenue_model TEXT,
    pricing_strategy TEXT,
    customer_lifetime_value DECIMAL,
    FOREIGN KEY (company_id) REFERENCES COMPANY(company_id)
);

CREATE TABLE INVESTMENT_MEMO (
    company_id UUID PRIMARY KEY,
    exec_summary TEXT,
    why_now TEXT,
    deal_summary TEXT,
    use_of_funds TEXT,
    product_overview TEXT,
    risks_mitigations TEXT,
    team_snapshot TEXT,
    exit_opportunities TEXT,
    funding_round TEXT,
    FOREIGN KEY (company_id) REFERENCES COMPANY(company_id)
);

CREATE TABLE INVESTMENT_PARTIES (
    company_id UUID PRIMARY KEY,
    investors TEXT,
    lead_investors TEXT,
    FOREIGN KEY (company_id) REFERENCES COMPANY(company_id)
);

CREATE TABLE TEAM (
    company_id UUID,
    name VARCHAR(255),
    position VARCHAR(255),
    experience TEXT,
    FOREIGN KEY (company_id) REFERENCES COMPANY(company_id)
);

CREATE TABLE SENTIMENT_ANALYSIS (
    company_id UUID PRIMARY KEY,
    tone VARCHAR(50),
    tone_aspect VARCHAR(255),
    tone_strength VARCHAR(50),
    tone_impact VARCHAR(50),
    tone_improvement_suggestion TEXT,
    clarity_section TEXT,
    clarity_strengths TEXT,
    clarity_weakness TEXT,
    clarity_recommendation TEXT,
    clarity_score DECIMAL,
    narrative_strength TEXT,
    market_fit_articulation TEXT,
    value_clarity TEXT,
    impression_key_recommendations TEXT,
    impression_strongest_elements TEXT,
    impression_weakest_elements TEXT,
    orbe_score DECIMAL,
    prominence TEXT,
    credibility_indicators TEXT,
    portrayal TEXT,
    FOREIGN KEY (company_id) REFERENCES COMPANY(company_id)
);

CREATE TABLE FOUNDER_ANALYSIS (
    founder_id INT PRIMARY KEY,
    company_id UUID,
    name VARCHAR(255),
    "current_role" VARCHAR(255),
    overall_assessment TEXT,
    FOREIGN KEY (company_id) REFERENCES COMPANY(company_id)
);

CREATE TABLE FOUNDER_EDUCATION (
    founder_id INT,
    institution VARCHAR(255),
    degree VARCHAR(255),
    field VARCHAR(255),
    year INT,
	FOREIGN KEY (founder_id) REFERENCES FOUNDER_ANALYSIS(founder_id)
);

CREATE TABLE FOUNDER_EXPERIENCE (
    founder_id INT,
    company VARCHAR(255),
    role VARCHAR(255),
    description TEXT,
    duration VARCHAR(100),
	FOREIGN KEY (founder_id) REFERENCES FOUNDER_ANALYSIS(founder_id)
);

CREATE TABLE FOUNDER_SOCIAL_MEDIA (
    founder_id INT,
    platform VARCHAR(100),
    profile_url TEXT,
    sentiment VARCHAR(100),
    activity_level VARCHAR(100),
    followers INT,
	FOREIGN KEY (founder_id) REFERENCES FOUNDER_ANALYSIS(founder_id)
);

CREATE TABLE FOUNDER_RISK_TABLE (
    founder_id INT,
    risk_type VARCHAR(255),
    description TEXT,
    severity VARCHAR(100),
    mitigation_suggestion TEXT,
	FOREIGN KEY (founder_id) REFERENCES FOUNDER_ANALYSIS(founder_id)
);

CREATE TABLE FINANCIAL_FUNDING_NEEDS (
    company_id UUID,
    amount NUMERIC,
    year INT,
	PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES COMPANY(company_id)
);

CREATE TABLE FINANCIAL_CASH_FLOW_FUNDING_NEEDS (
    company_id UUID,
    amount NUMERIC,
    year INT,
	PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES COMPANY(company_id)
);

CREATE TABLE FINANCIAL_CASH_FLOW (
    company_id UUID PRIMARY KEY,
    burn_rate NUMERIC,
    runway_months INT,
    FOREIGN KEY (company_id) REFERENCES COMPANY(company_id)
);

CREATE TABLE FINANCIAL_REVENUE_BY_YEAR (
    company_id UUID,
    year INT,
    is_projected BOOLEAN,
    revenue NUMERIC,
    expenses NUMERIC,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES COMPANY(company_id)
);

CREATE TABLE FINANCIAL_UNIT_ECONOMICS (
    company_id UUID PRIMARY KEY,
    cac NUMERIC,
    ltv NUMERIC,
    payback_period NUMERIC,
    FOREIGN KEY (company_id) REFERENCES COMPANY(company_id)
);

CREATE TABLE INVESTMENTS (
    company_id UUID PRIMARY KEY,
    my_investments TEXT,
    pre_money_valuation NUMERIC,
    post_money_valuation NUMERIC,
    reasoning TEXT,
    FOREIGN KEY (company_id) REFERENCES COMPANY(company_id)
);

CREATE TABLE PRODUCT_INSIGHTS (
    company_id UUID PRIMARY KEY,
    usp TEXT,
    product_overview TEXT,
    innovation_pipeline TEXT,
    milestones TEXT,
    product_roadmap TEXT,
    FOREIGN KEY (company_id) REFERENCES COMPANY(company_id)
);