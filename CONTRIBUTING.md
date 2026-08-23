# Contributing to Metaverse Booth Utility

Thank you for your interest in contributing to **Metaverse Booth Utility**  a Blender add-on for generating booth reference frames and front-direction arrows from preset definitions. This document explains everything you need to know to contribute effectively.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. 2. [Filing Issues](#filing-issues)
   3. 3. [Environment Setup](#environment-setup)
      4. 4. [Coding Standards](#coding-standards)
         5. 5. [Preset JSON Contributions](#preset-json-contributions)
            6. 6. [Localization Contributions](#localization-contributions)
               7. 7. [Branching Strategy](#branching-strategy)
                  8. 8. [Commit Message Conventions](#commit-message-conventions)
                     9. 9. [Pull Request Requirements](#pull-request-requirements)
                        10. 10. [Release Process](#release-process)
                           
                            11. ---
                           
                            12. ## Code of Conduct
                           
                            13. Be respectful and constructive. This project welcomes contributors of all backgrounds and skill levels. Harassment, discrimination, or disruptive behaviour in any form will not be tolerated.
                           
                            14. ---
                           
                            15. ## Filing Issues
                           
                            16. Before opening a new issue, please search [existing issues](../../issues) to avoid duplicates.
                           
                            17. ### Bug Reports
                           
                            18. Include the following in your report:
                           
                            19. - **Blender version** (e.g., `4.2.1`)
                                - - **Add-on version** (visible in *Edit > Preferences > Add-ons > Metaverse Booth Utility*)
                                  - - **Operating system** (e.g., Windows 11, macOS 14, Ubuntu 24.04)
                                    - - **Steps to reproduce**  numbered, minimal, and clear
                                      - - **Expected behaviour** vs. **actual behaviour**
                                        - - **Console output**  paste any Python errors from Blender's System Console (*Window > Toggle System Console* on Windows; launch from terminal on macOS/Linux)
                                          - - **Screenshots or screen recordings** if applicable
                                           
                                            - ### Feature Requests
                                           
                                            - Describe the problem you are trying to solve, not just the solution you have in mind. Include:
                                           
                                            - - **Use case**  who benefits and why
                                              - - **Proposed behaviour**  how you envision it working
                                                - - **Alternatives considered**
                                                 
                                                  - ### Preset / Event Data Requests
                                                 
                                                  - If you would like a new metaverse event or booth type added to `defaults.json`, open an issue with the label `preset-request` and provide:
                                                 
                                                  - - Event name and official source / URL
                                                    - - Booth variant names and dimensions (width x depth x height in metres)
                                                      - - Front axis direction
                                                        - - Localized names if available (Japanese, Spanish, or others)
                                                         
                                                          - ---

                                                          ## Environment Setup

                                                          ### Prerequisites

                                                          | Requirement | Minimum version |
                                                          |---|---|
                                                          | Blender | 3.6 |
                                                          | Python | Ships with Blender (no separate install needed) |
                                                          | Git | Any recent version |

                                                          ### Clone and install the add-on in development mode

                                                          ```bash
                                                          git clone https://github.com/hsaito/metaverse_booth_utility.git
                                                          cd metaverse_booth_utility
                                                          ```

                                                          **Blender add-on development link (recommended):**

                                                          1. Locate your Blender add-ons directory:
                                                          2.    - **Windows:** `%APPDATA%\Blender Foundation\Blender\>version>\scripts\addons\`
                                                                -    - **macOS:** `~/Library/Application Support/Blender/>version>/scripts/addons/`
                                                                     -    - **Linux:** `~/.config/blender/>version>/scripts/addons/`
                                                                          - 2. Create a symbolic link (or junction on Windows) from the `metaverse_booth_utility/` subdirectory into the add-ons directory so that Blender loads directly from your working tree.
                                                                            3. 3. Enable the add-on in *Edit > Preferences > Add-ons > Metaverse Booth Utility*.
                                                                               4. 4. Use **Reload Scripts** (`F3 > Reload Scripts`, or the button in Preferences) after editing Python files to apply changes without restarting Blender.
                                                                                 
                                                                                  5. ### JSON schema validation (CI parity)
                                                                                 
                                                                                  6. The CI workflow validates `defaults.json` against `defaults.schema.json`. To run this locally before pushing:
                                                                                 
                                                                                  7. ```bash
                                                                                     pip install check-jsonschema
                                                                                     check-jsonschema --schemafile metaverse_booth_utility/defaults.schema.json \
                                                                                                      metaverse_booth_utility/defaults.json
                                                                                     ```

                                                                                     ### Recommended editor

                                                                                     The repository ships a `.vscode/` configuration. [Visual Studio Code](https://code.visualstudio.com/) with the **Pylance** and **Blender Development** extensions provides the best in-editor experience.

                                                                                     ---

                                                                                     ## Coding Standards

                                                                                     ### Python style

                                                                                     - Follow [PEP 8](https://peps.python.org/pep-0008/) with a maximum line length of **120 characters**.
                                                                                     - - Use **4 spaces** for indentation  never tabs.
                                                                                       - - Keep Blender API calls at the module level where practical; avoid importing `bpy` inside functions unless necessary.
                                                                                         - - Prefer `bpy.props` descriptors declared at the class level over runtime attribute assignment.
                                                                                           - - Operators, panels, and preferences must be registered/unregistered through the module's `register()` / `unregister()` functions.
                                                                                             - - All operator `bl_idname` values must be prefixed with `metaverse_booth_utility.` to avoid namespace conflicts.
                                                                                              
                                                                                               - ### Type annotations
                                                                                              
                                                                                               - - Use type hints (PEP 484) for all public functions and methods.
                                                                                                 - - Blender RNA properties do not support standard Python type hints  document their types in docstrings instead.
                                                                                                  
                                                                                                   - ### Docstrings
                                                                                                  
                                                                                                   - - Use Google-style docstrings for functions and classes.
                                                                                                     - - Every operator, panel, and preference class must have a one-line `bl_description` and an inline comment explaining non-obvious logic.
                                                                                                      
                                                                                                       - ### Error handling
                                                                                                      
                                                                                                       - - Never use a bare `except:` clause. Catch specific exception types.
                                                                                                         - - Use `self.report({'ERROR'}, message)` inside operators instead of `print()` for user-visible errors.
                                                                                                          
                                                                                                           - ### No third-party dependencies
                                                                                                          
                                                                                                           - The add-on must ship without any third-party Python packages. All logic must rely exclusively on:
                                                                                                           - - Python standard library modules
                                                                                                             - - `bpy`, `mathutils`, and other Blender-bundled APIs
                                                                                                               - - `json` for preset loading
                                                                                                                
                                                                                                                 - ---
                                                                                                                 
                                                                                                                 ## Preset JSON Contributions
                                                                                                                 
                                                                                                                 Preset data lives in `metaverse_booth_utility/defaults.json` and is validated against `metaverse_booth_utility/defaults.schema.json`.
                                                                                                                 
                                                                                                                 ### Rules for editing presets
                                                                                                                 
                                                                                                                 - **Do not break the schema.** Run `check-jsonschema` locally (see [Environment Setup](#environment-setup)) before committing.
                                                                                                                 - - `name` must be the canonical English identifier used internally. It must be unique within its parent list.
                                                                                                                   - - `name_i18n` is optional. Provide localized display labels as a map of locale keys (e.g., `"ja"`, `"es"`, `"ja-JP"`).
                                                                                                                     - - Dimensions (`width_m`, `depth_m`, `height_m`) must be in **metres** as floating-point numbers.
                                                                                                                       - - `front_axis` must be one of: `"x+"`, `"x-"`, `"y+"`, `"y-"`, `"z+"`, `"z-"`.
                                                                                                                         - - Mark outdated or superseded entries with `"legacy": true` rather than deleting them, to preserve backward compatibility.
                                                                                                                           - - Add new events at the **end** of the `events` array; add new variants/types at the end of their respective arrays.
                                                                                                                            
                                                                                                                             - ---
                                                                                                                             
                                                                                                                             ## Localization Contributions
                                                                                                                             
                                                                                                                             The add-on supports English, Japanese (`ja`), and Spanish (`es`) UI labels. Localized strings are stored in two places:
                                                                                                                             
                                                                                                                             1. **Python source**  labels passed to Blender's `bpy.app.translations` or used directly as `bl_label` strings.
                                                                                                                             2. 2. **Preset JSON**  `name_i18n` maps inside `defaults.json`.
                                                                                                                               
                                                                                                                                3. When adding or modifying UI text:
                                                                                                                               
                                                                                                                                4. - Provide the English string first.
                                                                                                                                   - - If you know a correct translation, add it to the relevant locale key. If not, leave a comment in your PR and label it `needs-translation`.
                                                                                                                                     - - Do not use machine-translation without review by a native speaker.
                                                                                                                                      
                                                                                                                                       - ---
                                                                                                                                       
                                                                                                                                       ## Branching Strategy
                                                                                                                                       
                                                                                                                                       This project uses a **trunk-based development** model centred on `main`.
                                                                                                                                       
                                                                                                                                       | Branch pattern | Purpose |
                                                                                                                                       |---|---|
                                                                                                                                       | `main` | Stable, always releasable. Protected  no direct pushes. |
                                                                                                                                       | `feature/>short-description>` | New features or enhancements (e.g., `feature/add-cluster-preset`) |
                                                                                                                                       | `fix/>short-description>` | Bug fixes (e.g., `fix/front-axis-reset`) |
                                                                                                                                       | `chore/>short-description>` | Tooling, CI, or housekeeping (e.g., `chore/update-schema-validator`) |
                                                                                                                                       | `docs/>short-description>` | Documentation-only changes (e.g., `docs/update-readme-usage`) |
                                                                                                                                        Commits](https://www.conventionalcommits.org/) format.
                                                                                                                                    
                                                                                                                                       ### Format
                                                                                                                                    
                                                                                                                                       ```
                                                                                                                                       >type>(>scope>): >short summary>

                                                                                                                                       [optional body]

                                                                                                                                       [optional footer]
                                                                                                                                       ```
                                                                                                                                    
                                                                                                                                       ### Types
                                                                                                                                    
                                                                                                                                       | Type | When to use |
                                                                                                                                       |---|---|
                                                                                                                                       | `feat` | A new feature or capability |
                                                                                                                                       | `fix` | A bug fix |
                                                                                                                                       | `docs` | Documentation changes only |
                                                                                                                                       | `style` | Formatting, whitespace  no logic change |
                                                                                                                                       | `refactor` | Code restructuring without behaviour change |
                                                                                                                                       | `test` | Adding or updating tests |
                                                                                                                                       | `chore` | Build process, CI, tooling, dependency updates |
                                                                                                                                       | `preset` | Adding or updating entries in `defaults.json` |
                                                                                                                                       | `i18n` | Localization additions or corrections |
                                                                                                                                    
                                                                                                                                       ### Scopes (optional but encouraged)
                                                                                                                                    
                                                                                                                                       `ui`, `operator`, `preset`, `schema`, `prefs`, `ci`, `docs`
                                                                                                                                    
                                                                                                                                       ### Rules
                                                                                                                                    
                                                                                                                                       - Use the **imperative mood** in the summary line: *"add cluster booth variant"*, not *"added"* or *"adds"*.
                                                                                                                                       - - Limit the summary line to **72 characters**.
                                                                                                                                         - - Reference issue numbers in the footer: `Closes #42` or `Refs #17`.
                                                                                                                                           - - Mark breaking changes with `BREAKING CHANGE:` in the footer and a `!` after the type: `feat!: rename bl_idname prefix`.
                                                                                                                                            
                                                                                                                                             - ### Examples
                                                                                                                                            
                                                                                                                                             - ```
                                                                                                                                               feat(preset): add VketCloud 2025 booth variants

                                                                                                                                               Adds Standard, Wide, and Corner variants for VketCloud 2025.
                                                                                                                                               Dimensions sourced from official event guide.

                                                                                                                                               Closes #38
                                                                                                                                               ```
                                                                                                                                    
                                                                                                                                               ```
                                                                                                                                               fix(ui): reset front-axis dropdown on preset change

                                                                                                                                               Previously the front-axis selector retained a stale value
                                                                                                                                               when the user switched between events.

                                                                                                                                               Refs #29
                                                                                                                                               ```
                                                                                                                                    
                                                                                                                                               ```
                                                                                                                                               chore(ci): pin check-jsonschema to 0.29.3
                                                                                                                                               ```
                                                                                                                                    
                                                                                                                                               ---
                                                                                                                                    
                                                                                                                                               ## Pull Request Requirements
                                                                                                                                    
                                                                                                                                               ### Before opening a PR
                                                                                                                                    
                                                                                                                                               - [ ] Your branch is up to date with `main` (rebase preferred over merge).
                                                                                                                                               - [ ] - [ ] JSON schema validation passes locally (`check-jsonschema`).
                                                                                                                                               - [ ] - [ ] The add-on loads without errors in Blender 3.6+ and the latest stable Blender release.
                                                                                                                                               - [ ] - [ ] All changed Python files pass basic PEP 8 checks.
                                                                                                                                               - [ ] - [ ] Commit messages follow the conventions above.
                                                                                                                                              
                                                                                                                                               - [ ] ### PR description
                                                                                                                                              
                                                                                                                                               - [ ] Use the PR template and fill out all sections:
                                                                                                                                              
                                                                                                                                               - [ ] - **What does this PR do?**  one-paragraph summary.
                                                                                                                                               - [ ] - **Why?**  motivation, linked issue if applicable.
                                                                                                                                               - [ ] - **How was it tested?**  Blender version(s), OS, specific steps taken.
                                                                                                                                               - [ ] - **Screenshots**  required for any UI changes.
                                                                                                                                               - [ ] - **Checklist**  tick all boxes before requesting review.
                                                                                                                                              
                                                                                                                                               - [ ] ### Review process
                                                                                                                                              
                                                                                                                                               - [ ] - At least **one approving review** from a maintainer is required before merging.
                                                                                                                                               - [ ] - Address all review comments or explicitly explain why a suggestion is declined.
                                                                                                                                               - [ ] - Prefer **Squash and Merge** for `fix` and `chore` PRs; **Rebase and Merge** for `feat` and `preset` PRs to preserve a clean, readable history on `main`.
                                                                                                                                               - [ ] - Do not merge your own PR without a review unless you are the sole maintainer making a hotfix.
                                                                                                                                              
                                                                                                                                               - [ ] ### CI checks
                                                                                                                                              
                                                                                                                                               - [ ] All PRs targeting `main` must pass the `lint-defaults-schema` workflow. PRs that only touch documentation or non-JSON/non-Python files may skip JSON validation automatically; verify the workflow behaviour before assuming a skip is expected.
                                                                                                                                              
                                                                                                                                               - [ ] ---
                                                                                                                                              
                                                                                                                                               - [ ] ## Release Process
                                                                                                                                              
                                                                                                                                               - [ ] > This section is for maintainers.
                                                                                                                                              
                                                                                                                                               - [ ] 1. Confirm `main` is green (all CI checks pass).
                                                                                                                                               - [ ] 2. Update the version tuple in `metaverse_booth_utility/__init__.py` (`bl_info["version"]`) and in `blender_manifest.toml`.
                                                                                                                                               - [ ] 3. Commit the version bump: `chore(release): bump version to X.Y.Z`.
                                                                                                                                               - [ ] 4. Push a tag: `git tag vX.Y.Z && git push origin vX.Y.Z`.
                                                                                                                                               - [ ] 5. GitHub Actions will automatically package the add-on zip and attach it to a new GitHub Release.
                                                                                                                                               - [ ] 6. Edit the release notes on GitHub to summarise changes, crediting contributors.
                                                                                                                                              
                                                                                                                                               - [ ] ---
                                                                                                                                              
                                                                                                                                               - [ ] *Thank you for helping make Metaverse Booth Utility better for everyone!*
                                                                                                                                       ### Rules
                                                                                                                                       
                                                                                                                                       - Branch off from the latest `main`.
                                                                                                                                       - - Keep branches short-lived  open a PR as soon as the work is ready for review.
                                                                                                                                         - - Delete branches after they are merged.
                                                                                                                                           - - Never force-push to `main`.
                                                                                                                                             - - Releases are tagged on `main` using `v>major>.>minor>.>patch>` (e.g., `v1.2.0`). Pushing a `v*` tag triggers the GitHub Actions release workflow.
                                                                                                                                              
                                                                                                                                               - ---
                                                                                                                                               
                                                                                                                                               ## Commit Message Conventions
                                                                                                                                               
                                                                                                                                               This project follows a simplified [Conventional
