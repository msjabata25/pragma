"""
knowledge/fetch_sources.py
One-time script to fetch all curated security docs and save them as clean
markdown files into knowledge/sources/.

Run once, commit the results, never fetch again.

Usage:
    python -m knowledge.fetch_sources
    python -m knowledge.fetch_sources --output-dir knowledge/sources
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

import httpx
from markdownify import markdownify as md

# ─────────────────────────────────────────────────────────────────────────────
# Source manifest
# Each entry: (output_path_relative_to_sources_dir, url)
# ─────────────────────────────────────────────────────────────────────────────

SOURCES: list[tuple[str, str]] = [

    # ── OWASP Cheat Sheets ───────────────────────────────────────────────────
    ("owasp/sql_injection.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html"),
    ("owasp/query_parameterization.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/Query_Parameterization_Cheat_Sheet.html"),
    ("owasp/xss_prevention.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html"),
    ("owasp/dom_xss.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html"),
    ("owasp/csrf.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html"),
    ("owasp/authentication.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html"),
    ("owasp/session_management.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html"),
    ("owasp/password_storage.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html"),
    ("owasp/cryptographic_storage.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html"),
    ("owasp/secrets_management.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html"),
    ("owasp/injection_prevention.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html"),
    ("owasp/os_command_injection.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html"),
    ("owasp/input_validation.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html"),
    ("owasp/deserialization.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html"),
    ("owasp/file_upload.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html"),
    ("owasp/ssrf.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html"),
    ("owasp/xxe.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html"),
    ("owasp/access_control.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/Access_Control_Cheat_Sheet.html"),
    ("owasp/insecure_direct_object_reference.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html"),
    ("owasp/error_handling.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html"),
    ("owasp/logging.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html"),
    ("owasp/tls.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html"),
    ("owasp/http_headers.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html"),
    ("owasp/nodejs_security.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/Nodejs_Security_Cheat_Sheet.html"),
    ("owasp/django_security.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/Django_Security_Cheat_Sheet.html"),
    ("owasp/django_rest.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/Django_REST_Framework_Cheat_Sheet.html"),
    ("owasp/java_security.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/Java_Security_Cheat_Sheet.html"),
    ("owasp/prototype_pollution.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/Prototype_Pollution_Prevention_Cheat_Sheet.html"),
    ("owasp/mass_assignment.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html"),
    ("owasp/oauth2.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/OAuth2_Cheat_Sheet.html"),
    ("owasp/jwt.md",
     "https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html"),

    # ── CWE Definitions ──────────────────────────────────────────────────────
    ("cwe/cwe79_xss.md",
     "https://cwe.mitre.org/data/definitions/79.html"),
    ("cwe/cwe89_sqli.md",
     "https://cwe.mitre.org/data/definitions/89.html"),
    ("cwe/cwe78_os_injection.md",
     "https://cwe.mitre.org/data/definitions/78.html"),
    ("cwe/cwe22_path_traversal.md",
     "https://cwe.mitre.org/data/definitions/22.html"),
    ("cwe/cwe352_csrf.md",
     "https://cwe.mitre.org/data/definitions/352.html"),
    ("cwe/cwe502_deserialization.md",
     "https://cwe.mitre.org/data/definitions/502.html"),
    ("cwe/cwe306_auth.md",
     "https://cwe.mitre.org/data/definitions/306.html"),
    ("cwe/cwe862_authz.md",
     "https://cwe.mitre.org/data/definitions/862.html"),
    ("cwe/cwe798_hardcoded_creds.md",
     "https://cwe.mitre.org/data/definitions/798.html"),
    ("cwe/cwe327_weak_crypto.md",
     "https://cwe.mitre.org/data/definitions/327.html"),
    ("cwe/cwe330_weak_random.md",
     "https://cwe.mitre.org/data/definitions/330.html"),
    ("cwe/cwe611_xxe.md",
     "https://cwe.mitre.org/data/definitions/611.html"),
    ("cwe/cwe918_ssrf.md",
     "https://cwe.mitre.org/data/definitions/918.html"),
    ("cwe/cwe94_code_injection.md",
     "https://cwe.mitre.org/data/definitions/94.html"),
    ("cwe/cwe434_file_upload.md",
     "https://cwe.mitre.org/data/definitions/434.html"),
]

# ─────────────────────────────────────────────────────────────────────────────
# HTML → Markdown cleaning
# ─────────────────────────────────────────────────────────────────────────────

# Tags to strip entirely (nav, header, footer, scripts, etc.)
_STRIP_TAGS = [
    "nav", "header", "footer", "script", "style",
    "aside", "form", "button", "svg", "img",
]

def _strip_html_tags(html: str, tags: list[str]) -> str:
    for tag in tags:
        html = re.sub(
            rf"<{tag}[\s>].*?</{tag}>",
            "",
            html,
            flags=re.DOTALL | re.IGNORECASE,
        )
    return html


def _clean_markdown(text: str) -> str:
    """Post-process markdownify output to remove noise."""
    # Collapse 3+ blank lines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Remove lines that are just link noise e.g. "[Skip to content](#...)"
    text = re.sub(r"^\[.*?\]\(#.*?\)\s*$", "", text, flags=re.MULTILINE)
    # Remove bare URL lines (navigation artifacts)
    text = re.sub(r"^https?://\S+\s*$", "", text, flags=re.MULTILINE)
    # Remove lines with only whitespace
    text = re.sub(r"^\s+$", "", text, flags=re.MULTILINE)
    return text.strip()


def html_to_markdown(html: str) -> str:
    cleaned_html = _strip_html_tags(html, _STRIP_TAGS)
    raw_md = md(
        cleaned_html,
        heading_style="ATX",       # ## style headings
        bullets="-",
        strip=["a", "img"],        # strip links and images — keep text only
    )
    return _clean_markdown(raw_md)


# ─────────────────────────────────────────────────────────────────────────────
# Fetch
# ─────────────────────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": "Mozilla/5.0 (pragma-knowledge-fetcher/1.0; security research)",
}
# Polite delay between requests (seconds)
REQUEST_DELAY = 1.5


def fetch_all(output_dir: Path, skip_existing: bool = True) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    total   = len(SOURCES)
    success = 0
    failed  = []

    with httpx.Client(headers=HEADERS, timeout=30, follow_redirects=True) as client:
        for i, (rel_path, url) in enumerate(SOURCES, 1):
            dest = output_dir / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)

            if skip_existing and dest.exists():
                print(f"  [{i}/{total}] SKIP (exists)  {rel_path}")
                success += 1
                continue

            print(f"  [{i}/{total}] Fetching  {rel_path}")
            print(f"           ← {url}")

            try:
                resp = client.get(url)
                resp.raise_for_status()
                content = html_to_markdown(resp.text)

                if len(content) < 200:
                    raise ValueError(f"Suspiciously short content ({len(content)} chars) — page may have changed")

                dest.write_text(content, encoding="utf-8")
                print(f"           ✅ {len(content):,} chars saved")
                success += 1

            except Exception as exc:
                print(f"           ❌ FAILED: {exc}")
                failed.append((rel_path, url, str(exc)))

            # Be polite — don't hammer the servers
            if i < total:
                time.sleep(REQUEST_DELAY)

    print(f"\n[pragma-knowledge] Done: {success}/{total} fetched.")

    if failed:
        print(f"\n[pragma-knowledge] {len(failed)} failure(s):")
        for rel_path, url, err in failed:
            print(f"  ✗ {rel_path}")
            print(f"    {url}")
            print(f"    {err}")
        print("\nRe-run to retry failed sources (existing files are skipped).")
        sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="pragma-fetch-sources",
        description=(
            "One-time fetch of curated security docs into knowledge/sources/. "
            "Run once, commit the .md files, never run again."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("knowledge/sources"),
        help="Where to write the .md files (default: knowledge/sources)",
    )
    parser.add_argument(
        "--refetch",
        action="store_true",
        help="Re-fetch even if the file already exists (default: skip existing)",
    )
    args = parser.parse_args()

    print(f"[pragma-knowledge] Fetching {len(SOURCES)} sources → {args.output_dir}")
    print(f"[pragma-knowledge] Delay between requests: {REQUEST_DELAY}s\n")

    fetch_all(output_dir=args.output_dir, skip_existing=not args.refetch)


if __name__ == "__main__":
    main()