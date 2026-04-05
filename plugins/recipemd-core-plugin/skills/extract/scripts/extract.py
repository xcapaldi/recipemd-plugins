#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "recipe-scrapers",
# ]
# ///
"""Extract recipe data from a URL using recipe-scrapers.

Outputs a JSON object to stdout containing all available recipe fields.
Errors are written to stderr with a non-zero exit code.

Unsupported sites are handled via schema.org extraction (supported_only=False).

Usage:
    uv run scripts/extract.py <url>
    uv run scripts/extract.py --help
"""

import argparse
import json
import sys
import urllib.error
import urllib.request


_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


def scrape(url: str) -> dict:
    try:
        from recipe_scrapers import scrape_html
    except ImportError:
        print("recipe-scrapers is not available; run via: uv run scripts/extract.py", file=sys.stderr)
        sys.exit(1)

    try:
        req = urllib.request.Request(url, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        print(f"HTTP {exc.code} fetching {url}: {exc.reason}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Failed to fetch {url}: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        scraper = scrape_html(html, org_url=url, supported_only=False)
    except Exception as exc:
        print(f"Failed to parse recipe from {url}: {exc}", file=sys.stderr)
        sys.exit(1)

    data: dict = {}

    scalar_fields = [
        "title",
        "author",
        "description",
        "yields",
        "image",
        "instructions",
        "total_time",
        "cook_time",
        "prep_time",
        "cuisine",
        "category",
        "cooking_method",
        "host",
        "canonical_url",
        "site_name",
        "language",
        "ratings",
        "ratings_count",
    ]
    for field in scalar_fields:
        try:
            value = getattr(scraper, field)()
            if value is not None and value != "" and value != []:
                data[field] = value
        except Exception:
            pass

    list_fields = ["ingredients", "instructions_list", "keywords", "equipment"]
    for field in list_fields:
        try:
            value = getattr(scraper, field)()
            if value:
                data[field] = value
        except Exception:
            pass

    try:
        groups = scraper.ingredient_groups()
        if groups:
            data["ingredient_groups"] = [
                {"purpose": g.purpose, "ingredients": g.ingredients}
                for g in groups
            ]
    except Exception:
        pass

    try:
        nutrients = scraper.nutrients()
        if nutrients:
            data["nutrients"] = nutrients
    except Exception:
        pass

    return data


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Extract recipe data from a URL and output JSON to stdout.\n"
            "Errors are written to stderr; exit code is non-zero on failure."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("url", help="Recipe page URL to scrape")
    args = parser.parse_args()

    data = scrape(args.url)
    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
