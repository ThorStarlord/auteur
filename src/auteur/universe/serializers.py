from pathlib import Path
from auteur.universe.models import UniverseIdentity


def load_universe_identity(path: Path) -> UniverseIdentity:
    """Load a universe_identity.yaml file."""
    return UniverseIdentity.from_yaml(path)


def save_universe_identity(universe: UniverseIdentity, path: Path) -> Path:
    """Save a UniverseIdentity to YAML."""
    universe.to_yaml(path)
    return path
