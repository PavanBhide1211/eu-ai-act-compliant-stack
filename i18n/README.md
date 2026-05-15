# i18n — Multilingual Support

Locale files and runtime patching for the compliant CV-screening demo.

## Layout

```
i18n/
├── README.md
├── locales/
│   ├── en.json
│   ├── de.json
│   ├── fr.json
│   ├── es.json
│   └── it.json
├── loader.py          # backend locale loader (used by FastAPI)
└── patch_locale.py    # CLI to add/update locales at runtime
```

## Seed locales

The seed set is **EN, DE, FR, ES, IT**. These cover the bulk of the EU/EEA addressable market for the demo's CV-screening use case. Add more locales using `patch_locale.py` — no redeploy required.

## Production note on translation quality

The seed translations are intended to demonstrate the i18n plumbing. **They have not been reviewed by professional translators.** Before production use:

- Have each locale reviewed by a native-speaker linguist familiar with HR-tech and regulatory vocabulary.
- Have the candidate-facing disclosure copy reviewed by legal counsel in each jurisdiction. Disclosure copy under Article 50 of the EU AI Act, and the equivalent under GDPR Article 14, may be subject to specific national wording requirements.
- Verify that any regulator-facing copy follows the official-language requirements of the Member State the system is registered in.

## Adding a new locale

```bash
# bootstrap a new locale from English with empty values
python i18n/patch_locale.py create nl

# edit i18n/locales/nl.json, then validate
python i18n/patch_locale.py validate nl

# the backend will pick it up on the next request (or call /i18n/reload)
```

## Updating an existing locale

```bash
python i18n/patch_locale.py set fr ui.score "Score"
python i18n/patch_locale.py validate fr
```

## File schema

Every locale file follows the same schema. Keys are dot-paths grouped by surface:

- `ui.*` — frontend UI strings.
- `panels.*` — text on the two side-by-side panels.
- `compliance.*` — labels and short descriptions for the compliance sidecar tabs.
- `disclosure.*` — Article 50 candidate-facing disclosure copy.
- `errors.*` — error messages surfaced to end users.

When validating, any key present in `en.json` but missing in a target locale is reported as a gap. The seed locales are intentionally complete relative to `en.json`.
