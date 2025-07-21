import psycopg2
import json
import traceback

# --- CONFIGURATION ---
SOURCE_DB = {
    'dbname': 'orbe_dev',
    'user': 'postgres',
    'password': 'Admin0rbE',
    'host': 'orbe360.ai',
    'port': '5432',
}

TARGET_DB = {
    'dbname': 'orbe_insights',
    'user': 'postgres',
    'password': 'Admin0rbE',
    'host': 'orbe360.ai',
    'port': '5432',
}

def connect(config):
    return psycopg2.connect(
        dbname=config['dbname'], user=config['user'],
        password=config['password'], host=config['host'], port=config['port']
    )

def get_nested(data, path, default=None):
    for part in path.split('.'):
        if isinstance(data, dict):
            data = data.get(part, default)
        else:
            return default
    return data

def clean_value(val):
    if val is None:
        return None
    if isinstance(val, str) and val.strip() == '':
        return None
    return val

def safe_value(val):
    if isinstance(val, (dict, list)):
        return json.dumps(val)
    return clean_value(val)

def safe_year(val):
    if not val or (isinstance(val, str) and val.strip() == ''):
        return None
    if isinstance(val, str):
        import re
        matches = re.findall(r'\b(\d{4})\b', val)
        return int(matches[-1]) if matches else None
    if isinstance(val, int):
        return val
    return None

def safe_numeric(val):
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return val
    if isinstance(val, str):
        import re
        # Remove currency symbols and commas, handle M/K/B suffixes
        s = val.replace(',', '').replace('$', '').strip().upper()
        match = re.match(r'([0-9.]+)\s*([KMB]?)', s)
        if match:
            num = float(match.group(1))
            mult = match.group(2)
            if mult == 'K':
                num *= 1_000
            elif mult == 'M':
                num *= 1_000_000
            elif mult == 'B':
                num *= 1_000_000_000
            return num
        try:
            return float(s)
        except Exception:
            return None
    return None

def process_row(row, cur):
    try:
        cur.execute("SAVEPOINT row_savepoint;")
        company_id = row['id']  # UUID string, use as is
        # --- PROFILE ---
        profile = row.get('profile', {}) or {}
        if isinstance(profile, str):
            profile = json.loads(profile)
        profile = profile.get('data', {}) or {}

        # --- COMPANY ---
        company = get_nested(profile, 'company', {})
        contact = company.get('contact', {})
        cur.execute("""
            INSERT INTO COMPANY (company_id, name, website, location, description,
            contact_name, contact_email, contact_phone, contact_position)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (company_id) DO NOTHING;
        """, (
            company_id,
            safe_value(company.get('name')),
            safe_value(company.get('website')),
            safe_value(company.get('location')),
            safe_value(company.get('description')),
            safe_value(contact.get('name')),
            safe_value(contact.get('email')),
            safe_value(contact.get('phone')),
            safe_value(contact.get('position'))
        ))

        # --- TEAM ---
        for member in profile.get('team', []):
            cur.execute("""
                INSERT INTO TEAM (company_id, name, position, experience)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (
                company_id,
                safe_value(member.get('name')),
                safe_value(member.get('position')),
                safe_value(member.get('experience'))
            ))

        # --- FINANCIALS ---
        financial = row.get('financial', {}) or {}
        if isinstance(financial, str):
            financial = json.loads(financial)
        financial = financial.get('data', {}) or {}
        fin_data = get_nested(financial, 'financial_analysis.financials', {})

        cur.execute("""
            INSERT INTO FINANCIALS (company_id, total_funding, recent_revenue, projection,
            arr, burn_rate_monthly, cash_on_hand, ebitda, ebitda_margin, fcf,
            gross_margin_percent, nrr, sensitivity_scenarios, currency, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (company_id) DO NOTHING;
        """, (
            company_id,
            safe_value(get_nested(profile, 'financials.funding.total_funding')),
            safe_value(get_nested(profile, 'financials.revenue.recent')),
            safe_value(get_nested(profile, 'financials.revenue.projection')),
            safe_value(fin_data.get('arr')),
            safe_value(fin_data.get('burn_rate_monthly')),
            safe_value(fin_data.get('cash_on_hand')),
            safe_value(fin_data.get('ebitda')),
            safe_value(fin_data.get('ebitda_margin')),
            safe_value(fin_data.get('fcf')),
            safe_value(fin_data.get('gross_margin_percent')),
            safe_value(fin_data.get('nrr')),
            safe_value(fin_data.get('sensitivity_scenarios')),
            safe_value(get_nested(financial, 'financial_analysis.currency')),
            safe_value(get_nested(financial, 'financial_analysis.notes')),
        ))

        # --- FUNDING_ROUNDS ---
        for round in get_nested(profile, 'financials.funding.rounds', []):
            cur.execute("""
                INSERT INTO FUNDING_ROUNDS (funding_round_id, company_id, stage, amount, status, notes)
                VALUES (DEFAULT, %s, %s, %s, %s, %s)
                RETURNING funding_round_id;
            """, (
                company_id,
                safe_value(round.get('stage')),
                safe_value(round.get('amount')),
                safe_value(round.get('status')),
                safe_value(round.get('notes'))
            ))
            round_id = cur.fetchone()[0]
            for contributor in round.get('contributors', []):
                cur.execute("""
                    INSERT INTO FUNDING_CONTRIBUTERS (funding_round_id, name, type, contribution)
                    VALUES (%s, %s, %s, %s);
                """, (
                    round_id,
                    safe_value(contributor.get('name')),
                    safe_value(contributor.get('type')),
                    safe_value(contributor.get('contribution'))
                ))

        # --- FUTURE FUNDING PLANS ---
        for plan in get_nested(profile, 'financials.funding.future_plans', []):
            cur.execute("""
                INSERT INTO FUTURE_FUNDING_PLANS (company_id, purpose, planned_stage, target_amount, status)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (company_id) DO NOTHING;
            """, (
                company_id,
                safe_value(plan.get('purpose')),
                safe_value(plan.get('planned_stage')),
                safe_value(plan.get('target_amount')),
                safe_value(plan.get('status'))
            ))

        # --- PRODUCT_SERVICE ---
        prod = get_nested(profile, 'product_or_service', {})
        tech = prod.get('technology_stack', {})
        cur.execute("""
            INSERT INTO PRODUCT_SERVICE (company_id, overview, features, value_proposition,
            technology_stack_hardware, technology_stack_software, technology_stack_other)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (
            company_id,
            safe_value(prod.get('overview')),
            safe_value(prod.get('features')),
            safe_value(prod.get('value_proposition')),
            safe_value(tech.get('hardware')),
            safe_value(tech.get('software')),
            safe_value(tech.get('other'))
        ))

        # --- INVESTMENT_MEMO ---
        insights = get_nested(profile, 'investment_memo_insights', {})
        cur.execute("""
            INSERT INTO INVESTMENT_MEMO (company_id, exec_summary, why_now, deal_summary,
            use_of_funds, product_overview, risks_mitigations, team_snapshot,
            exit_opportunities, funding_round)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (company_id) DO NOTHING;
        """, (
            company_id,
            safe_value(insights.get('exec_summary')),
            safe_value(insights.get('why_now')),
            safe_value(insights.get('deal_summary')),
            safe_value(insights.get('use_of_funds')),
            safe_value(insights.get('product_overview')),
            safe_value(insights.get('risks_mitigations')),
            safe_value(insights.get('team_snapshot')),
            safe_value(insights.get('exit_opportunities')),
            safe_value(insights.get('funding_round'))
        ))

        # --- FOUNDER_ANALYSIS ---
        founder_sentiment = row.get('founderSentiment', {}) or {}
        if isinstance(founder_sentiment, str):
            founder_sentiment = json.loads(founder_sentiment)
        founder_sentiment = founder_sentiment.get('data', {}) or {}
        for i, founder in enumerate(get_nested(founder_sentiment, 'founder_analyses', [])):
            founder_id = i + 1
            cur.execute("""
                INSERT INTO FOUNDER_ANALYSIS (founder_id, company_id, name, "current_role", overall_assessment)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (
                founder_id,
                company_id,
                safe_value(founder.get('name')),
                safe_value(founder.get('current_role')),
                safe_value(founder.get('overall_assessment'))
            ))

            for edu in founder.get('background', {}).get('education', []):
                year = safe_year(edu.get('year'))
                cur.execute("""
                    INSERT INTO FOUNDER_EDUCATION (founder_id, institution, degree, field, year)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING;
                """, (
                    founder_id,
                    safe_value(edu.get('institution')),
                    safe_value(edu.get('degree')),
                    safe_value(edu.get('field')),
                    year
                ))

            for exp in founder.get('background', {}).get('prior_experiences', []):
                cur.execute("""
                    INSERT INTO FOUNDER_EXPERIENCE (founder_id, company, role, description, duration)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING;
                """, (
                    founder_id,
                    safe_value(exp.get('company')),
                    safe_value(exp.get('role')),
                    safe_value(exp.get('description')),
                    safe_value(exp.get('duration'))
                ))

            for soc in founder.get('social_media_presence', []):
                cur.execute("""
                    INSERT INTO FOUNDER_SOCIAL_MEDIA (founder_id, platform, profile_url, sentiment, activity_level, followers)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING;
                """, (
                    founder_id,
                    safe_value(soc.get('platform')),
                    safe_value(soc.get('profile_url')),
                    safe_value(soc.get('sentiment')),
                    safe_value(soc.get('activity_level')),
                    safe_value(soc.get('followers'))
                ))

            for risk in founder.get('key_risks', []):
                cur.execute("""
                    INSERT INTO FOUNDER_RISK_TABLE (founder_id, risk_type, description, severity, mitigation_suggestion)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING;
                """, (
                    founder_id,
                    safe_value(risk.get('risk_type')),
                    safe_value(risk.get('description')),
                    safe_value(risk.get('severity')),
                    safe_value(risk.get('mitigation_suggestion'))
                ))

        # --- PRODUCT_INSIGHTS ---
        product = row.get('product', {}) or {}
        if isinstance(product, str):
            product = json.loads(product)
        product = product.get('data', {}) or {}
        product_insights = product.get('product_insights', {})
        cur.execute("""
            INSERT INTO PRODUCT_INSIGHTS (company_id, usp, product_overview, innovation_pipeline, milestones, product_roadmap)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (company_id) DO NOTHING;
        """, (
            company_id,
            safe_value(product_insights.get('usp')),
            safe_value(product_insights.get('product_overview')),
            safe_value(product_insights.get('innovation_pipeline')),
            safe_value(product_insights.get('milestones')),
            safe_value(product_insights.get('product_roadmap'))
        ))

        # --- INVESTMENTS ---
        investments = row.get('investments', {}) or {}
        if isinstance(investments, str):
            investments = json.loads(investments)
        cur.execute("""
            INSERT INTO INVESTMENTS (company_id, my_investments, pre_money_valuation, post_money_valuation, reasoning)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (company_id) DO NOTHING;
        """, (
            company_id,
            safe_value(investments.get('myInvestments')),
            safe_numeric(investments.get('preMoneyValuation')),
            safe_numeric(investments.get('postMoneyValuation')),
            safe_value(investments.get('reasoning'))
        ))
        cur.execute("RELEASE SAVEPOINT row_savepoint;")
    except Exception as e:
        print(f"Error processing company_id {row.get('id')}: {e}")
        traceback.print_exc()
        cur.execute("ROLLBACK TO SAVEPOINT row_savepoint;")

def main():
    src_conn = connect(SOURCE_DB)
    tgt_conn = connect(TARGET_DB)
    src_cur = src_conn.cursor()
    tgt_cur = tgt_conn.cursor()

    src_cur.execute("""SELECT id, profile, market, product, "pitchDeckSentiment", "companySentiment", "founderSentiment", financial, "investmentMemo", investments FROM insights""")
    rows = src_cur.fetchall()
    colnames = [desc[0] for desc in src_cur.description]

    for r in rows:
        row = dict(zip(colnames, r))
        process_row(row, tgt_cur)

    tgt_conn.commit()
    print(f"Inserted {len(rows)} rows.")
    src_conn.close()
    tgt_conn.close()

if __name__ == '__main__':
    main()