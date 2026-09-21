import pytest

from app import config, webfetch
from app.webfetch import FetchError, Fetcher, query_page, summarize_page, validate_url


@pytest.mark.parametrize("url", [
    "http://127.0.0.1/", "http://localhost:8000/", "http://[::1]/", "http://10.0.0.5/",
    "http://192.168.1.1/", "http://169.254.169.254/latest/meta-data/", "http://2130706433/",
    "file:///etc/passwd", "ftp://example.com/", "http://user:pw@example.com/",
])
def test_blocks_unsafe_urls(url):
    with pytest.raises(FetchError):
        validate_url(url)


def test_adds_scheme_and_strips_fragment(local_ok):
    assert validate_url("example.com/a#frag") == "https://example.com/a"


def test_summary(site, local_ok):
    f = Fetcher()
    page = f.get(site + "/")
    s = summarize_page(page)
    assert s["status"] == 200 and s["title"] == "Test Site"
    assert s["meta_description"] == "A test page" and s["lang"] == "en"
    assert s["headings"]["h1"] == ["Hello"]
    assert s["images"] == {"count": 2, "missing_alt": 1, "lazy_loaded": 0}
    assert s["links"]["internal_count"] == 1 and s["links"]["external_count"] == 1
    assert "x-frame-options" in s["security_headers"]
    assert "content-security-policy" in s["missing_security_headers"]
    assert "var x=1" not in s["text_excerpt"]  # scripts stripped from visible text
    f.close()


def test_query_page_uses_cache(site, local_ok):
    f = Fetcher()
    assert f.cached(site + "/") is None
    f.get(site + "/")
    r = query_page(f.cached(site + "/"), "a[href]", "href")
    assert r["match_count"] == 2 and "/about" in r["results"]
    with pytest.raises(FetchError):
        query_page(f.cached(site + "/"), "a[[[")
    f.close()


def test_robots_disallow(site, local_ok):
    f = Fetcher()
    with pytest.raises(FetchError, match="robots.txt"):
        f.get(site + "/private")
    f.close()


def test_robots_can_be_disabled(site, local_ok, monkeypatch):
    monkeypatch.setattr(config, "RESPECT_ROBOTS", False)
    f = Fetcher()
    assert f.get(site + "/private").status == 200
    f.close()


def test_follows_redirect(site, local_ok):
    f = Fetcher()
    page = f.get(site + "/redirect")
    assert page.url.endswith("/") and len(page.redirects) == 1
    f.close()


def test_redirect_target_is_revalidated(site, monkeypatch):
    def only_first_host(host, port):
        if host != "127.0.0.1":
            raise FetchError("non-public")
    monkeypatch.setattr(webfetch, "_check_host", only_first_host)
    f = Fetcher()
    with pytest.raises(FetchError, match="non-public"):
        f.get(site + "/evil-redirect")
    f.close()


def test_body_cap_and_fetch_budget(site, local_ok, monkeypatch):
    monkeypatch.setattr(config, "MAX_BODY_BYTES", 1000)
    monkeypatch.setattr(config, "MAX_FETCHES_PER_RUN", 2)
    f = Fetcher()
    p = f.get(site + "/big")
    assert p.truncated and len(p.body) == 1000
    f.get(site + "/")
    with pytest.raises(FetchError, match="budget"):
        f.get(site + "/")
    f.close()
