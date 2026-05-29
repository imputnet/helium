# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

`kaguya-chromium` is Kaguya's **shared, platform-agnostic Chromium layer**: the quilt patchset, branding/resources, browser metadata, i18n strings, domain/name-substitution lists, and the Python tooling (`utils/`, `devutils/`) that transform a Chromium source tree into Kaguya. It is based on [ungoogled-chromium](https://github.com/ungoogled-software/ungoogled-chromium) and forked from Helium.

**No browser is built or run here, and there is no checked-in Chromium source.** This repo is consumed as a git submodule by the platform repos — [`kaguya-linux`](https://github.com/iceice666/kaguya-linux) (the active development platform) and [`kaguya-macos`](https://github.com/iceice666/kaguya-macos); a Windows repo is planned but does not exist yet — which own build orchestration, packaging, and the dev environment. When working inside `kaguya-linux`, that repo's `CLAUDE.md` also loads and describes the build/packaging pipeline; **don't duplicate it here — point to it.**

## Testing, linting, and CI

There is no browser test suite. "Testing" here means `pytest` over the Python tooling plus the patch/i18n/config linters. CI runs these via `.github/workflows/lint.yml` and Cirrus (`.cirrus.yml`). Run them locally before committing changes to tooling, patches, or i18n:

```bash
# Patch-series sanity checks — the primary gate (also run in kaguya-linux CI as `lint.py -t .`)
python3 ./devutils/lint.py

# i18n: regenerate source strings and verify no drift (CI fails on drift), then validate translations
python3 ./devutils/i18n.py generate -o /tmp/source.gen.json && diff -u ./i18n/source.gen.json /tmp/source.gen.json
python3 ./devutils/i18n_lint.py

# Config-file sanity (downloads.ini, gn flags, patch readability/dupes, list integrity)
./devutils/validate_config.py

# Patch + list validation against a real source tree (needs a checked-out Chromium at <src>)
./devutils/validate_patches.py -l <src> -v

# Format + lint + test all Python tooling at once
./devutils/check_all_code.sh
```

Run the test suites and a single test directly (note: each `pytest.ini` lives next to the code it covers, and `cd` matters because of relative `--cov` config):

```bash
./devutils/run_utils_tests.sh        # all utils/ tests
./devutils/run_devutils_tests.sh     # all devutils/ tests

# A single test — cd into the package and pass its pytest.ini explicitly:
cd utils && python3 -m pytest -c pytest.ini tests/test_patches.py::test_name
cd devutils && python3 -m pytest -c pytest.ini tests/test_validate_patches.py
```

Formatting is `yapf` with `.style.yapf` (excluding `*/third_party/*`); linting is `pylint` (`run_utils_pylint.py` / `run_devutils_pylint.py`, often run with `--hide-fixme`).

## Architecture

Two tooling trees with distinct roles:

- **`utils/`** — pipeline steps the *platform build scripts* invoke against a Chromium source tree, in roughly this order: `downloads.py` (fetch lite tarball per `downloads.ini`) or `clone.py` → `prune_binaries.py` (strip per `pruning.list`) → `patches.py apply` → `domain_substitution.py` (per `domain_substitution.list`/`domain_regex.list`) → `name_substitution.py` (Chrome/Chromium → Kaguya) → `generate_resources.py` + `kaguya_svg_icon_generator.py` → `i18n_apply.py` → `kaguya_version.py`. `deps.ini` describes post-clone downloads (search-engine data, bundled uBlock Origin). `utils/third_party/` is vendored — don't touch casually.
- **`devutils/`** — repo-maintenance and CI scripts (no source tree needed unless noted): `lint.py`/`_lint_tests.py`, `validate_config.py` and its `check_*.py` helpers, `validate_patches.py` (needs source), `i18n.py`/`i18n_lint.py`/`i18n_generate.py`, `update_lists.py` (regenerate pruning/domain-sub lists from a source tree), `update_platform_patches.py` (merge series), plus the yapf/pylint/pytest runners.

### Patches
- `patches/series` is the **authoritative apply order**. A `.patch` file is inert unless listed there. Imported/vendor groups (`upstream-fixes/`, `inox-patchset/`, `iridium-browser/`, `ungoogled-chromium/`, `bromite/`, `debian/`, `brave/`) come first; the ~196 Kaguya-owned patches under `patches/kaguya/` come last (`core/` = defaults, services, importers, privacy/update/search behavior, uBlock; `settings/` = Settings WebUI; `ui/` = chrome, layout, tabstrip/sidebar, NTP, PDF viewer, theme; `hop/` = Hop integration).
- **Don't hand-edit patch files.** Make changes in the Chromium source tree (the platform repo checks one out under `build/src`), then refresh the affected patch with `quilt`. Preserve ownership and ordering; place a new patch near related behavior in `series`, not blindly at the end. Prefer editing Kaguya-owned patches over vendor groups.

### Versioning & releases
Version = `chromium_version.txt` + `revision.txt` + `version.txt`, computed by `kaguya_version.py`. Pushing a version bump to `main` triggers `.github/workflows/release-and-tag.yml` to cut a release. Bumping `chromium_version.txt` requires refreshing the patchset and regenerating `pruning.list`/`domain_substitution.list`.

### i18n
`i18n/source.gen.json` is **generated** from translatable strings in patches — regenerate with `./devutils/i18n.py generate` after adding/changing UI strings (CI gates on drift). `i18n/languages.json` mirrors Chromium's supported locales — don't add new locales. `i18n/translations/*.json` entries are matched by content (`name` + `source`), not position; preserve `<ph>` placeholders exactly and never translate brand names. Don't machine-translate — maintainers handle that.

### Generated/ignored artifacts (don't hand-edit or commit)
`resources/generated/`, `graphify-out/`, `devutils/i18n-data/`, and `build/` are gitignored. The curated agent project map lives in `docs/project-map/` (`GRAPH_TREE.html`, `graph.html/json`, `GRAPH_REPORT.md`) — an orientation aid, generated from the repo; verify against current source.

## Conventions

- **Commits use Conventional Commits** (`feat:`, `fix:`, `docs:`, `chore:`, `build:`, …) — match recent history on this fork; `CONTRIBUTING.md` documents the same convention.
- Treat `patches/series`, `downloads.ini`, `deps.ini`, `flags.gn`, the resource manifests (`resources/*.txt`), and generated i18n/resource files as **coupled metadata** — changing one usually means checking the corresponding helper script or regenerated output.
- `flags.gn` holds default GN args; keep it sorted, no duplicates. Be especially cautious with browser-facing defaults around networking, Google-service integration, updates, extension downloading, safe browsing, telemetry, and sandbox/build-security flags — Kaguya is privacy-first, and platform packaging contracts depend on these.
- Add the Kaguya copyright header (see existing patches) when introducing new Kaguya-authored files into the Chromium tree.
- Do not use AI to author issue/PR descriptions (repo policy — `CONTRIBUTING.md`).
