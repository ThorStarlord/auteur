"""Registry for built-in Story Design Packs."""
from __future__ import annotations

from .loader import load_builtin_pack
from .models import StoryDesignPack


class StoryDesignPackRegistry:
    def __init__(self) -> None:
        self._packs: dict[tuple[str, str], tuple[StoryDesignPack, str]] = {}
        for pack_id in (
            "superhero",
            "anti_hero",
            "hard_determinism",
            "corporate_superhuman_metropolis",
            "rivals_allies",
            "investigation",
        ):
            pack, digest = load_builtin_pack(pack_id)
            self._packs[(pack.pack_id, pack.version)] = (pack, digest)

    def register(self, pack: StoryDesignPack, digest: str) -> None:
        """Register a validated pack, primarily for project-local extensions and tests."""
        self._packs[(pack.pack_id, pack.version)] = (pack, digest)

    def get(self, pack_id: str, version: str = "0.1.0") -> tuple[StoryDesignPack, str]:
        try:
            return self._packs[(pack_id, version)]
        except KeyError as exc:
            raise ValueError(f"Story Design Pack '{pack_id}' version '{version}' is not registered") from exc

    def list(self) -> list[dict[str, str]]:
        return [
            {"pack_id": p.pack_id, "pack_kind": p.pack_kind.value, "version": p.version,
             "display_name": p.display_name, "content_hash": digest, "description": p.description}
            for p, digest in self._packs.values()
        ]


_REGISTRY: StoryDesignPackRegistry | None = None


def get_design_pack_registry() -> StoryDesignPackRegistry:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = StoryDesignPackRegistry()
    return _REGISTRY
