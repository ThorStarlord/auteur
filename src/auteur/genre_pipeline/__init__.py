"""Genre-neutral runtime for built-in interactive genre pipelines."""

from auteur.genre_pipeline.models import CoreIdentityProfile, GenrePipelineSpec
from auteur.genre_pipeline.registry import (
    get_all_genres,
    get_genre_pipeline,
    get_genre_pipeline_for_core,
)

__all__ = [
    "CoreIdentityProfile",
    "GenrePipelineSpec",
    "get_all_genres",
    "get_genre_pipeline",
    "get_genre_pipeline_for_core",
]
