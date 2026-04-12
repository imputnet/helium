# Helium i18n
This directory contains the translations for Helium browser UI strings.

## Files
- `source.gen.json` - Auto-generated list of translatable strings extracted from
                      from patches. Do not edit manually.
- `languages.json` - Map of locale codes to language names for all supported languages.
                     Do not edit, we are not adding support for additional languages
                     beyond what is already supported in Chromium.
- `translations/` - Per-language translation files.

## Translation reviewers
Your responsibility as a reviewer is to ensure the translation is the
best it can be. When reviewing translations for a specific language, focus on:
- Accuracy of the translation relative to the `source` field
- Correct preservation of `<ph>` placeholder tags
- Appropriate formality register for the language
- "Helium" and other brand names should not be translated

If you notice an error or mistranslation in any of the strings, feel free
to open a pull request to resolve it.

## Translation owners
If you are a native speaker of a particular language and would be willing to
review any changes made to its translations, you may ask to be added for the
particular language file in [CODEOWNERS](../CODEOWNERS), if there are no or
few translators for that file. This would be preferrably done in a PR related to
the file itself.

## Development
When adding strings to Helium, you might need to regenerate the source
file using `./devutils/i18n.py generate`. Do not generate machine translations
of the strings, the maintainers will take care of this.

To apply existing translations to the Chromium tree, use `utils/i18n_apply.py`.
For more instructions, see the help (`-h`) output of these scripts.

## Format
Each file in `translations/` is a JSON array of translated entries.
Entries are matched to `source.gen.json` by content (`name` + `source`),
not by position. Each entry is an object:

```json
{
  "name": "IDS_EXAMPLE_STRING",
  "source": "Original English text",
  "message": "Translated text",
  "feminine": "Feminine form (optional)",
  "masculine": "Masculine form (optional)"
}
```

The `feminine`/`masculine` fields are only present when the
translation genuinely differs by grammatical gender.
