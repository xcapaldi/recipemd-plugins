---
name: recipemd-validate
description: Validate a RecipeMD file against the spec, using the Go validator if available or falling back to the recipemd Python CLI
license: MIT
compatibility: Requires either Go 1.21+ (go run) or Python 3.11+ with uv or pipx for the fallback CLI. If none are available, manual validation can be attempted.
metadata:
    author: Xavier Capaldi
    version: 0.1.1
---

# Validate Recipe Skill

Validate a RecipeMD file and report any structural errors. Used as the final
step after recipe extraction or editing.

## Execution

Four execution paths are available. Check tool availability in order and use
the first that succeeds — do not attempt a lower-priority path if a
higher-priority one is available.

| Priority | Check | Command |
|---|---|---|
| 1 (preferred) | `go version` exits 0 | `go run github.com/xcapaldi/recipemd-validate@latest <file>` |
| 2 | `uv --version` exits 0 | `uvx recipemd <file>` |
| 3 | `pipx --version` exits 0 | `pipx run recipemd <file>` |
| 4 (last resort) | none of the above | manual validation against `references/REFERENCE.md` |

If manual validation is necessary, warn the user that results may contain
errors due to your stochastic nature.

## Instructions

### Step 1: Run the validator

Run the availability checks above and execute the appropriate command.

Go is preferred because it produces more detailed, actionable output. The
Python CLI (via uv or pipx) is functionally equivalent but may give terser
messages.

### Step 2: Interpret results

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

### Step 3: Report

Tell the user whether validation passed or failed, which validator was used,
and (on failure) what was fixed.
