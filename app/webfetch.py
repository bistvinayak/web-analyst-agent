"""Safe web access for the agent.

The agent fetches URLs on a user's behalf, so every request goes through
`Fetcher.get`, which:
  * allows only http/https and refuses URLs with embedded credentials
  * resolves the host and refuses private, loopback, link-local and reserved addresses
  * follows redirects manually and re-validates every hop
  * caps body size (after decompression), redirect count, timeout and fetches per run
  * honors robots.txt (configurable)

Known limit: DNS is resolved once for validation and again by the HTTP client, so a
hostile DNS server could in theory answer differently the second time (DNS rebinding).
Run the service in a network with no route to internal systems if that matters to you.
"""
import ipaddress
import re
import socket
import time
import urllib.robotparser
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse, urlunparse

import httpx
from bs4 import BeautifulSoup

from . import config


class FetchError(Exception):
    """A fetch was refused or failed. The message is safe to show to the model."""


@dataclass
class Page:
    url: str
    status: int
    headers: dict
    content_type: str
    body: bytes
    truncated: bool
    elapsed_ms: int
    redirects: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return self.body.decode(_charset(self.content_type), errors="replace")

    @property
    def is_html(self) -> bool:
        return "html" in self.content_type or self.text.lstrip()[:15].lower().startswith(("<!doctype", "<html"))


def _charset(content_type: str) -> str:
    m = re.search(r"charset=([\w-]+)", content_type or "", re.I)
    return m.group(1) if m else "utf-8"


def validate_url(url: str) -> str:
    """Return a normalized URL, or raise FetchError if it should not be fetched."""
    if not isinstance(url, str) or not url.strip():
        raise FetchError("url is required.")
    url = url.strip()
    if "://" not in url:
        url = "https://" + url
    parts = urlparse(url)
    if parts.scheme not in ("http", "https"):
        raise FetchError("Only http and https URLs can be fetched.")
    if not parts.hostname:
        raise FetchError("URL has no host.")
    if parts.username or parts.password:
        raise FetchError("URLs with embedded credentials are not allowed.")
    try:
        port = parts.port
    except ValueError:
        raise FetchError("URL has an invalid port.")
    if not config.ALLOW_PRIVATE_HOSTS:
        _check_host(parts.hostname, port or (443 if parts.scheme == "https" else 80))
    return urlunparse(parts._replace(fragment=""))


def _check_host(host: str, port: int) -> None:
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror:
        raise FetchError(f"Could not resolve host '{host}'.")
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if not ip.is_global:
            raise FetchError(f"Refusing to fetch '{host}': it resolves to a non-public address.")


class Fetcher:
    """Per-run fetcher with a fetch budget and a small page cache."""

    def __init__(self):
        self._client = httpx.Client(
            follow_redirects=False,
            timeout=httpx.Timeout(config.FETCH_TIMEOUT),
            headers={"User-Agent": config.USER_AGENT, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"},
        )
        self.fetch_count = 0
        self._cache: dict[str, Page] = {}
        self._robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}

    def close(self) -> None:
        self._client.close()

    # -- low level ---------------------------------------------------------

    def _request(self, url: str) -> Page:
        chain: list[str] = []
        started = time.monotonic()
        for _ in range(config.MAX_REDIRECTS + 1):
            url = validate_url(url)
            try:
                with self._client.stream("GET", url) as r:
                    if r.is_redirect and r.headers.get("location"):
                        chain.append(url)
                        url = urljoin(url, r.headers["location"])
                        continue
                    body = bytearray()
                    truncated = False
                    for chunk in r.iter_bytes():
                        body.extend(chunk)
                        if len(body) > config.MAX_BODY_BYTES:
                            del body[config.MAX_BODY_BYTES :]
                            truncated = True
                            break
                    return Page(
                        url=url,
                        status=r.status_code,
                        headers={k.lower(): v for k, v in r.headers.items()},
                        content_type=r.headers.get("content-type", ""),
                        body=bytes(body),
                        truncated=truncated,
                        elapsed_ms=int((time.monotonic() - started) * 1000),
                        redirects=chain,
                    )
            except httpx.TimeoutException:
                raise FetchError(f"Timed out fetching {url}.")
            except httpx.HTTPError as e:
                raise FetchError(f"Network error fetching {url}: {type(e).__name__}.")
        raise FetchError(f"Too many redirects (more than {config.MAX_REDIRECTS}).")

    def _robots_for(self, url: str):
        parts = urlparse(url)
        origin = f"{parts.scheme}://{parts.netloc}"
        if origin not in self._robots:
            rp = urllib.robotparser.RobotFileParser()
            try:
                page = self._request(origin + "/robots.txt")
                if page.status == 200:
                    rp.parse(page.text.splitlines())
                    self._robots[origin] = rp
                else:
                    self._robots[origin] = None  # no usable robots.txt: allow
            except FetchError:
                self._robots[origin] = None
        return self._robots[origin]

    # -- public ------------------------------------------------------------

    def get(self, url: str, *, check_robots: bool = True) -> Page:
        url = validate_url(url)
        if config.RESPECT_ROBOTS and check_robots and not url.rstrip("/").endswith("/robots.txt"):
            rp = self._robots_for(url)
            if rp is not None and not rp.can_fetch(config.USER_AGENT, url):
                raise FetchError("robots.txt disallows fetching this URL. Do not work around it; report it as a limitation.")
        if self.fetch_count >= config.MAX_FETCHES_PER_RUN:
            raise FetchError(
                f"Fetch budget of {config.MAX_FETCHES_PER_RUN} requests reached. "
                "Stop fetching and write the report from what you have."
            )
        self.fetch_count += 1
        page = self._request(url)
        self._cache[page.url] = page
        self._cache[url] = page
        return page

    def cached(self, url: str) -> Page | None:
        try:
            return self._cache.get(validate_url(url))
        except FetchError:
            return None


# -- HTML analysis ---------------------------------------------------------

SECURITY_HEADERS = (
    "strict-transport-security",
    "content-security-policy",
    "x-frame-options",
    "x-content-type-options",
    "referrer-policy",
    "permissions-policy",
    "cross-origin-opener-policy",
    "cross-origin-resource-policy",
)
OTHER_HEADERS = ("server", "x-powered-by", "cache-control", "content-encoding", "content-language", "via", "x-robots-tag")


def _cookie_summary(headers: dict) -> list[str] | None:
    raw = headers.get("set-cookie")
    if not raw:
        return None
    out = []
    for cookie in re.split(r",\s*(?=[^;,=\s]+=)", raw):
        name = cookie.split("=", 1)[0].strip()
        flags = [f for f in ("secure", "httponly", "samesite") if f in cookie.lower()]
        out.append(f"{name} [{', '.join(flags) or 'no flags'}]")
    return out


def summarize_page(page: Page, *, max_links: int = 60, max_text: int = 3000) -> dict:
    """Structured summary of a fetched page. Body text is untrusted content."""
    summary: dict = {
        "url": page.url,
        "status": page.status,
        "content_type": page.content_type,
        "size_bytes": len(page.body),
        "body_truncated": page.truncated,
        "elapsed_ms": page.elapsed_ms,
        "redirect_chain": page.redirects,
        "security_headers": {h: page.headers[h] for h in SECURITY_HEADERS if h in page.headers},
        "missing_security_headers": [h for h in SECURITY_HEADERS[:6] if h not in page.headers],
        "other_headers": {h: page.headers[h] for h in OTHER_HEADERS if h in page.headers},
        "cookies": _cookie_summary(page.headers),
    }
    if not page.is_html:
        summary["text_excerpt"] = page.text[:max_text]
        return summary

    soup = BeautifulSoup(page.text, "html.parser")
    host = urlparse(page.url).netloc

    def meta(**attrs):
        tag = soup.find("meta", attrs=attrs)
        return tag.get("content", "").strip() if tag else None

    html_tag = soup.find("html")
    canonical = soup.find("link", rel="canonical")
    summary.update(
        {
            "title": soup.title.get_text(strip=True) if soup.title else None,
            "lang": html_tag.get("lang") if html_tag else None,
            "meta_description": meta(name="description"),
            "meta_robots": meta(name="robots"),
            "viewport": meta(name="viewport"),
            "canonical": canonical.get("href") if canonical else None,
            "open_graph": {t["property"]: t.get("content", "")[:200] for t in soup.find_all("meta", property=re.compile("^og:"))},
            "twitter_card": meta(name="twitter:card"),
            "headings": {f"h{n}": [h.get_text(" ", strip=True)[:120] for h in soup.find_all(f"h{n}")][:15] for n in (1, 2, 3)},
            "json_ld_present": bool(soup.find("script", type="application/ld+json")),
        }
    )

    internal, external = [], []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        full = urljoin(page.url, href)
        entry = {"href": full, "text": a.get_text(" ", strip=True)[:80]}
        (internal if urlparse(full).netloc == host else external).append(entry)
    summary["links"] = {
        "internal_count": len(internal),
        "external_count": len(external),
        "internal_sample": internal[:max_links],
        "external_sample": external[:15],
    }

    images = soup.find_all("img")
    scripts = soup.find_all("script", src=True)
    summary["images"] = {
        "count": len(images),
        "missing_alt": sum(1 for i in images if not i.get("alt")),
        "lazy_loaded": sum(1 for i in images if i.get("loading") == "lazy"),
    }
    summary["scripts"] = {
        "external_count": len(scripts),
        "inline_count": len(soup.find_all("script", src=False)),
        "external_hosts": sorted({urlparse(urljoin(page.url, s["src"])).netloc for s in scripts})[:20],
    }
    summary["stylesheets"] = len(soup.find_all("link", rel="stylesheet"))
    summary["forms"] = len(soup.find_all("form"))

    for tag in soup(["script", "style", "noscript", "template"]):
        tag.decompose()
    text = soup.get_text(" ", strip=True)
    summary["word_count"] = len(text.split())
    summary["text_excerpt"] = text[:max_text]
    return summary


def query_page(page: Page, selector: str, attribute: str | None = None, limit: int = 30) -> dict:
    """Run a CSS selector over a fetched HTML page."""
    if not page.is_html:
        raise FetchError("That resource is not HTML, so it cannot be queried with a CSS selector.")
    soup = BeautifulSoup(page.text, "html.parser")
    try:
        found = soup.select(selector)
    except Exception:
        raise FetchError(f"Invalid CSS selector: {selector!r}")
    limit = max(1, min(int(limit or 30), 100))
    items = []
    for el in found[:limit]:
        items.append(el.get(attribute) if attribute else el.get_text(" ", strip=True)[:300])
    return {"url": page.url, "selector": selector, "match_count": len(found), "results": items}
