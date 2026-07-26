"""Genre Pack registry managing built-in and custom genre packs."""

from typing import Optional
from auteur.genre_packs.models import GenrePack, SubgenreProfile, GenreErrorCode, GenrePackError
from auteur.genre_packs.loader import load_built_in_pack, load_genre_pack


class GenrePackRegistry:
    """Registry of available Genre Packs and subgenre profiles."""

    def __init__(self) -> None:
        self._packs: dict[tuple[str, str], tuple[GenrePack, str]] = {}
        # Pre-register built-in packs
        self._load_built_ins()

    def _load_built_ins(self) -> None:
        try:
            pack, content_hash = load_built_in_pack("erotic_fiction", "0.1.0")
            self.register_pack(pack, content_hash)
        except Exception:
            pass

    def register_pack(self, pack: GenrePack, content_hash: str) -> None:
        key = (pack.pack_id, pack.version)
        self._packs[key] = (pack, content_hash)

    def get_pack(self, pack_id: str, version: str = "0.1.0") -> tuple[GenrePack, str]:
        key = (pack_id, version)
        if key not in self._packs:
            # Attempt to lazy load built-in
            try:
                pack, content_hash = load_built_in_pack(pack_id, version)
                self.register_pack(pack, content_hash)
                return pack, content_hash
            except Exception as e:
                raise GenrePackError(
                    GenreErrorCode.PACK_NOT_FOUND,
                    f"Genre Pack '{pack_id}' (version {version}) is not registered or installed.",
                    {"pack_id": pack_id, "version": version},
                ) from e
        return self._packs[key]

    def get_profile(self, pack_id: str, profile_id: str, version: str = "0.1.0") -> SubgenreProfile:
        pack, _ = self.get_pack(pack_id, version)
        for profile in pack.subgenre_profiles:
            if profile.profile_id == profile_id:
                return profile
        raise GenrePackError(
            GenreErrorCode.PROFILE_NOT_FOUND,
            f"Subgenre profile '{profile_id}' not found in Genre Pack '{pack_id}' (v{version}).",
            {"pack_id": pack_id, "profile_id": profile_id, "version": version},
        )

    def list_packs(self) -> list[dict[str, str]]:
        result = []
        for (pack_id, version), (pack, content_hash) in self._packs.items():
            result.append({
                "pack_id": pack_id,
                "version": version,
                "display_name": pack.display_name,
                "content_hash": content_hash,
                "description": pack.description,
            })
        return result


_GLOBAL_REGISTRY: Optional[GenrePackRegistry] = None


def get_pack_registry() -> GenrePackRegistry:
    global _GLOBAL_REGISTRY
    if _GLOBAL_REGISTRY is None:
        _GLOBAL_REGISTRY = GenrePackRegistry()
    return _GLOBAL_REGISTRY
