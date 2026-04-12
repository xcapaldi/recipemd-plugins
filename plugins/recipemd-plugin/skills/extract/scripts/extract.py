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


def scrape(url: str) -> dict:
    try:
        from recipe_scrapers import scrape_me
    except ImportError:
        print("recipe-scrapers is not available; run via: uv run scripts/extract.py", file=sys.stderr)
        sys.exit(1)

    try:
        scraper = scrape_me(url)
    except Exception as exc:
        print(f"Failed to scrape {url}: {exc}", file=sys.stderr)
        sys.exit(1)

    # to_json() returns a dict, not a JSON string, despite the name
    print(json.dumps(scraper.to_json(), indent=2, ensure_ascii=False))


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

    scrape(args.url)


if __name__ == "__main__":
    main()
