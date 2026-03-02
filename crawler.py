import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

HEADERS = {"User-Agent": "Mozilla/5.0"}


def is_internal(base, link):
    return urlparse(base).netloc == urlparse(link).netloc


def crawl_site(start_url, max_pages=10):
    visited = set()
    to_visit = [start_url]
    pages_data = []

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)

        if url in visited:
            continue
        visited.add(url)

        try:
            r = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)

            # Skip non-HTML responses
            if 'text/html' not in r.headers.get('Content-Type', ''):
                continue

            soup = BeautifulSoup(r.text, "html.parser")

            forms = soup.find_all("form")
            inputs = soup.find_all("input")
            scripts = soup.find_all("script")
            links = soup.find_all("a", href=True)

            pages_data.append({
                "url": url,
                "forms": len(forms),
                "inputs": len(inputs),
                "scripts": len(scripts),
                "has_password_field": any(
                    inp.get("type") == "password" for inp in inputs
                ),
                "has_external_scripts": any(
                    "http" in s.get("src", "") for s in scripts
                )
            })

            # Only follow internal links
            for link in links:
                try:
                    href = urljoin(url, link["href"])
                    # Clean fragment and only add if internal
                    href = href.split("#")[0]
                    if href and is_internal(start_url, href) and href not in visited:
                        to_visit.append(href)
                except:
                    continue

        except Exception as e:
            print(f"[-] Error crawling {url}: {e}")
            continue

    return pages_data