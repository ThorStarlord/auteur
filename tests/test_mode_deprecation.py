"""Tests for --mode open-ended deprecation warning (issue #21)."""

from __future__ import annotations



class TestModeDeprecationWarning:

    def test_mode_open_ended_deprecates(self, monkeypatch, capsys):
        """--mode open-ended should emit a deprecation warning before LLM call."""
        from auteur.llm import LLMResponse
        from auteur.llm.fake import FakeClient
        fake = FakeClient([LLMResponse(text="yaml:\n  title: Test", input_tokens=10, output_tokens=5)])
        monkeypatch.setattr("auteur.llm.factory.build_client", lambda *a, **kw: fake)
        from auteur.cli import main
        main([
            "identity", "recommend",
            "A test premise",
            "--mode", "open-ended",
            "--candidates", "1",
        ])
        stderr = capsys.readouterr().err
        assert "deprecated" in stderr.lower()

    def test_recommend_mode_no_deprecation(self, monkeypatch, capsys):
        """--recommend-mode open-ended should NOT emit a deprecation warning."""
        from auteur.llm import LLMResponse
        from auteur.llm.fake import FakeClient
        fake = FakeClient([LLMResponse(text="yaml:\n  title: Test", input_tokens=10, output_tokens=5)])
        monkeypatch.setattr("auteur.llm.factory.build_client", lambda *a, **kw: fake)
        from auteur.cli import main
        main([
            "identity", "recommend",
            "A test premise",
            "--recommend-mode", "open-ended",
            "--candidates", "1",
        ])
        stderr = capsys.readouterr().err
        assert "deprecated" not in stderr.lower()

    def test_both_flags_parse(self, monkeypatch):
        """Both flags should parse without SystemExit."""
        from auteur.llm import LLMResponse
        from auteur.llm.fake import FakeClient
        fake = FakeClient([LLMResponse(text="yaml:\n  title: Test", input_tokens=10, output_tokens=5)])
        monkeypatch.setattr("auteur.llm.factory.build_client", lambda *a, **kw: fake)
        from auteur.cli import main
        rc1 = main([
            "identity", "recommend",
            "A test premise",
            "--mode", "open-ended",
            "--candidates", "1",
        ])
        assert rc1 is not None
        rc2 = main([
            "identity", "recommend",
            "A test premise",
            "--recommend-mode", "open-ended",
            "--candidates", "1",
        ])
        assert rc2 is not None
