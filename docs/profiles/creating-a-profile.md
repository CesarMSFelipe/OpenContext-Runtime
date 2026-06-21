# Creating A Profile

## Purpose
Create profiles by extending `TechnologyProfile` outside core and keeping framework imports in profile packages.

## Current Status
First-party profile registry exists in `packages/opencontext_profiles`. CLI templates can select profile names.

## Steps

Profiles are authored in code, not via the CLI (`opencontext init --template` only
scaffolds a project from an existing template). To add one:

1. For a marker-only stack, append a `MarkerProfileSpec` to the
   `ADDITIONAL_PROFILE_SPECS` tuple in
   `packages/opencontext_profiles/opencontext_profiles/markers.py`:

   ```python
   MarkerProfileSpec(
       name="myframework",
       markers=("myframework.toml", ".mf"),
       required_any_markers=("myframework.toml",),
   )
   ```

   These specs are turned into profiles by `additional_marker_profiles()` and
   registered through `first_party_profiles()` (registry.py).

2. For custom workflow packs or validation commands, subclass
   `MarkerTechnologyProfile` instead — set `workflow_packs` / `validation_commands`
   (as `SymfonyTechnologyProfile` does) and add the subclass to the `core_profiles`
   list in `registry.py`.

3. Confirm detection in a sample project:

   ```bash
   opencontext stack
   ```

See [Technology Profiles](../architecture/technology-profiles.md) for the full
registry overview.

## Implemented Code
- `packages/opencontext_profiles/opencontext_profiles/markers.py`
- `packages/opencontext_profiles/opencontext_profiles/registry.py`
- `packages/opencontext_core/opencontext_core/project/profiles.py`
