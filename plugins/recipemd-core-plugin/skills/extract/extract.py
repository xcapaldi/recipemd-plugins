#!/usr/bin/env python3
"""Extract recipe data from a URL using recipe-scrapers.

Outputs a JSON object to stdout containing all available recipe fields.
Unsupported sites are handled via schema.org extraction (supported_only=False).
"""

import argparse
import json
import sys


def scrape(url: str) -> dict:
    try:
        from recipe_scrapers import scrape_html
        import urllib.request

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
            },
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode("utf-8")

        scraper = scrape_html(html, org_url=url, supported_only=False)
    except ImportError:
        print(
            json.dumps(
                {
                    "error": (
                        "recipe-scrapers is not installed. "
                        "Run: pip install recipe-scrapers"
                    )
                }
            )
        )
        sys.exit(1)
    except Exception as exc:
        print(json.dumps({"error": str(exc)}))
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

    # List fields
    list_fields = ["ingredients", "instructions_list", "keywords", "equipment"]
    for field in list_fields:
        try:
            value = getattr(scraper, field)()
            if value:
                data[field] = value
        except Exception:
            pass

    # Ingredient groups (structured)
    try:
        groups = scraper.ingredient_groups()
        if groups:
            data["ingredient_groups"] = [
                {"purpose": g.purpose, "ingredients": g.ingredients}
                for g in groups
            ]
    except Exception:
        pass

    # Nutrients dict
    try:
        nutrients = scraper.nutrients()
        if nutrients:
            data["nutrients"] = nutrients
    except Exception:
        pass

    return data


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract recipe data from a URL and output JSON."
    )
    parser.add_argument("url", help="Recipe URL to scrape")
    args = parser.parse_args()

    data = scrape(args.url)
    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
