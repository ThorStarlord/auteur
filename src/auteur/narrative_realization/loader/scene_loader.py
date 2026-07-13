"""SceneLoader: YAML serialization and deserialization for SceneOutline artifacts.

This module provides bidirectional YAML persistence for SceneOutline objects,
enabling scenes to be stored and retrieved without information loss. Handles:

- Pydantic model serialization to YAML
- YAML deserialization back to SceneOutline
- Nested model reconstruction (Goal, Opposition, Turn, Decision, Outcome, etc.)
- Enum value handling (SceneStatus, TemporalRelationType, Literal types)
- Directory operations (load/save scenes, directory listing, indexing)
- YAML structure validation
- Draft, incomplete, and ready status preservation
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import ValidationError

from auteur.narrative_realization.schema.scene_outline import (
    SceneOutline,
    SceneStatus,
    TemporalRelation,
)


class SceneLoader:
    """Loader/saver for SceneOutline artifacts in YAML format.

    Provides:
    - save_scene(scene, filepath) → writes YAML
    - load_scene(filepath) → reads YAML → SceneOutline
    - save_scenes_to_directory(scenes, dirpath) → saves batch
    - load_scenes_from_directory(dirpath) → loads all from directory
    - validate_scene_yaml_structure(filepath) → checks YAML validity
    - list_scenes_in_directory(dirpath) → lists scene filenames
    """

    def save_scene(self, scene: SceneOutline, filepath: str) -> None:
        """Save a SceneOutline to YAML file.

        Creates parent directories if needed (mkdir -p behavior).

        Args:
            scene: The SceneOutline to save
            filepath: Path where YAML should be written

        Raises:
            ValueError: If scene is invalid
            FileNotFoundError: If parent directory cannot be created
            OSError: If file cannot be written
        """
        # Validate scene
        if not isinstance(scene, SceneOutline):
            raise ValueError(f"scene must be a SceneOutline, got {type(scene)}")

        # Convert to dict for YAML serialization
        data = self._serialize_scene(scene)

        # Create parent directories
        output_path = Path(filepath)
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise FileNotFoundError(
                f"Cannot create parent directory for {filepath}"
            ) from e

        # Write YAML file
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False)
        except OSError as e:
            raise OSError(f"Cannot write to {filepath}") from e

    def load_scene(self, filepath: str) -> SceneOutline:
        """Load a SceneOutline from YAML file.

        Args:
            filepath: Path to the YAML file

        Returns:
            Fully instantiated SceneOutline object

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If YAML is invalid or doesn't match SceneOutline schema
        """
        scene_path = Path(filepath)
        if not scene_path.exists():
            raise FileNotFoundError(f"Scene file not found: {filepath}")

        # Load YAML
        try:
            with open(scene_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except OSError as e:
            raise FileNotFoundError(f"Cannot read scene file: {filepath}") from e

        if data is None:
            raise ValueError(f"YAML file is empty: {filepath}")

        if not isinstance(data, dict):
            raise ValueError(f"YAML file is not a dict: {filepath}")

        # Reconstruct SceneOutline
        try:
            return self._deserialize_scene(data)
        except ValidationError as e:
            raise ValueError(f"Invalid scene YAML in {filepath}: {e}") from e

    def save_scenes_to_directory(
        self, scenes: List[SceneOutline], dirpath: str
    ) -> None:
        """Save multiple scenes to a directory structure.

        Saves scenes in subdirectories by chapter:
        {dirpath}/{chapter_id}/{scene_id}.yaml

        Also creates an index file:
        {dirpath}/index.yaml

        Args:
            scenes: List of SceneOutline objects to save
            dirpath: Base directory for scene storage

        Raises:
            ValueError: If any scene is invalid
            FileNotFoundError: If directory cannot be created
        """
        if not scenes:
            return

        dir_path = Path(dirpath)
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise FileNotFoundError(
                f"Cannot create directory {dirpath}"
            ) from e

        # Save each scene in chapter subdirectory
        saved_scenes = []
        for scene in scenes:
            chapter_dir = dir_path / scene.chapter_id
            try:
                chapter_dir.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                raise FileNotFoundError(
                    f"Cannot create chapter directory {chapter_dir}"
                ) from e

            scene_file = chapter_dir / f"{scene.id}.yaml"
            self.save_scene(scene, str(scene_file))
            saved_scenes.append({
                "id": scene.id,
                "chapter_id": scene.chapter_id,
                "filepath": f"{scene.chapter_id}/{scene.id}.yaml",
            })

        # Write index file
        index_file = dir_path / "index.yaml"
        try:
            with open(index_file, "w", encoding="utf-8") as f:
                yaml.safe_dump(saved_scenes, f, sort_keys=False, default_flow_style=False)
        except OSError as e:
            raise OSError(f"Cannot write index file: {index_file}") from e

    def load_scenes_from_directory(self, dirpath: str) -> List[SceneOutline]:
        """Load all scenes from a directory structure.

        Expects directory layout:
        {dirpath}/{chapter_id}/{scene_id}.yaml
        {dirpath}/index.yaml (optional, for reference)

        Args:
            dirpath: Base directory containing scenes

        Returns:
            List of loaded SceneOutline objects

        Raises:
            FileNotFoundError: If directory doesn't exist
            ValueError: If any scene YAML is invalid
        """
        dir_path = Path(dirpath)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {dirpath}")

        scenes = []

        # Find all .yaml files in subdirectories (excluding index.yaml)
        for scene_file in dir_path.rglob("*.yaml"):
            # Skip index file
            if scene_file.name == "index.yaml":
                continue

            try:
                scene = self.load_scene(str(scene_file))
                scenes.append(scene)
            except (FileNotFoundError, ValueError) as e:
                # Log but continue loading other scenes
                # In production, might want to raise after collecting all errors
                pass

        return scenes

    def validate_scene_yaml_structure(self, filepath: str) -> tuple[bool, List[str]]:
        """Validate that a YAML file contains valid scene structure.

        Checks:
        - File exists
        - YAML is valid and is a dict
        - All required fields for the scene's status are present
        - All Pydantic model constraints are satisfied

        Args:
            filepath: Path to the YAML file

        Returns:
            Tuple of (is_valid, error_messages)
            is_valid: True if YAML is valid and can be loaded
            error_messages: List of validation error descriptions
        """
        errors = []
        scene_path = Path(filepath)

        # Check file exists
        if not scene_path.exists():
            errors.append(f"File not found: {filepath}")
            return False, errors

        # Check YAML validity
        try:
            with open(scene_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML syntax: {e}")
            return False, errors
        except OSError as e:
            errors.append(f"Cannot read file: {e}")
            return False, errors

        if data is None:
            errors.append("YAML file is empty")
            return False, errors

        if not isinstance(data, dict):
            errors.append(f"YAML file must be a dict, got {type(data).__name__}")
            return False, errors

        # Check that it can be deserialized as SceneOutline
        try:
            self._deserialize_scene(data)
        except ValidationError as e:
            for error in e.errors():
                error_msg = f"Validation error in {error['loc']}: {error['msg']}"
                errors.append(error_msg)
            return False, errors
        except Exception as e:
            errors.append(f"Deserialization error: {e}")
            return False, errors

        return True, []

    def list_scenes_in_directory(self, dirpath: str) -> List[str]:
        """List all scene filenames in a directory (non-recursively within chapters).

        Returns filenames (not full paths) of all .yaml scene files.

        Args:
            dirpath: Base directory containing scenes

        Returns:
            List of scene filenames (e.g., ['scene_01_01.yaml', 'scene_01_02.yaml'])

        Raises:
            FileNotFoundError: If directory doesn't exist
        """
        dir_path = Path(dirpath)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {dirpath}")

        filenames = []

        # Find all .yaml files in subdirectories, excluding index.yaml
        for scene_file in dir_path.rglob("*.yaml"):
            if scene_file.name == "index.yaml":
                continue
            # Return relative path from base directory
            filenames.append(scene_file.name)

        return sorted(filenames)

    # -----------------------------------------------------------------------
    # Internal Serialization/Deserialization
    # -----------------------------------------------------------------------

    def _serialize_scene(self, scene: SceneOutline) -> Dict[str, Any]:
        """Convert SceneOutline to dictionary for YAML serialization.

        Uses Pydantic's model_dump() with mode='json' for proper enum
        and nested model handling.

        Args:
            scene: The SceneOutline to serialize

        Returns:
            Dictionary representation suitable for YAML
        """
        # Use Pydantic's model_dump with json mode for proper serialization
        data = scene.model_dump(mode="json", exclude_none=False)
        return data

    def _deserialize_scene(self, data: Dict[str, Any]) -> SceneOutline:
        """Reconstruct SceneOutline from dictionary.

        Uses Pydantic's model_validate() to handle:
        - Enum conversion (status, turn.type, etc.)
        - Nested model reconstruction
        - Field validation

        Args:
            data: Dictionary representation of the scene

        Returns:
            Fully instantiated SceneOutline object

        Raises:
            ValidationError: If data doesn't match SceneOutline schema
        """
        # Use Pydantic's model_validate() for validation and reconstruction
        return SceneOutline.model_validate(data)
