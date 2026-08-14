# Metaverse Booth Utility

Metaverse Booth Utility is a Blender add-on for quickly generating a booth reference frame and front-direction arrow from preset definitions.

## Features
- Sidebar UI in 3D View (`Metaverse` tab)
- Event -> variant -> type preset selection
- UI labels follow Blender UI language (`English`, `Japanese`, `Spanish`)
- Auto-filled booth dimensions from JSON presets
- Front-axis preview and generation support (`x+`, `x-`, `y+`, `y-`, `z+`, `z-`)
- Generated helper objects are grouped in `Metaverse Booth Utility Generated` collection
- One-click removal of generated helper objects

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
2. (Optional) Open `Advanced` to tweak width/depth/height/front axis.
3. Click `Generate` to create helper objects:
    - `Booth Frame Reference`
    - `Booth Front Arrow`
   The helper objects are created in `Metaverse Booth Utility Generated` collection.
4. Click `Remove Generated` to clean up generated helpers.
   If the generated collection is empty afterward, it is also removed.

## Preset JSON
Presets are loaded from `metaverse_booth_utility/defaults.json`.

Structure overview:
- `events[]`
- `events[].name`
- `events[].name_i18n` (optional localized label map)
- `events[].variants[]`
- `events[].variants[].name`
- `events[].variants[].name_i18n` (optional localized label map)
- `events[].variants[].types[]`
- `events[].variants[].types[].name`
- `events[].variants[].types[].name_i18n` (optional localized label map)
- `events[].variants[].types[].width_m`
- `events[].variants[].types[].depth_m`
- `events[].variants[].types[].height_m`
- `events[].variants[].types[].front_axis`

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
