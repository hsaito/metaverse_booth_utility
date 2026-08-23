# Metaverse Booth Utility

Metaverse Booth Utility is a Blender add-on for quickly generating a booth reference frame and front-direction arrow from preset definitions.

## Features
- Sidebar UI in 3D View (`Metaverse` tab)
- Event -> variant -> type preset selection
- `Show legacy` toggle to include/exclude legacy presets
- Add-on preference `Default Show Legacy` (Edit -> Preferences -> Add-ons) with immediate apply to open scenes
- UI labels follow Blender UI language (`English`, `Japanese`, `Spanish`)
- Auto-filled booth dimensions from JSON presets
- Front-axis preview and generation support (`x+`, `x-`, `y+`, `y-`, `z+`, `z-`)
- Generated helper objects are grouped in `Metaverse Booth Utility Generated` collection
- One-click removal of generated helper objects
- Collapsible human-model tools for adding simple procedural box-shaped people
- Per-model height control with bulk deletion for generated human models

## Requirements
- Blender 3.6+

## Installation
1. Download a release zip or package this repository.
2. In Blender, open Edit -> Preferences -> Add-ons.
3. Click Install..., then select the zip file.
4. Enable Metaverse Booth Utility.
5. Open the 3D View sidebar and select the `Metaverse` tab.

## Usage
1. Pick Event, Variant, and Type.
2. (Optional) Enable `Show legacy` to include legacy-marked entries.
3. (Optional) Open `Advanced` to tweak width/depth/height/front axis.
4. Click `Generate` to create helper objects:
    - `Booth Frame Reference`
    - `Booth Front Arrow`
   The helper objects are created in `Metaverse Booth Utility Generated` collection.
5. Click `Remove Generated` to clean up generated helpers.
   If the generated collection is empty afterward, it is also removed.
6. Open `Human Models` to add simple procedural human models at the 3D cursor position.
   Use the height slider to adjust their size before pressing `Add Human`.
   `Delete All Humans` removes every generated human model from the scene.

Behavior notes:
- `Reset` clears current Event/Variant/Type selection and preview state back to the initial prompt (`Select Event`, `Select a preset to preview`).
- Toggling `Show legacy` performs the same selection reset behavior to avoid invalid/hidden selection states.
- `Default Show Legacy` can be set in Add-on Preferences and is applied live to all open scenes.

## Preset JSON
Presets are loaded from `metaverse_booth_utility/defaults.json`.

Structure overview:
- `events[]`
- `events[].name`
- `events[].name_i18n` (optional localized label map)
- `events[].legacy` (optional boolean)
- `events[].variants[]`
- `events[].variants[].name`
- `events[].variants[].name_i18n` (optional localized label map)
- `events[].variants[].legacy` (optional boolean)
- `events[].variants[].types[]`
- `events[].variants[].types[].name`
- `events[].variants[].types[].name_i18n` (optional localized label map)
- `events[].variants[].types[].legacy` (optional boolean)
- `events[].variants[].types[].width_m`
- `events[].variants[].types[].depth_m`
- `events[].variants[].types[].height_m`
- `events[].variants[].types[].front_axis`

Legacy behavior:
- If an `event` is marked `legacy: true`, all contained variants/types are treated as legacy unless overridden by explicit fields in descendants.
- If a `variant` is marked `legacy: true`, contained types are treated as legacy unless a type explicitly sets its own `legacy`.
- If a `type` is marked `legacy: true`, only that type is legacy.
- Legacy entries are hidden unless `Show legacy` is enabled.

Localization behavior:
- `name` is always the canonical/fallback English key used internally.
- UI display name is chosen based on Blender language.
- `name_i18n` accepts arbitrary language/locale keys, for example `ja`, `es`, `ja-JP`, `en-GB`.
- If no language-specific key is found, the add-on falls back to `name`.

Schema:
- `metaverse_booth_utility/defaults.schema.json` validates this format.
- `defaults.json` includes `$schema` for editor-assisted validation.

Example:

```json
{
   "events": [
      {
         "name": "Virtual Market",
         "name_i18n": {
            "ja": "バーチャルマーケット",
            "es": "Mercado Virtual"
         },
         "variants": [
            {
               "name": "Space",
               "name_i18n": {
                  "ja": "スペース",
                  "es": "Espacio"
               },
               "types": [
                  {
                     "name": "Standard",
                     "name_i18n": {
                        "ja": "標準",
                        "es": "Estandar"
                     },
                     "width_m": 4.0,
                     "depth_m": 4.0,
                     "height_m": 5.0,
                     "front_axis": "y-"
                  }
               ]
            }
         ]
      },
      {
         "name": "Casmarket",
         "legacy": true,
         "variants": [
            {
               "name": "Booth",
               "types": [
                  {
                     "name": "S",
                     "width_m": 4.0,
                     "depth_m": 4.0,
                     "height_m": 5.0,
                     "front_axis": "y-"
                  }
               ]
            }
         ]
      }
   ]
}
```

## Development
- Main add-on entry point: `metaverse_booth_utility/__init__.py`
- Preset data: `metaverse_booth_utility/defaults.json`
- Blender Extensions manifest: `blender_manifest.toml`

## Release Packaging
This repository includes a GitHub Actions workflow that:
- Reads add-on version from `bl_info`
- Packages `metaverse_booth_utility/` as a zip
- Uploads the zip as a build artifact
- Creates a GitHub Release asset when a `v*` tag is pushed

## CI Validation
This repository includes a GitHub Actions workflow that validates preset JSON schema compatibility:
- Workflow: `.github/workflows/lint-defaults-schema.yml`
- Runs on push to `main` (when preset/schema/workflow files change)
- Runs on pull requests targeting `main` (same file scope)
- Checks `metaverse_booth_utility/defaults.json` against `metaverse_booth_utility/defaults.schema.json`
