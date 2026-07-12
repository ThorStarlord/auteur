"""OutlineLoader for YAML serialization of narrative outline artifacts.

This module provides YAML-based persistence for all outline artifacts, following
the genre_pipeline session storage pattern. All outline types (BookOutline,
ChapterOutline, CharacterArc, etc.) use the same loader with zero special-casing.
"""

from __future__ import annotations

import dataclasses
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Type, TypeVar, get_type_hints

import yaml

from auteur.narrative_blueprint.schema.outline_types import OutlineArtifact

T = TypeVar("T", bound=OutlineArtifact)


class OutlineLoader:
    """Loader/saver for narrative outline artifacts in YAML format.

    Handles:
    - Serialization of outline artifacts to YAML (save_outline)
    - Deserialization of YAML back to outline objects (load_outline)
    - Nested dataclass reconstruction (TurningPoint, ArcCheckpoint, PhaseRange)
    - DateTime preservation in ISO format
    - Parent directory creation (mkdir -p behavior)
    """

    def save_outline(self, outline: OutlineArtifact, path: str) -> None:
        """Save an outline artifact to YAML file.

        Args:
            outline: The outline artifact to save
            path: File path where the YAML should be written

        Raises:
            FileNotFoundError: If parent directory cannot be created
            ValueError: If outline is invalid
        """
        # Validate outline
        if not isinstance(outline, OutlineArtifact):
            raise ValueError(f"outline must be an OutlineArtifact, got {type(outline)}")

        # Convert to dict
        data = self._to_dict(outline)

        # Create parent directories
        output_path = Path(path)
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise FileNotFoundError(f"Cannot create parent directory for {path}") from e

        # Write YAML
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False)

    def load_outline(self, path: str, outline_class: Type[T]) -> T:
        """Load an outline artifact from YAML file.

        Args:
            path: File path to the YAML file
            outline_class: The outline class to reconstruct

        Returns:
            Fully instantiated outline object

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If YAML doesn't match outline_class
        """
        outline_path = Path(path)
        if not outline_path.exists():
            raise FileNotFoundError(f"Outline file not found: {path}")

        # Load YAML
        with open(outline_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if data is None:
            raise ValueError(f"YAML file is empty: {path}")

        if not isinstance(data, dict):
            raise ValueError(f"YAML file is not a dict: {path}")

        # Reconstruct outline
        return self._from_dict(data, outline_class)

    def _to_dict(self, outline: OutlineArtifact) -> dict[str, Any]:
        """Convert outline artifact to dictionary.

        Handles:
        - datetime objects → ISO format strings
        - Nested dataclasses → dicts
        - Enums → their values
        - Lists and dicts → pass through with recursion

        Args:
            outline: The outline artifact to convert

        Returns:
            Dictionary representation of the outline
        """
        result = {}

        # Get all attributes from the outline object
        for attr_name in dir(outline):
            # Skip private/magic attributes and methods
            if attr_name.startswith("_") or callable(getattr(outline, attr_name)):
                continue

            # Skip artifact_type method
            if attr_name == "artifact_type":
                continue

            value = getattr(outline, attr_name)
            result[attr_name] = self._serialize_value(value)

        return result

    def _serialize_value(self, value: Any) -> Any:
        """Recursively serialize a value.

        Handles:
        - datetime → ISO format string
        - Enum → value
        - dataclass → dict
        - list → list with recursive serialization
        - dict → dict with recursive serialization
        - other → pass through

        Args:
            value: The value to serialize

        Returns:
            Serialized value
        """
        if value is None:
            return None
        elif isinstance(value, datetime):
            # Convert datetime to ISO format string
            return value.isoformat()
        elif isinstance(value, Enum):
            # Convert enum to its value
            return value.value
        elif dataclasses.is_dataclass(value) and not isinstance(value, type):
            # Convert dataclass to dict
            return {
                f.name: self._serialize_value(getattr(value, f.name))
                for f in dataclasses.fields(value)
            }
        elif isinstance(value, list):
            # Recursively serialize list items
            return [self._serialize_value(item) for item in value]
        elif isinstance(value, dict):
            # Recursively serialize dict values
            return {k: self._serialize_value(v) for k, v in value.items()}
        else:
            # Pass through primitive types
            return value

    def _from_dict(self, data: dict[str, Any], outline_class: Type[T]) -> T:
        """Reconstruct outline artifact from dictionary.

        Args:
            data: Dictionary representation of the outline
            outline_class: The outline class to reconstruct

        Returns:
            Fully instantiated outline object

        Raises:
            ValueError: If data doesn't match outline_class
        """
        # Deserialize all values first
        deserialized_data = {}
        type_hints = get_type_hints(outline_class.__init__)

        # Only include keys that are in the __init__ signature
        init_params = set(type_hints.keys())

        for key, value in data.items():
            # Skip keys that are not in the __init__ signature
            if key not in init_params:
                continue

            # Get the expected type from the __init__ method
            expected_type = type_hints.get(key, type(None))

            deserialized_data[key] = self._deserialize_value(
                value, key, expected_type, outline_class
            )

        # Create instance using the deserialized data
        try:
            return outline_class(**deserialized_data)
        except TypeError as e:
            raise ValueError(f"Cannot instantiate {outline_class.__name__}: {e}") from e

    def _deserialize_value(
        self, value: Any, field_name: str, expected_type: Any, outline_class: Type[T]
    ) -> Any:
        """Recursively deserialize a value based on expected type.

        Args:
            value: The value to deserialize
            field_name: The field name (for error messages)
            expected_type: The expected type for this field
            outline_class: The outline class being reconstructed

        Returns:
            Deserialized value
        """
        if value is None:
            return None

        # Handle datetime strings
        if expected_type is datetime or (
            hasattr(expected_type, "__origin__") and "datetime" in str(expected_type)
        ):
            if isinstance(value, str):
                try:
                    return datetime.fromisoformat(value)
                except ValueError:
                    raise ValueError(f"Cannot parse datetime for {field_name}: {value}")
            return value

        # Handle Enum values
        if isinstance(expected_type, type) and issubclass(expected_type, Enum):
            if isinstance(value, str):
                try:
                    return expected_type(value)
                except ValueError:
                    raise ValueError(
                        f"Cannot parse enum {expected_type.__name__} for {field_name}: {value}"
                    )
            return value

        # Handle dataclass reconstruction (nested dataclasses like TurningPoint)
        if isinstance(expected_type, type) and dataclasses.is_dataclass(expected_type):
            if isinstance(value, dict):
                return self._reconstruct_dataclass(value, expected_type)
            return value

        # Handle list of dataclasses
        if hasattr(expected_type, "__origin__") and expected_type.__origin__ is list:
            if isinstance(value, list):
                # Get the item type from the list generic
                item_type = expected_type.__args__[0] if hasattr(expected_type, "__args__") else None
                if item_type and dataclasses.is_dataclass(item_type):
                    return [self._reconstruct_dataclass(item, item_type) for item in value]
                return value
            return value

        # Handle dict values
        if isinstance(value, dict) and expected_type in (dict, type(None)):
            return value

        # Pass through other types
        return value

    def _reconstruct_dataclass(self, data: dict[str, Any], dataclass_type: Type) -> Any:
        """Reconstruct a dataclass from dictionary.

        Args:
            data: Dictionary representation
            dataclass_type: The dataclass type to reconstruct

        Returns:
            Instantiated dataclass

        Raises:
            ValueError: If data doesn't match dataclass_type
        """
        if not dataclasses.is_dataclass(dataclass_type):
            raise ValueError(f"{dataclass_type} is not a dataclass")

        # Get type hints for the dataclass
        type_hints = get_type_hints(dataclass_type)

        # Deserialize each field
        reconstructed_data = {}
        for field in dataclasses.fields(dataclass_type):
            field_name = field.name
            if field_name in data:
                value = data[field_name]
                expected_type = type_hints.get(field_name, type(None))
                reconstructed_data[field_name] = self._deserialize_value(
                    value, field_name, expected_type, dataclass_type  # type: ignore
                )

        # Create dataclass instance
        try:
            return dataclass_type(**reconstructed_data)
        except TypeError as e:
            raise ValueError(f"Cannot instantiate {dataclass_type.__name__}: {e}") from e
