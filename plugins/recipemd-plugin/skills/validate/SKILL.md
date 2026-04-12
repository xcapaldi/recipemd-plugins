---
name: validate
description: Validate a RecipeMD file against the spec, using the Go validator if available or falling back to the recipemd Python CLI
license: MIT
compatibility: Requires either Go 1.21+ (go run) or Python 3.11+ with uv or pipx for the fallback CLI. If none are available, manual validation can be attempted.
metadata:
    author: Xavier Capaldi
    version: 0.1.0
---

# Validate Recipe Skill

Validate a RecipeMD file and report any structural errors. Used as the final
step after recipe extraction or editing.

## Instructions

### 1: Run the validator

Always try Go first — it produces more detailed, actionable output. Fall back
to the Python CLI only when Go is not available.

1. **Go** (preferred): `go run github.com/xcapaldi/recipemd-validate@latest <file>`
2. **Python via uv** (fallback): `uvx recipemd <file>`
3. **Python via pipx** (fallback): `pipx run recipemd <file>`

Check availability by running `go version`, `uv --version`, or `pipx --version`.
Use whichever is present, in that order.

If none of the runners are available, use `references/REFERENCE.md` to do a 
manual validation but be sure to warn the user you are falling back to this and
that there may be errors due to your stochastic nature.

### 2: Interpret results

- **Exit code 0 / no errors**: file is valid. Report success and the filename.
- **Errors reported**: the file has structural problems. Read each error, fix
  the RecipeMD content, and re-run. Repeat up to 3 times.

Common errors and fixes:

| Error | Fix |
|---|---|
| Missing title | Ensure first line is `# Title` |
| Ingredient not in list | Wrap each ingredient as a `- *amount* name` list item |
| Amount not in italics | Wrap the amount portion in `*…*` |
| Missing first `---` | Add a horizontal rule between yields/tags and ingredients |
| Instructions in wrong section | Move prose after the second `---` |
| Tags not italicised | Tags paragraph must be entirely `*tag1, tag2*` |
| Yields not bold | Yields paragraph must be entirely `**N servings**` |

Consult `references/REFERENCE.md` for the full format specification.

### 3: Report

Tell the user whether validation passed or failed, which validator was used,
and (on failure) what was fixed.
