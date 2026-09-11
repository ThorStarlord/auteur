from __future__ import annotations

import shutil
import unicodedata
from pathlib import Path

import yaml

from auteur.provenance import ArtifactStore, Lifecycle
from auteur.provenance.store import canonical_content_hash


def test_yaml_semantic_hash_ignores_key_order_and_crlf(tmp_path: Path):
    left = tmp_path / "left.yaml"
    right = tmp_path / "right.yaml"
    left.write_bytes("title: Caf\u00e9\nstructure:\n  chapters: 20\n  mode: novel\n".encode("utf-8"))
    right.write_bytes("structure:\r\n  mode: novel\r\n  chapters: 20\r\ntitle: Cafe\u0301\r\n".encode("utf-8"))
    assert canonical_content_hash(left) == canonical_content_hash(right)


def test_markdown_hash_normalizes_line_endings_trailing_spaces_and_unicode(tmp_path: Path):
    left = tmp_path / "left.md"
    right = tmp_path / "right.md"
    left.write_bytes("# Caf\u00e9\nLine one\n".encode("utf-8"))
    right.write_bytes("# Cafe\u0301  \r\nLine one   \r\n\r\n".encode("utf-8"))
    assert canonical_content_hash(left) == canonical_content_hash(right)


def test_unicode_artifact_filename_and_metadata_roundtrip(tmp_path: Path):
    project = tmp_path / "Projeto \u00c9pico"
    scene = project / "chapters" / "01" / "scenes" / "cena_\u00e1rvore.yaml"
    scene.parent.mkdir(parents=True)
    scene.write_text(
        yaml.safe_dump(
            {
                "id": "cena_\u00e1rvore",
                "chapter_id": "chapter_01",
                "participants": ["L\u00edvia"],
                "location": "Esta\u00e7\u00e3o",
                "goal": "lembrar",
                "outcome": "mem\u00f3ria preservada",
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    store = ArtifactStore(project)
    accepted = store.accept(scene, "scene_realization")
    assert accepted.lifecycle is Lifecycle.ACCEPTED
    reloaded = ArtifactStore(project).status(scene, "scene_realization")
    assert reloaded.lifecycle is Lifecycle.ACCEPTED
    assert unicodedata.normalize("NFC", reloaded.content_hash) == reloaded.content_hash


def test_project_relocation_preserves_relative_provenance_and_semantic_hashes(tmp_path: Path):
    source = tmp_path / "source-project"
    scene = source / "chapters" / "01" / "scenes" / "scene_01_01.yaml"
    scene.parent.mkdir(parents=True)
    scene.write_text(
        "id: scene_01_01\nchapter_id: chapter_01\nlocation: archive\noutcome: evidence preserved\n",
        encoding="utf-8",
    )
    source_store = ArtifactStore(source)
    accepted = source_store.accept(scene, "scene_realization")
    source_hash = accepted.content_hash

    relocated = tmp_path / "relocated" / "novel"
    shutil.copytree(source, relocated)
    relocated_scene = relocated / "chapters" / "01" / "scenes" / "scene_01_01.yaml"
    relocated_store = ArtifactStore(relocated)
    status = relocated_store.status(relocated_scene, "scene_realization")

    assert status.lifecycle is Lifecycle.ACCEPTED
    assert status.content_hash == source_hash
    assert relocated_store.content_hash(relocated_scene) == source_hash
    assert relocated_store.list_revisions("scene_01_01") == [1]
