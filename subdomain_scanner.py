"""
Subdomain Scanner - Discovers and validates subdomains
"""

import requests
import socket
import concurrent.futures
from urllib.parse import urlparse


class SubdomainScanner:
    """
    Discovers active subdomains using multiple sources
    """

    def __init__(self, max_subdomains=20):
        self.max_subdomains = max_subdomains
        self.headers = {"User-Agent": "Mozilla/5.0 (Security Scanner)"}

    def find_subdomains(self, domain):
        """
        Find all active subdomains for a given domain
        """
        print(f"[*] Finding subdomains for: {domain}")

        # Clean domain
        domain = domain.replace('https://', '').replace('http://', '').split('/')[0]

        # Collect subdomains from multiple sources
        subdomains = set()

        # Source 1: crt.sh (Certificate Transparency Logs)
        subdomains.update(self._fetch_from_crtsh(domain))

        # Source 2: HackerTarget
        subdomains.update(self._fetch_from_hackertarget(domain))

        # Source 3: Common subdomains
        subdomains.update(self._try_common_subdomains(domain))

        # Always include main domain
        subdomains.add(domain)
        subdomains.add(f"www.{domain}")

        print(f"[*] Found {len(subdomains)} potential subdomains")

        # Validate which ones are active
        active_subdomains = self._validate_subdomains(list(subdomains))

        print(f"[+] {len(active_subdomains)} active subdomains validated")

        # Limit to max_subdomains
        return active_subdomains[:self.max_subdomains]

    def _fetch_from_crtsh(self, domain):
        """Fetch subdomains from crt.sh"""
        subdomains = set()

        try:
            url = f"https://crt.sh/?q=%25.{domain}&output=json"
            response = requests.get(url, headers=self.headers, timeout=15)

            if response.status_code == 200:
                data = response.json()
                for entry in data:
                    name = entry.get('name_value', '')
                    for subdomain in name.split('\n'):
                        subdomain = subdomain.strip().replace('*.', '')
                        if subdomain and '.' in subdomain:
                            subdomains.add(subdomain)

                print(f"[+] crt.sh: Found {len(subdomains)} subdomains")

        except Exception as e:
            print(f"[-] crt.sh failed: {e}")

        return subdomains

    def _fetch_from_hackertarget(self, domain):
        """Fetch subdomains from HackerTarget API"""
        subdomains = set()

        try:
            url = f"https://api.hackertarget.com/hostsearch/?q={domain}"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                for line in response.text.split('\n'):
                    if ',' in line:
                        subdomain = line.split(',')[0].strip()
                        if subdomain and '.' in subdomain:
                            subdomains.add(subdomain)

                print(f"[+] HackerTarget: Found {len(subdomains)} subdomains")

        except Exception as e:
            print(f"[-] HackerTarget failed: {e}")

        return subdomains

    def _try_common_subdomains(self, domain):
        """Try common subdomain names"""
        common = [
            'www', 'mail', 'ftp', 'admin', 'blog', 'shop', 'api',
            'dev', 'staging', 'test', 'app', 'portal', 'dashboard',
            'secure', 'vpn', 'remote', 'cloud', 'mobile', 'support'
        ]

        return {f"{sub}.{domain}" for sub in common}

    def _validate_subdomains(self, subdomains):
        """Validate which subdomains are actually active and get their IP addresses"""

        def check_subdomain(subdomain):
            # First, check DNS resolution and get IP address
            ip_address = None
            try:
                ip_address = socket.gethostbyname(subdomain)
            except:
                return None

            # Then check if website is accessible
            for protocol in ['https', 'http']:
                try:
                    url = f"{protocol}://{subdomain}"
                    response = requests.get(
                        url,
                        headers=self.headers,
                        timeout=8,
                        allow_redirects=True
                    )

                    if response.status_code < 500:
                        return {
                            'url': url,
                            'subdomain': subdomain,
                            'ip_address': ip_address,
                            'status': response.status_code,
                            'protocol': protocol,
                            'server': response.headers.get('Server', 'Unknown'),
                            'title': self._extract_title(response.text)
                        }
                except:
                    continue

            return None

        # Use thread pool for parallel checking
        active = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            results = executor.map(check_subdomain, subdomains)
            active = [r for r in results if r is not None]

        return active

    def _extract_title(self, html):
        """Extract page title from HTML"""
        try:
            import re
            match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()[:100]
        except:
            pass
        return "N/A"