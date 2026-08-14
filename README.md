# Metaverse Booth Utility

Metaverse Booth Utility is a Blender add-on for quickly generating a booth reference frame and front-direction arrow from preset definitions.

## Features
- Sidebar UI in 3D View (`Metaverse` tab)
- Event -> variant -> type preset selection
- UI labels follow Blender UI language (`English`, `Japanese`, `Spanish`)
- Auto-filled booth dimensions from JSON presets
- Front-axis preview and generation support (`x+`, `x-`, `y+`, `y-`, `z+`, `z-`)
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
4. Click `Remove Generated` to clean up generated helpers.

## Preset JSON
Presets are loaded from `metaverse_booth_utility/defaults.json`.

Structure overview:
- `events[]`
- `events[].name`
- `events[].name_jaJP` / `events[].name_ja` / `events[].name_es` (optional localized labels)
- `events[].variants[]`
- `events[].variants[].name`
- `events[].variants[].name_jaJP` / `events[].variants[].name_ja` / `events[].variants[].name_es` (optional localized labels)
- `events[].variants[].types[]`
- `events[].variants[].types[].name`
- `events[].variants[].types[].name_jaJP` / `events[].variants[].types[].name_ja` / `events[].variants[].types[].name_es` (optional localized labels)
- `events[].variants[].types[].width_m`
- `events[].variants[].types[].depth_m`
- `events[].variants[].types[].height_m`
- `events[].variants[].types[].front_axis`

Localization behavior:
- `name` is always the canonical/fallback English key used internally.
- UI display name is chosen based on Blender language.
- For Japanese, both `name_jaJP` and `name_ja` are accepted.
- If no language-specific key is found, the add-on falls back to `name`.

Example:

```json
{
   "events": [
      {
         "name": "Virtual Market",
         "name_jaJP": "バーチャルマーケット",
         "name_ja": "バーチャルマーケット",
         "name_es": "Mercado Virtual",
         "variants": [
            {
               "name": "Space",
               "name_ja": "スペース",
               "name_es": "Espacio",
               "types": [
                  {
                     "name": "Standard",
                     "name_ja": "標準",
                     "name_es": "Estandar",
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
