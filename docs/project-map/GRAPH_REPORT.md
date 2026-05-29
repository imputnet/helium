# Graph Report - .  (2026-05-23)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1088 nodes · 1468 edges · 171 communities (150 shown, 21 thin omitted)
- Extraction: 82% EXTRACTED · 18% INFERRED · 0% AMBIGUOUS · INFERRED: 259 edges (avg confidence: 0.81)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0c025d3f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 144|Community 144]]
- [[_COMMUNITY_Community 150|Community 150]]
- [[_COMMUNITY_Community 151|Community 151]]
- [[_COMMUNITY_Community 152|Community 152]]
- [[_COMMUNITY_Community 153|Community 153]]
- [[_COMMUNITY_Community 154|Community 154]]
- [[_COMMUNITY_Community 155|Community 155]]
- [[_COMMUNITY_Community 156|Community 156]]
- [[_COMMUNITY_Community 157|Community 157]]
- [[_COMMUNITY_Community 158|Community 158]]
- [[_COMMUNITY_Community 159|Community 159]]
- [[_COMMUNITY_Community 161|Community 161]]
- [[_COMMUNITY_Community 162|Community 162]]
- [[_COMMUNITY_Community 164|Community 164]]
- [[_COMMUNITY_Community 169|Community 169]]
- [[_COMMUNITY_Community 170|Community 170]]

## God Nodes (most connected - your core abstractions)
1. `get_logger()` - 55 edges
2. `path()` - 44 edges
3. `Contributing to Kaguya` - 21 edges
4. `Kaguya` - 20 edges
5. `Bump revision and make PR step` - 17 edges
6. `Kaguya Chromium Codebase Notes` - 17 edges
7. `DownloadInfo` - 14 edges
8. `UnidiffParseError` - 12 edges
9. `Hunk` - 12 edges
10. `extract_tar_file()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `path()`  [INFERRED]
  utils/generate_resources.py → devutils/third_party/unidiff/patch.py
- `Project Version 0` --conceptually_related_to--> `Kaguya`  [AMBIGUOUS]
  version.txt → README.md
- `Kaguya` --references--> `Kaguya App Icon`  [EXTRACTED]
  README.md → resources/branding/app_icon/raw.png
- `Bump revision and make PR step` --calls--> `devutils/set_quilt_vars.sh`  [EXTRACTED]
  .github/actions/bump-platform/action.yml → kaguya-chromium/devutils/set_quilt_vars.sh
- `i18n job` --calls--> `devutils/i18n.py`  [EXTRACTED]
  .github/workflows/lint.yml → devutils/i18n.py

## Communities (171 total, 21 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.02
Nodes (81): af, am, ar, as, az, be, bg, bn (+73 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (40): BaseException, validate_with_source_task, main(), Combines and checks if the the downloads.ini files provided are valid.      down, ExtractorEnum, PlatformEnum, Enum for platforms that need distinction for certain functionality, Enum for extraction binaries (+32 more)

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (47): brave Vendor Patch Group, bromite Vendor Patch Group, chromium_version.txt Chromium Base Version, CONTRIBUTING.md Contributor Policy and Patch Conventions, Kaguya Core Patches, debian Vendor Patch Group, deps.ini Post-Clone Downloads, devutils Development and Validation Scripts (+39 more)

### Community 3 - "Community 3"
Cohesion: 0.08
Nodes (19): list, object, Exception when parsing the unified diff data., UnidiffParseError, _convert_string(), from_string(), Hunk, Line (+11 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (40): do_substitution(), do_unsubstitution(), get_substitutable_files(), main(), maybe_make_tarball(), parse_args(), Replaces strings in an .xtb file, and returns     ((arcname, original_content)), Reverts name substitutions from the backup tarball (+32 more)

### Community 5 - "Community 5"
Cohesion: 0.09
Nodes (32): Returns True if the DEPS file passes validation; False otherwise, And, _callable_str(), Const, _dict_key_priority(), Forbidden, Optional, Or (+24 more)

### Community 6 - "Community 6"
Cohesion: 0.08
Nodes (32): Chromium, Chromium Source Tree, Chromium Style and Conventions, Clean Commit History, Contributing to Kaguya, Development Tooling, Git Commit Titles, GitHub (+24 more)

### Community 7 - "Community 7"
Cohesion: 0.08
Nodes (31): Brand Names Rule, Brevity Rule, Browser UI Strings, context Field, DNS, feminine Field, Formal Register, Gendered Variants (+23 more)

### Community 8 - "Community 8"
Cohesion: 0.09
Nodes (26): Chromium Version 148.0.7778.178, Credits, Development, Kaguya repos, License, Other Chromium browsers, Platform packaging and tooling, Web services and Kaguya components (+18 more)

### Community 9 - "Community 9"
Cohesion: 0.08
Nodes (24): code:json ({), Development, Files, Format, Translation owners, Translation reviewers, Translation data, Locale ca (+16 more)

### Community 10 - "Community 10"
Cohesion: 0.08
Nodes (24): actions/checkout v4, GitHub CLI gh, i18n-no-notify skip marker, i18n/translations directory, Pull request event, Translation review requested comment marker, Notify translation owners workflow, Shared Chromium patch metadata (+16 more)

### Community 11 - "Community 11"
Cohesion: 0.18
Nodes (24): str, get_logger(), Gets the named logger, Parses an INI file located at path          Raises schema.SchemaError if validat, extract_tar_file(), _extract_tar_with_7z(), _extract_tar_with_python(), _extract_tar_with_tar() (+16 more)

### Community 12 - "Community 12"
Cohesion: 0.11
Nodes (24): apply_language(), apply_translations(), build_xtb_index(), find_parent_grd(), get_id(), get_parent_grd(), insert_into_xtb(), main() (+16 more)

### Community 13 - "Community 13"
Cohesion: 0.13
Nodes (22): build/src, .github/bump-hook.sh, Bump platform revision, Bump revision and make PR step, Clear disk space step, build/download_cache, get_version function, gh CLI (+14 more)

### Community 14 - "Community 14"
Cohesion: 0.11
Nodes (10): code_check_task, Cirrus CI Configuration, validate_config_task, main(), ChangeDir, main(), Changes directory to path in with statement, Runs Pylint. Returns a boolean indicating success (+2 more)

### Community 15 - "Community 15"
Cohesion: 0.12
Nodes (20): clone(), main(), Clones, downloads, and generates the required sources, add_common_params(), Adds common command line arguments to a parser., main(), _archive_callback(), create_archive() (+12 more)

### Community 16 - "Community 16"
Cohesion: 0.14
Nodes (20): build_payload(), fill_prompt(), find_untranslated(), fixup_json(), llm_chat(), load_existing(), parse_response(), Fill in the language placeholders in a prompt template. (+12 more)

### Community 17 - "Community 17"
Cohesion: 0.14
Nodes (15): main(), _apply_file_unidiff(), _dry_check_patched_file(), _get_required_files(), _load_all_patches(), main(), Applies the unidiff.PatchedFile to the source files under testing, Run "patch --dry-check" on a unidiff.PatchedFile for diagnostics (+7 more)

### Community 18 - "Community 18"
Cohesion: 0.14
Nodes (19): actions/checkout@v4, cirruslabs/cirrus-action, cirrus job, cirrus workflow, actions/checkout@v4, actions/setup-python@v5, devutils/i18n.py, devutils/lint.py (+11 more)

### Community 19 - "Community 19"
Cohesion: 0.12
Nodes (18): Blank Issues Disabled, Issue Template Configuration, Additional Context Field, AI Description Restriction, Permanent Ban Policy, Existing Issue Search Requirement, Feature Request, Feature Request Template (+10 more)

### Community 20 - "Community 20"
Cohesion: 0.18
Nodes (16): _apply_callback(), apply_patches(), _copy_files(), dry_run_check(), find_and_check_patch(), _find_patch_from_env(), _find_patch_from_which(), generate_patches_from_series() (+8 more)

### Community 21 - "Community 21"
Cohesion: 0.19
Nodes (14): main(), Checks if GN flags are sorted and not duplicated.      gn_flags_path is a pathli, check_patch_readability(), check_series_duplicates(), check_unused_patches(), main(), Returns a generator over the entries in the series file      patches_dir is a pa, Check if the patches from iterable patch_path_iter are readable.         Patches (+6 more)

### Community 22 - "Community 22"
Cohesion: 0.17
Nodes (13): _get_gitiles_commit_before_date(), _get_gitiles_git_log_date(), _get_last_chromium_modification(), _get_requests_session(), gn_version(), Returns the last modification date of the chromium-browser-official tar file, Helper for _get_gitiles_git_log_date, Returns the hexadecimal hash of the closest commit before target_datetime (+5 more)

### Community 23 - "Community 23"
Cohesion: 0.15
Nodes (15): _deps_var(), _download_googlesource_file(), _download_source_file(), _get_child_deps_tree(), _get_target_file_deps_node(), _NotInRepoError, _parse_deps(), Return a function that implements DEPS's Var() function (+7 more)

### Community 24 - "Community 24"
Cohesion: 0.15
Nodes (11): compute_lists(), _dir_empty(), main(), Tracks unused prefixes and patterns, Logs unused patterns and prefixes          Returns True if there are unused patt, Returns True if the directory is empty; False otherwise      path is a pathlib.P, Compute the binary pruning and domain substitution lists of the source tree., UnusedPatterns (+3 more)

### Community 25 - "Community 25"
Cohesion: 0.15
Nodes (9): Test check_series_duplicates, Test _dry_check_patched_file, test_test_patches(), get_running_platform(), Returns a PlatformEnum value indicating the platform that utils is running on., Sets logging level based on command line arguments it receives, Sets logging level of logger and all its handlers, set_logging_level() (+1 more)

### Community 26 - "Community 26"
Cohesion: 0.21
Nodes (11): apply_substitution(), _callback(), Validation of file index and hashes against the source tree.         Updates cac, Context manager to set the timestamp of the path to plus or     minus a fixed de, Substitute domains in source_tree with files and substitutions,         and save, Revert domain substitution on source_tree using the pre-domain         substitut, Perform domain substitution on path and add it to the domain substitution cache., revert_substitution() (+3 more)

### Community 27 - "Community 27"
Cohesion: 0.22
Nodes (12): extract_strings(), extract_strings_from_hunk(), get_patch_paths(), get_relevant_patches(), prep_platform_repos(), Generate strings to be translated for all grit strings in patches., Generate the base source strings JSON from patches., Clone and update platform repos into the given directory. (+4 more)

### Community 28 - "Community 28"
Cohesion: 0.21
Nodes (12): _check_regex_match(), compute_lists_proc(), _is_binary(), # NOTE: Domain substitution path prefix exclusion has precedence over inclusion, Returns True if the data seems to be binary data (i.e. not human readable); Fals, Returns True if a path should be pruned from the source tree; False otherwise, Returns True if a regex pattern matches a file; False otherwise      file_path i, Returns True if a path should be domain substituted in the source tree; False ot (+4 more)

### Community 29 - "Community 29"
Cohesion: 0.29
Nodes (11): _dir_empty(), main(), merge_platform_patches(), _parse_series_metadata(), Undo merge_platform_patches(), adding any new patches from series.merged as nece, Prepends prepend_patches_dir into platform_patches_dir      Returns True if succ, Returns True if the directory exists and is empty; False otherwise, Moves a list of sorted files back to their original location,     removing empty (+3 more)

### Community 30 - "Community 30"
Cohesion: 0.29
Nodes (11): Bug Report, Chrome, Kaguya, kaguya://settings/help, Linux, macOS, relevant repository, root kaguya repo (+3 more)

### Community 31 - "Community 31"
Cohesion: 0.31
Nodes (9): a_all_patches_in_tree_are_in_series(), b_all_patches_have_meaningful_contents(), b_all_patches_have_no_trailing_whitespace(), c_all_new_files_have_license_header(), c_all_new_headers_have_correct_guard(), d_no_whitespace_only_changes(), _init(), _read_patch() (+1 more)

### Community 32 - "Community 32"
Cohesion: 0.18
Nodes (10): LC_ALL, QUILT_COLORS, QUILT_DIFF_ARGS, QUILT_DIFF_OPTS, QUILT_PATCH_OPTS, QUILT_PATCHES, QUILT_PATCHES_ARGS, QUILT_PUSH_ARGS (+2 more)

### Community 33 - "Community 33"
Cohesion: 0.22
Nodes (10): astroid 2.14.2, Debian Bookworm Python Packages, httplib2 0.20.4, pillow 11.3.0, pylint 2.16.2, pytest 7.2.1, pytest-cov 4.0.0, Python Requirements (+2 more)

### Community 34 - "Community 34"
Cohesion: 0.20
Nodes (10): _get_files_under_test(), _initialize_deps_tree(), Initializes and returns a dependency tree for DEPS files      The DEPS tree is a, Retrieves all file paths in file_iter from Google      file_iter is an iterable, Retrieves all file paths in file_iter from the local source tree      file_iter, Helper for main to get files_under_test      Exits the program if --cache-remote, _retrieve_local_files(), _retrieve_remote_files() (+2 more)

### Community 35 - "Community 35"
Cohesion: 0.29
Nodes (9): append_version(), check_existing_version(), get_version_part(), main(), parse_args(), Gets the (first) digit representing a part of     the version from a particular, Appends a version part to the chromium VERSION file, Verifies that the version has not yet been added to the build tree (+1 more)

### Community 36 - "Community 36"
Cohesion: 0.22
Nodes (9): _get_dep_value_url(), _modify_file_lines(), _PatchValidationError, _process_deps_entries(), Helper for _process_deps_entries, Helper for _get_child_deps_tree, Helper for _apply_file_unidiff, Raised when patch validation fails (+1 more)

### Community 37 - "Community 37"
Cohesion: 0.46
Nodes (8): generated/product_icon/128x128.png, generated/product_icon/24x24.png, generated/product_icon/256x256.png, generated/product_icon/32x32.png, generated/product_icon/48x48.png, generated/product_icon/64x64.png, branding/app_icon/raw.png, Resource generation manifest

### Community 38 - "Community 38"
Cohesion: 0.36
Nodes (7): _callback(), prune_dirs(), prune_files(), _prune_path(), Delete files under unpack_root listed in prune_list. Returns an iterable of unre, Delete files and directories in path.      path is a pathlib.Path to the directo, Delete all files and directories in pycache and CONTINGENT_PATHS directories.

### Community 39 - "Community 39"
Cohesion: 0.38
Nodes (7): Product Icon 128x128, Product Icon 16x16, Product Icon 24x24, Product Icon 256x256, Product Icon 32x32, Product Icon 48x48, Product Icon 64x64

### Community 40 - "Community 40"
Cohesion: 0.47
Nodes (4): breakKey(), clear(), fs, stripURLs()

### Community 41 - "Community 41"
Cohesion: 0.40
Nodes (4): _DepsNodeVisitor, Override Call syntax handling, Raised when unexpected syntax is used in DEPS, _UnexpectedSyntaxError

### Community 42 - "Community 42"
Cohesion: 0.33
Nodes (6): Favicon Conflicts 32, Favicon Flags 32, Favicon Management 16, Favicon Management 32, Favicon Plugins 32, Favicon Settings 32

### Community 43 - "Community 43"
Cohesion: 0.47
Nodes (6): Appropriate security vulnerability reporting channel, Blank issue template, Issue submission checkbox confirmation, Permanent ban from interacting with organization, Predefined issue categories, Security vulnerability

### Community 44 - "Community 44"
Cohesion: 0.50
Nodes (4): main(), parse_args(), Parses the CLI arguments., CLI entrypoint for executing tests

### Community 45 - "Community 45"
Cohesion: 0.40
Nodes (3): _FallbackRepoManager, Retrieves fallback repos and caches data needed for determining repos, Helper for _download_source_file          It returns a new (repo_url, version, n

### Community 46 - "Community 46"
Cohesion: 0.40
Nodes (4): main(), Scales the square image to provided size and saves it, Parses the resource list and generates resources     for each valid line, scale_image()

### Community 47 - "Community 47"
Cohesion: 0.40
Nodes (4): code:json ({), Input, Output, Rules

### Community 48 - "Community 48"
Cohesion: 0.50
Nodes (3): _callback(), make_domain_substitution_script(), Generate a standalone shell script (which uses Perl) that performs         domai

### Community 49 - "Community 49"
Cohesion: 0.50
Nodes (4): actions/stale@v6, stale job, need info label, Close stale issues and PRs workflow

### Community 50 - "Community 50"
Cohesion: 0.67
Nodes (3): copy_resources(), main(), Handles copying resources from the source tree into the build     tree based on

### Community 51 - "Community 51"
Cohesion: 0.67
Nodes (3): domain_regex.list Domain Replacement Patterns, Domain Replacement Tooling, domain_substitution.list Domain Substitutions

### Community 54 - "Community 54"
Cohesion: 0.67
Nodes (3): Product Logo 200, Product Logo, Product Logo White 200

### Community 55 - "Community 55"
Cohesion: 1.00
Nodes (3): Product Logo 22 Mono, Product Logo, Product Logo White

## Ambiguous Edges - Review These
- `Favicon History 16` → `Favicon Bookmarks 16`  [AMBIGUOUS]
  resources/favicons/favicon_bookmarks_16.png · relation: conceptually_related_to
- `Project Version 0` → `Kaguya`  [AMBIGUOUS]
  version.txt · relation: conceptually_related_to

## Knowledge Gaps
- **245 isolated node(s):** `af`, `am`, `ar`, `as`, `az` (+240 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Favicon History 16` and `Favicon Bookmarks 16`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Project Version 0` and `Kaguya`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `path()` connect `Community 17` to `Community 1`, `Community 3`, `Community 4`, `Community 11`, `Community 12`, `Community 14`, `Community 15`, `Community 20`, `Community 21`, `Community 23`, `Community 25`, `Community 26`, `Community 27`, `Community 28`, `Community 29`, `Community 34`, `Community 36`, `Community 38`, `Community 44`, `Community 46`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Why does `get_logger()` connect `Community 11` to `Community 1`, `Community 34`, `Community 5`, `Community 38`, `Community 45`, `Community 15`, `Community 17`, `Community 20`, `Community 21`, `Community 22`, `Community 23`, `Community 24`, `Community 25`, `Community 26`, `Community 28`, `Community 29`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Are the 53 inferred relationships involving `str` (e.g. with `merge_platform_patches()` and `_dir_empty()`) actually correct?**
  _`str` has 53 INFERRED edges - model-reasoned connections that need verification._
- **Are the 52 inferred relationships involving `get_logger()` (e.g. with `merge_platform_patches()` and `_rename_files_with_dirs()`) actually correct?**
  _`get_logger()` has 52 INFERRED edges - model-reasoned connections that need verification._
- **Are the 43 inferred relationships involving `path()` (e.g. with `_rename_files_with_dirs()` and `main()`) actually correct?**
  _`path()` has 43 INFERRED edges - model-reasoned connections that need verification._