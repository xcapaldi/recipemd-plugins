---
name: extract
description: Extract a recipe in RecipeMD format from another source
license: MIT
compatibility: Scraper requires Python 3.11+ with recipe-scrapers installed; run via uv, pipx, or python directly. Validator requires Go 1.21+ (invoked with go run).
---

# Extract Recipe Skill

Extract a recipe from a URL and convert it to [RecipeMD](https://recipemd.org) format.
Two modes are available:

- **normal** — verbatim copy with optional image and an attribution warning
- **cleanroom** — LLM rewrites description and instructions in a neutral tone to avoid
  attribution issues; ingredients (factual data) are kept as-is

## Scripts

| Script | Purpose |
|---|---|
| `scripts/extract.py` | Fetches a recipe URL and outputs structured JSON |

Dependencies are declared inline via PEP 723. Pick whichever runner is available:

```bash
uv run scripts/extract.py <url>          # auto-installs deps
pipx run scripts/extract.py <url>        # auto-installs deps
python scripts/extract.py <url>          # requires: pip install recipe-scrapers
```

Pass `--help` to see the full interface.

## Invocation

The user will typically say something like:

> Extract the recipe at `<url>` [in cleanroom mode]

Default mode is **normal** unless the user explicitly requests cleanroom.

---

## Step 1 — Scrape

Run the extraction script from the skill root using whichever Python runner is available:

```bash
uv run scripts/extract.py <url>
pipx run scripts/extract.py <url>
python scripts/extract.py <url>
```

On success the script prints a JSON object to **stdout**. On failure it writes a
human-readable message to **stderr** and exits non-zero — report the error to the user
and stop.

Key JSON fields:

| Field | Type | Notes |
|---|---|---|
| `title` | string | Recipe name |
| `author` | string | Original author if available |
| `description` | string | Introductory text |
| `yields` | string | e.g. `"4 servings"` |
| `image` | string | URL of the recipe image |
| `ingredients` | list[str] | Flat ingredient list |
| `ingredient_groups` | list[{purpose, ingredients}] | Grouped ingredients |
| `instructions_list` | list[str] | Steps as individual strings |
| `instructions` | string | Steps as a single block |
| `cuisine` | string | |
| `category` | string | |
| `keywords` | list[str] | |
| `host` | string | Source domain |
| `canonical_url` | string | Canonical source URL |

---

## Step 2 — Convert to RecipeMD

Use the scraped JSON and the RecipeMD specification (in `references/REFERENCE.md`) to
produce a valid RecipeMD document.

### RecipeMD structure

```
# Title

Description paragraph(s).

*tag1, tag2, tag3*

**N servings**

---

- *amount* ingredient
- *amount* ingredient

---

Instructions prose or numbered steps.
```

Rules:
- Title is an h1 (`#`).
- Description is plain paragraph(s) — omit if none available.
- Tags: a single paragraph of entirely italicised, comma-separated strings (`*a, b, c*`).
  Use `cuisine`, `category`, and `keywords` to populate tags; omit if none available.
- Yields: a single paragraph of entirely bold text (`**N servings**`); omit if none.
- First `---` separates metadata from ingredients.
- Ingredients: unordered list. Amount goes in italics at the start of the item
  (`- *1 cup* flour`). Items with no amount have no italics prefix (`- salt`).
  If `ingredient_groups` is present, use h2 headings to group them.
- Second `---` separates ingredients from instructions; omit when there are no
  instructions.
- Instructions: write as flowing prose or numbered steps — do **not** use a bulleted
  list.

### Normal mode

- Keep title, description, ingredients, and instructions **verbatim** from the scraped
  data.
- If `image` is present, embed it immediately after the title:
  ```markdown
  ![Recipe photo](<image_url>)
  ```
- Add a source blockquote at the very top of the file (before the h1):
  ```markdown
  > **Source:** [<title>](<canonical_url>) via <host>
  ```
- After writing the file, **warn the user**:
  > ⚠️ Attribution: This recipe was copied verbatim from `<canonical_url>`. Make sure
  > you have the right to store and share this content before distributing it.

### Cleanroom mode

The goal is a clean, independent document that conveys the same culinary information
without copying the original author's expression.

- Keep the **title** as-is (titles are not copyrightable).
- **Rewrite the description** in a neutral, factual, third-person tone. Remove personal
  anecdotes, first-person voice, brand references, and any phrasing that echoes the
  source. Describe what the dish is and why someone would make it.
- Keep **ingredients and amounts exactly as scraped** — quantities and ingredient names
  are factual information.
- **Rewrite the instructions** in clear, neutral imperative language (e.g.
  "Dice the onion." not "I like to dice my onion really finely!"). Each step should
  convey only the cooking action; remove all personality, asides, and first-person
  references.
- Do **not** include the source image.
- Do **not** include a source attribution block.

---

## Step 3 — Write output file

Derive a filename from the title: lowercase, spaces replaced with hyphens, non-alphanumeric
characters stripped, `.md` extension. Example: `pico-de-gallo.md`.

Write the RecipeMD content to that file in the current working directory (or a path
specified by the user).

---

## Step 4 — Validate

Delegate to the **`validate`** skill, passing the output file path.

The validate skill handles validator selection (Go preferred, uv/pipx fallback)
and will prompt you to fix any errors before reporting a final result.
