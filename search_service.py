import os
import requests

# ============================================================
# SalesIQ Search Service
# Supports: Tavily, Serper, Google Custom Search, Bing Search
# Toggle each provider via environment variables.
# Priority order: Tavily → Serper → Google CSE → Bing
# ============================================================

class SearchService:

    TIMEOUT = 12

    # --------------------------------------------------------
    # Tavily Search (best for AI agents — returns clean text)
    # Enable: TAVILY_API_KEY=your_key
    # --------------------------------------------------------
    @staticmethod
    def search_tavily(company_name: str, website: str) -> dict:
        api_key = os.getenv("TAVILY_API_KEY", "").strip()
        if not api_key:
            return {"success": False, "error": "Tavily API key not configured."}

        query = f"{company_name} company overview products services"
        if website:
            query += f" site:{_extract_domain(website)}"

        try:
            response = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": api_key,
                    "query": query,
                    "search_depth": "basic",
                    "include_answer": True,
                    "include_raw_content": False,
                    "max_results": 5,
                },
                timeout=SearchService.TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()

            # Combine the AI answer + top result snippets
            parts = []
            if data.get("answer"):
                parts.append(data["answer"])
            for r in data.get("results", []):
                if r.get("content"):
                    parts.append(r["content"])

            combined = " ".join(parts).strip()
            if not combined or len(combined) < 50:
                return {"success": False, "error": "Tavily returned insufficient content."}

            return {
                "success": True,
                "text": combined[:10000],
                "source": "Search API",
                "provider": "Tavily",
            }
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Tavily request timed out."}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "error": f"Tavily HTTP error: {e.response.status_code}"}
        except Exception as e:
            return {"success": False, "error": f"Tavily error: {str(e)}"}

    # --------------------------------------------------------
    # Serper Search (Google results via serper.dev)
    # Enable: SERPER_API_KEY=your_key
    # --------------------------------------------------------
    @staticmethod
    def search_serper(company_name: str, website: str) -> dict:
        api_key = os.getenv("SERPER_API_KEY", "").strip()
        if not api_key:
            return {"success": False, "error": "Serper API key not configured."}

        query = f"{company_name} company overview products services"
        if website:
            query += f" {_extract_domain(website)}"

        try:
            response = requests.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
                json={"q": query, "num": 5},
                timeout=SearchService.TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()

            parts = []
            # Answer box (if available)
            if data.get("answerBox", {}).get("answer"):
                parts.append(data["answerBox"]["answer"])
            if data.get("answerBox", {}).get("snippet"):
                parts.append(data["answerBox"]["snippet"])
            # Knowledge graph
            if data.get("knowledgeGraph", {}).get("description"):
                parts.append(data["knowledgeGraph"]["description"])
            # Organic snippets
            for r in data.get("organic", []):
                if r.get("snippet"):
                    parts.append(r["snippet"])

            combined = " ".join(parts).strip()
            if not combined or len(combined) < 50:
                return {"success": False, "error": "Serper returned insufficient content."}

            return {
                "success": True,
                "text": combined[:10000],
                "source": "Search API",
                "provider": "Serper",
            }
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Serper request timed out."}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "error": f"Serper HTTP error: {e.response.status_code}"}
        except Exception as e:
            return {"success": False, "error": f"Serper error: {str(e)}"}

    # --------------------------------------------------------
    # Google Custom Search Engine (CSE)
    # Enable: GOOGLE_CSE_API_KEY=your_key & GOOGLE_CSE_ID=your_cx
    # --------------------------------------------------------
    @staticmethod
    def search_google_cse(company_name: str, website: str) -> dict:
        api_key = os.getenv("GOOGLE_CSE_API_KEY", "").strip()
        cx = os.getenv("GOOGLE_CSE_ID", "").strip()
        if not api_key or not cx:
            return {"success": False, "error": "Google CSE API key or CX ID not configured."}

        query = f"{company_name} company overview products services {_extract_domain(website)}"

        try:
            response = requests.get(
                "https://www.googleapis.com/customsearch/v1",
                params={"key": api_key, "cx": cx, "q": query, "num": 5},
                timeout=SearchService.TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()

            parts = []
            for item in data.get("items", []):
                if item.get("snippet"):
                    parts.append(item["snippet"])
                # Metatags description
                meta = item.get("pagemap", {}).get("metatags", [{}])[0]
                if meta.get("og:description"):
                    parts.append(meta["og:description"])

            combined = " ".join(parts).strip()
            if not combined or len(combined) < 50:
                return {"success": False, "error": "Google CSE returned insufficient content."}

            return {
                "success": True,
                "text": combined[:10000],
                "source": "Search API",
                "provider": "Google CSE",
            }
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Google CSE request timed out."}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "error": f"Google CSE HTTP error: {e.response.status_code}"}
        except Exception as e:
            return {"success": False, "error": f"Google CSE error: {str(e)}"}

    # --------------------------------------------------------
    # Bing Web Search API (Azure Cognitive Services)
    # Enable: BING_SEARCH_API_KEY=your_key
    # --------------------------------------------------------
    @staticmethod
    def search_bing(company_name: str, website: str) -> dict:
        api_key = os.getenv("BING_SEARCH_API_KEY", "").strip()
        if not api_key:
            return {"success": False, "error": "Bing Search API key not configured."}

        query = f"{company_name} company overview products services {_extract_domain(website)}"

        try:
            response = requests.get(
                "https://api.bing.microsoft.com/v7.0/search",
                headers={"Ocp-Apim-Subscription-Key": api_key},
                params={"q": query, "count": 5, "mkt": "en-US"},
                timeout=SearchService.TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()

            parts = []
            for r in data.get("webPages", {}).get("value", []):
                if r.get("snippet"):
                    parts.append(r["snippet"])

            combined = " ".join(parts).strip()
            if not combined or len(combined) < 50:
                return {"success": False, "error": "Bing Search returned insufficient content."}

            return {
                "success": True,
                "text": combined[:10000],
                "source": "Search API",
                "provider": "Bing",
            }
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Bing Search request timed out."}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "error": f"Bing HTTP error: {e.response.status_code}"}
        except Exception as e:
            return {"success": False, "error": f"Bing error: {str(e)}"}

    # --------------------------------------------------------
    # Unified Orchestrator: tries enabled providers in priority order
    # Returns the first successful result, or the last error dict.
    # --------------------------------------------------------
    @staticmethod
    def search(company_name: str, website: str) -> dict:
        """
        Tries all configured search providers in priority order:
        Tavily → Serper → Google CSE → Bing.
        Returns first successful result, otherwise returns failure dict
        with a 'provider' key set to 'None'.
        """
        providers = [
            ("Tavily",     os.getenv("TAVILY_API_KEY"),     SearchService.search_tavily),
            ("Serper",     os.getenv("SERPER_API_KEY"),     SearchService.search_serper),
            ("Google CSE", os.getenv("GOOGLE_CSE_API_KEY"), SearchService.search_google_cse),
            ("Bing",       os.getenv("BING_SEARCH_API_KEY"),SearchService.search_bing),
        ]

        last_error = {"success": False, "error": "No search API keys configured.", "provider": "None"}

        for name, key, fn in providers:
            if not key or not key.strip():
                continue  # Skip unconfigured providers
            result = fn(company_name, website)
            if result.get("success"):
                return result
            last_error = result
            last_error["provider"] = name  # track which one failed last

        return last_error


# --------------------------------------------------------
# Helper: extract bare domain from a URL string
# --------------------------------------------------------
def _extract_domain(url: str) -> str:
    if not url:
        return ""
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    from urllib.parse import urlparse
    try:
        return urlparse(url).netloc or url
    except Exception:
        return url
