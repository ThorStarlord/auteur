from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from pydantic import ValidationError

from auteur.blueprint import StoryMode
from auteur.genre_pipeline.models import GenrePipelineSpec, GenreSession, GenreSessionStatus


class GenreSessionError(ValueError):
    pass


@dataclass(frozen=True)
class GenreSessionStore:
    project_path: Path
    spec: GenrePipelineSpec
    session_file: Path
    legacy_session_file: Path

    @classmethod
    def for_project(cls, project_path: Path, spec: GenrePipelineSpec) -> "GenreSessionStore":
        project = Path(project_path)
        return cls(
            project_path=project,
            spec=spec,
            session_file=project / ".auteur" / "genre_sessions" / spec.slug / "session.json",
            legacy_session_file=project / "netorare" / "session.json",
        )

    def create(
        self,
        core_id: str,
        *,
        mode: StoryMode | str | None = None,
        working_title: str | None = None,
    ) -> GenreSession:
        if self.legacy_session_file.exists():
            raise GenreSessionError(
                f"Legacy genre session exists at {self.legacy_session_file}; "
                "move or remove it explicitly before starting a new session."
            )
        if self.session_file.exists():
            raise GenreSessionError(f"Genre session already exists at {self.session_file}")
        if core_id not in self.spec.core_ids:
            raise GenreSessionError(f"Unknown core_id '{core_id}' for {self.spec.slug}")

        profile = self.spec.identity_profile_factory(core_id)
        try:
            resolved_mode = profile.default_mode if mode is None else StoryMode(mode)
        except ValueError as exc:
            raise GenreSessionError(f"Invalid story mode: {mode}") from exc
        now = datetime.now(timezone.utc)
        session = GenreSession(
            id=str(uuid4()),
            genre=self.spec.genre,
            core_id=core_id,
            mode=resolved_mode,
            working_title=(working_title or profile.default_title).strip(),
            created_at=now,
            updated_at=now,
        )
        self._write(session)
        return session

    def load(self) -> GenreSession:
        if not self.session_file.exists():
            raise GenreSessionError(f"Genre session not found: {self.session_file}")
        try:
            return GenreSession.model_validate_json(self.session_file.read_text(encoding="utf-8"))
        except (OSError, ValidationError) as exc:
            raise GenreSessionError(f"Invalid genre session at {self.session_file}: {exc}") from exc

    def update_choices(self, phase: int, choices: dict[str, str]) -> GenreSession:
        session = self._load_incomplete()
        merged = {key: dict(value) for key, value in session.choices.items()}
        merged.setdefault(phase, {}).update(choices)
        session.choices = merged
        session.updated_at = datetime.now(timezone.utc)
        self._write(session)
        return session

    def update_settings(
        self,
        *,
        mode: StoryMode | str | None = None,
        working_title: str | None = None,
    ) -> GenreSession:
        session = self._load_incomplete()
        if mode is not None:
            try:
                session.mode = StoryMode(mode)
            except ValueError as exc:
                raise GenreSessionError(f"Invalid story mode: {mode}") from exc
        if working_title is not None:
            title = working_title.strip()
            if not title:
                raise GenreSessionError("Working title must not be empty")
            session.working_title = title
        session.updated_at = datetime.now(timezone.utc)
        self._write(session)
        return session

    def mark_complete(self) -> GenreSession:
        session = self._load_incomplete()
        session.status = GenreSessionStatus.COMPLETE
        session.updated_at = datetime.now(timezone.utc)
        self._write(session)
        return session

    def _load_incomplete(self) -> GenreSession:
        session = self.load()
        if session.status == GenreSessionStatus.COMPLETE:
            raise GenreSessionError("A completed genre session cannot be modified")
        if session.status == GenreSessionStatus.ARCHIVED:
            raise GenreSessionError("An archived genre session cannot be modified")
        return session

    @property
    def history_dir(self) -> Path:
        return self.session_file.parent / "history"

    def acknowledge_warning(self, warning: str) -> GenreSession:
        session = self.load()
        if warning not in session.warnings:
            raise GenreSessionError("Warning is not present in this session")
        if warning not in session.acknowledged_warnings:
            session.acknowledged_warnings.append(warning)
            session.updated_at = datetime.now(timezone.utc)
            self._write(session)
        return session

    def archive(self) -> GenreSession:
        session = self.load()
        if session.status == GenreSessionStatus.ARCHIVED:
            raise GenreSessionError("Genre session is already archived")
        session.status = GenreSessionStatus.ARCHIVED
        session.updated_at = datetime.now(timezone.utc)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        archive_path = self.history_dir / f"{session.id}.json"
        self._write_to(session, archive_path)
        self.session_file.unlink()
        return session

    def history(self) -> list[GenreSession]:
        if not self.history_dir.exists():
            return []
        sessions: list[GenreSession] = []
        for path in sorted(self.history_dir.glob("*.json")):
            try:
                sessions.append(GenreSession.model_validate_json(path.read_text(encoding="utf-8")))
            except (OSError, ValidationError) as exc:
                raise GenreSessionError(f"Invalid archived genre session at {path}: {exc}") from exc
        return sessions

    def _write(self, session: GenreSession) -> None:
        self._write_to(session, self.session_file)

    @staticmethod
    def _write_to(session: GenreSession, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        payload = json.dumps(session.model_dump(mode="json"), indent=2, ensure_ascii=True) + "\n"
        try:
            temporary.write_text(payload, encoding="utf-8")
            temporary.replace(path)
        except OSError as exc:
            raise GenreSessionError(f"Failed to write genre session: {exc}") from exc
        finally:
            if temporary.exists():
                temporary.unlink()
