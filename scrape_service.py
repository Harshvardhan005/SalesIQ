import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

class ScrapeService:
    TIMEOUT = 15
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    @staticmethod
    def validate_url(url):
        if not url:
            return None
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname
            if not parsed.netloc or not hostname:
                return None
            
            # SSRF Protection: Block localhost and private/reserved IP ranges
            hostname_lower = hostname.lower()
            if hostname_lower in ['localhost', '127.0.0.1', '0.0.0.0', '::1'] or hostname_lower.endswith('.local') or hostname_lower.endswith('.internal'):
                return None
            
            # Block internal IPv4 private ranges (10.x.x.x, 172.16-31.x.x, 192.168.x.x, 169.254.x.x)
            import ipaddress
            try:
                ip = ipaddress.ip_address(hostname)
                if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                    return None
            except ValueError:
                # Hostname is a regular domain string (e.g. google.com)
                pass

            return url
        except:
            return None

    @staticmethod
    def is_restricted_page(url):
        restricted_keywords = ['/login', '/signin', '/admin', '/dashboard', '/portal', '/auth']
        url_lower = url.lower()
        for keyword in restricted_keywords:
            if keyword in url_lower:
                return True
        return False

    @staticmethod
    def scrape_website(url):
        valid_url = ScrapeService.validate_url(url)
        if not valid_url:
            return {"success": False, "error": "Invalid URL format."}

        if ScrapeService.is_restricted_page(valid_url):
            return {"success": False, "error": "Cannot scrape login or private pages."}

        headers = {"User-Agent": ScrapeService.USER_AGENT}
        try:
            response = requests.get(valid_url, headers=headers, timeout=ScrapeService.TIMEOUT)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "footer", "noscript", "meta", "header", "svg", "iframe", "form"]):
                element.decompose()

            # Extract text
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean lines and remove duplicates while preserving order
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            unique_lines = list(dict.fromkeys(lines))
            clean_text = ' '.join(unique_lines)

            # Limit text length to avoid token limits (e.g., first 10000 chars)
            clean_text = clean_text[:10000]

            if not clean_text or len(clean_text) < 50:
                return {"success": False, "error": "Insufficient text content found on the page."}

            return {"success": True, "text": clean_text, "source": "Website"}

        except requests.exceptions.Timeout:
            return {"success": False, "error": "Connection timed out."}
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in [403, 401]:
                return {"success": False, "error": "Access denied (403/401)."}
            elif e.response.status_code == 404:
                return {"success": False, "error": "Page not found (404)."}
            else:
                return {"success": False, "error": f"HTTP Error: {e.response.status_code}"}
        except requests.exceptions.SSLError:
            return {"success": False, "error": "SSL certificate validation failed."}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Failed to fetch website: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Scraping error: {str(e)}"}
