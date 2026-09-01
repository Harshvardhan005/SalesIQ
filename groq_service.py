import os
import json
import time
import requests

class GroqService:
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    DEFAULT_MODEL = "openai/gpt-oss-20b"
    TIMEOUT = 25  # seconds

    @classmethod
    def analyze_company(cls, company_name, website, industry, product_offered="", target_customer="", notes="", scraped_content="", information_source=""):
        """
        Queries Groq AI completions API to perform a structured B2B sales analysis.
        Returns a dictionary conforming to the requested schema.
        """
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("Missing Groq API Key. Please add GROQ_API_KEY to your .env file.")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        system_instruction = (
            "You are a premium B2B Sales Intelligence AI. Your job is to analyze target prospect companies "
            "and generate structured sales reports. You must evaluate the fit of the target company for our product "
            "and identify key buying signals. You must return a valid JSON object ONLY. No conversational introduction, "
            "no markdown formatting backticks, no trailing explanation."
        )

        user_prompt = f"""
Analyze the target company based on the following firmographic inputs:
- Target Company Name: {company_name}
- Website/Domain: {website}
- Industry: {industry}
- Product/Service We Offer Them: {product_offered or 'Our B2B Solution'}
- Target Buyer Persona/Title: {target_customer or 'Revenue/Operational Leaders'}
- Custom Research Notes: {notes or 'None provided.'}
- Information Source: {information_source or 'None'}
- Scraped Website Content: {scraped_content[:1500] if scraped_content else 'None available.'}

Analyze the target company and return exactly this JSON structure:
{{
  "company_overview": "A detailed 2-3 sentence summary of the company's business model and operations.",
  "industry": "Standardized industry name.",
  "products": ["List of key products or services they offer (max 3)"],
  "pain_points": ["Specific operational pain points they face that our product can solve (max 3)"],
  "business_goals": ["Primary business goals they are likely pursuing (max 3)"],
  "growth_opportunities": ["Opportunities for growth or expansion where they could use our solution (max 3)"],
  "sales_strategy": "A customized strategic sales playbook on how to pitch our product to them, highlighting key value props.",
  "lead_score": 85,
  "confidence": "High"
}}

Rules:
1. Ensure 'lead_score' is an integer between 0 and 100.
2. Ensure 'confidence' is either 'High', 'Medium', or 'Low'.
3. The response must be valid JSON matching the schema above.
"""

        payload = {
            "model": cls.DEFAULT_MODEL,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
            "max_tokens": 1200
        }

        # Handle rate limits and retries
        retries = 2
        backoff = 2  # seconds

        for attempt in range(retries + 1):
            try:
                response = requests.post(
                    cls.API_URL, 
                    headers=headers, 
                    json=payload, 
                    timeout=cls.TIMEOUT
                )

                if response.status_code == 429:
                    if attempt < retries:
                        time.sleep(backoff)
                        backoff *= 2
                        continue
                    else:
                        raise RuntimeError("Groq API rate limit exceeded (HTTP 429). Please try again shortly.")

                if response.status_code != 200:
                    error_msg = f"Groq API returned error status {response.status_code}."
                    try:
                        err_json = response.json()
                        error_msg += f" Details: {err_json.get('error', {}).get('message', '')}"
                    except Exception:
                        error_msg += f" Response: {response.text[:100]}"
                    raise RuntimeError(error_msg)

                result_data = response.json()
                content = result_data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

                if not content:
                    raise ValueError("Groq returned an empty response.")

                # Parse the response JSON
                parsed_json = cls._parse_json(content)
                cls._validate_schema(parsed_json)
                return parsed_json

            except requests.exceptions.Timeout:
                if attempt < retries:
                    time.sleep(1)
                    continue
                raise RuntimeError(f"Groq API connection timed out after {cls.TIMEOUT} seconds.")

            except requests.exceptions.RequestException as e:
                raise RuntimeError(f"Network error communicating with Groq API: {str(e)}")

        raise RuntimeError("Failed to get response from Groq API after multiple attempts.")

    @classmethod
    def generate_sales_content(cls, company_info, content_type, tone, length, custom_prompt=""):
        """
        Queries Groq AI completions API to generate personalized sales copy.
        Returns the raw generated text content.
        """
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("Missing Groq API Key. Please add GROQ_API_KEY to your .env file.")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Format arrays for prompt injection
        products_list = ", ".join(company_info.get("products", []))
        pain_points_list = ", ".join(company_info.get("pain_points", []))
        goals_list = ", ".join(company_info.get("business_goals", []))
        opportunities_list = ", ".join(company_info.get("growth_opportunities", []))

        system_instruction = (
            "You are a premium B2B Sales Copywriter. Your goal is to draft hyper-personalized sales outreach content "
            "based on firmographic details. Do not include markdown code block backticks (like ```), do not include intro "
            "or outro remarks (like 'Here is the requested email:'). Output only the final copy ready to send."
        )

        user_prompt = f"""
Draft a personalized sales outreach copy using these parameters:
- Content Type: {content_type}
- Tone: {tone}
- Length/Detail level: {length}
- Custom Instructions: {custom_prompt or 'None'}

Target Prospect Information:
- Company Name: {company_info.get('company_name')}
- Industry: {company_info.get('industry')}
- Fit Score: {company_info.get('lead_score')}/100
- Company Overview: {company_info.get('company_overview')}
- Products they offer: {products_list}
- Business Pain Points: {pain_points_list}
- Core Business Goals: {goals_list}
- Growth Opportunities: {opportunities_list}

Our Information:
- Product Offered: {company_info.get('product_offered') or 'Our SalesIQ platform'}
- Value/Sales Strategy Playbook: {company_info.get('sales_strategy')}

Rules:
1. Ensure the output matches the requested content type ('Cold Email', 'Follow-up Email', 'LinkedIn Connection Request', etc.).
2. The tone must reflect '{tone}' (Professional, Friendly, Consultative, or Persuasive).
3. The length must align with '{length}':
   - Short: Quick outreach/note (under 120 words).
   - Medium: Standard length (120-250 words).
   - Long: Highly detailed or multi-step/script (250-450 words).
4. Output only the final ready-to-use copy. Do not add markdown wraps or conversational intro/outro text.
"""

        payload = {
            "model": cls.DEFAULT_MODEL,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }

        retries = 2
        backoff = 2

        for attempt in range(retries + 1):
            try:
                response = requests.post(
                    cls.API_URL, 
                    headers=headers, 
                    json=payload, 
                    timeout=cls.TIMEOUT
                )

                if response.status_code == 429:
                    if attempt < retries:
                        time.sleep(backoff)
                        backoff *= 2
                        continue
                    else:
                        raise RuntimeError("Groq API rate limit exceeded (HTTP 429). Please try again shortly.")

                if response.status_code != 200:
                    error_msg = f"Groq API returned error status {response.status_code}."
                    try:
                        err_json = response.json()
                        error_msg += f" Details: {err_json.get('error', {}).get('message', '')}"
                    except Exception:
                        pass
                    raise RuntimeError(error_msg)

                result_data = response.json()
                content = result_data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

                if not content:
                    raise ValueError("Groq returned an empty response.")

                # Remove markdown wraps if present
                if content.startswith("```"):
                    lines = content.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].strip() == "```":
                        lines = lines[:-1]
                    content = "\n".join(lines).strip()
                
                return content

            except requests.exceptions.Timeout:
                if attempt < retries:
                    time.sleep(1)
                    continue
                raise RuntimeError(f"Groq API connection timed out after {cls.TIMEOUT} seconds.")

            except requests.exceptions.RequestException as e:
                raise RuntimeError(f"Network error communicating with Groq API: {str(e)}")

        raise RuntimeError("Failed to get response from Groq API after multiple attempts.")

    @staticmethod
    def _parse_json(text_content):
        """Helper to safely parse JSON from raw LLM output, handling markdown wrappers."""
        cleaned = text_content.strip()
        # Remove markdown code block wraps if present
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            if lines[0].startswith("```json") or lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse structured JSON from Groq response: {str(e)}. Raw output was: {text_content[:200]}")

    @staticmethod
    def _validate_schema(data):
        """Ensures all requested keys are present in the parsed dictionary."""
        required_keys = [
            "company_overview", "industry", "products", "pain_points", 
            "business_goals", "growth_opportunities", "sales_strategy", 
            "lead_score", "confidence"
        ]
        
        missing = [k for k in required_keys if k not in data]
        if missing:
            raise ValueError(f"AI response is missing required keys: {', '.join(missing)}")

        # Clean/sanitize values
        if not isinstance(data.get("products"), list):
            data["products"] = [str(data.get("products"))] if data.get("products") else []
        if not isinstance(data.get("pain_points"), list):
            data["pain_points"] = [str(data.get("pain_points"))] if data.get("pain_points") else []
        if not isinstance(data.get("business_goals"), list):
            data["business_goals"] = [str(data.get("business_goals"))] if data.get("business_goals") else []
        if not isinstance(data.get("growth_opportunities"), list):
            data["growth_opportunities"] = [str(data.get("growth_opportunities"))] if data.get("growth_opportunities") else []

        try:
            data["lead_score"] = int(data.get("lead_score", 90))
        except (ValueError, TypeError):
            data["lead_score"] = 90
            
        if data.get("confidence") not in ["High", "Medium", "Low"]:
            data["confidence"] = "High"
