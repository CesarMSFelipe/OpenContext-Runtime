"""First-party profile registry."""

from __future__ import annotations

from opencontext_core.project.profiles import TechnologyProfile
from opencontext_profiles.markers import (
    DataMlTechnologyProfile,
    DjangoTechnologyProfile,
    DotNetTechnologyProfile,
    DrupalTechnologyProfile,
    FastApiTechnologyProfile,
    GoTechnologyProfile,
    JavaSpringTechnologyProfile,
    LaravelTechnologyProfile,
    NextTechnologyProfile,
    NodeTechnologyProfile,
    PythonTechnologyProfile,
    RailsTechnologyProfile,
    ReactTechnologyProfile,
    RustTechnologyProfile,
    SymfonyTechnologyProfile,
    TerraformTechnologyProfile,
    WordPressTechnologyProfile,
    additional_marker_profiles,
)


def first_party_profiles() -> list[TechnologyProfile]:
    """Return optional first-party profiles layered above the universal core."""

    core_profiles: list[TechnologyProfile] = [
        DrupalTechnologyProfile(),
        SymfonyTechnologyProfile(),
        LaravelTechnologyProfile(),
        NodeTechnologyProfile(),
        ReactTechnologyProfile(),
        NextTechnologyProfile(),
        PythonTechnologyProfile(),
        DjangoTechnologyProfile(),
        FastApiTechnologyProfile(),
        JavaSpringTechnologyProfile(),
        DotNetTechnologyProfile(),
        GoTechnologyProfile(),
        RustTechnologyProfile(),
        RailsTechnologyProfile(),
        WordPressTechnologyProfile(),
        TerraformTechnologyProfile(),
        DataMlTechnologyProfile(),
    ]
    seen: set[str] = {profile.name for profile in core_profiles}
    expanded_profiles = [
        profile for profile in additional_marker_profiles() if profile.name not in seen
    ]
    return [*core_profiles, *expanded_profiles]
