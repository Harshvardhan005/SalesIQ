from database import get_db_connection
import json

class DatabaseService:

    @staticmethod
    def get_all_reports():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reports ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        result = []
        for r in rows:
            dict_row = dict(r)
            for array_field in ['pain_points', 'products', 'business_goals', 'growth_opportunities']:
                val = dict_row.get(array_field)
                if val:
                    try:
                        dict_row[array_field] = json.loads(val)
                    except Exception:
                        dict_row[array_field] = [val] if val else []
                else:
                    dict_row[array_field] = []
            result.append(dict_row)
        return result

    @staticmethod
    def get_report_by_company_name(company_name):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reports WHERE company_name = ? LIMIT 1", (company_name,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
            
        dict_row = dict(row)
        for array_field in ['pain_points', 'products', 'business_goals', 'growth_opportunities']:
            val = dict_row.get(array_field)
            if val:
                try:
                    dict_row[array_field] = json.loads(val)
                except Exception:
                    dict_row[array_field] = [val] if val else []
            else:
                dict_row[array_field] = []
        return dict_row

    @staticmethod
    def create_report(report_data):
        conn = get_db_connection()
        cursor = conn.cursor()

        pain_points_str = json.dumps(report_data.get('pain_points', []))
        products_str = json.dumps(report_data.get('products', []))
        business_goals_str = json.dumps(report_data.get('business_goals', []))
        growth_opportunities_str = json.dumps(report_data.get('growth_opportunities', []))

        cursor.execute('''
            INSERT INTO reports 
            (company_name, website, industry, product_offered, target_customer, notes, lead_score, pain_points,
             company_overview, products, business_goals, growth_opportunities, sales_strategy, confidence,
             email_script, linkedin_script)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            report_data['company_name'],
            report_data['website'],
            report_data['industry'],
            report_data.get('product_offered', ''),
            report_data.get('target_customer', ''),
            report_data.get('notes', ''),
            report_data['lead_score'],
            pain_points_str,
            report_data.get('company_overview', ''),
            products_str,
            business_goals_str,
            growth_opportunities_str,
            report_data.get('sales_strategy', ''),
            report_data.get('confidence', 'High'),
            report_data.get('email_script', ''),
            report_data.get('linkedin_script', '')
        ))
        conn.commit()
        report_id = cursor.lastrowid
        conn.close()
        return report_id

    @staticmethod
    def delete_report(report_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    @staticmethod
    def save_generated_content(company_name, content_type, prompt, output_text):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO generated_content (company_name, content_type, prompt, output_text)
            VALUES (?, ?, ?, ?)
        ''', (company_name, content_type, prompt, output_text))
        conn.commit()
        content_id = cursor.lastrowid
        conn.close()
        return content_id

    @staticmethod
    def get_all_leads():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM saved_leads ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def create_lead(lead_data):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO saved_leads (company_name, website, industry, lead_score, status, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            lead_data['company_name'],
            lead_data['website'],
            lead_data['industry'],
            lead_data['lead_score'],
            lead_data.get('status', 'High Fit'),
            lead_data.get('notes', '')
        ))
        conn.commit()
        lead_id = cursor.lastrowid
        conn.close()
        return lead_id

    @staticmethod
    def delete_lead(lead_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM saved_leads WHERE id = ?", (lead_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    @staticmethod
    def get_dashboard_stats():
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as total FROM reports")
        total_companies = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM saved_leads")
        total_leads = cursor.fetchone()['total']

        cursor.execute("SELECT AVG(lead_score) as avg_score FROM reports")
        avg_score_row = cursor.fetchone()['avg_score']
        avg_lead_score = round(avg_score_row, 1) if avg_score_row else 90.0

        cursor.execute("SELECT COUNT(*) as total FROM reports")
        recent_reports = cursor.fetchone()['total']

        conn.close()

        return {
            "total_companies": total_companies,
            "total_leads": total_leads,
            "avg_lead_score": avg_lead_score,
            "recent_reports": recent_reports
        }

    # ── User Authentication ────────────────────────────────────────────────────

    @staticmethod
    def create_user(name, email, password_hash):
        """Insert a new user. Raises ValueError on duplicate email."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, password_hash)
            )
            conn.commit()
            user_id = cursor.lastrowid
        except Exception as e:
            conn.close()
            raise ValueError(f"Email already registered: {str(e)}")
        conn.close()
        return user_id

    @staticmethod
    def get_user_by_email(email):
        """Fetch a user row by email. Returns a dict or None."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? LIMIT 1", (email,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

