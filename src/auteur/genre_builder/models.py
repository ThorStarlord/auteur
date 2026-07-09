from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from auteur.genres.models import GenreContract


class GenreBrief(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sections: dict[str, str] = Field(default_factory=dict)
    diagnostics: list[str] = Field(default_factory=list)


class CustomGenreContract(BaseModel):
    model_config = ConfigDict(extra="forbid")

    custom_genre_id: str
    base_genre: str = "other"
    contract: GenreContract


class GenreBuilderDiagnostic(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule: str
    severity: str
    message: str

