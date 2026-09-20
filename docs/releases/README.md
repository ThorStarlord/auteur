# Auteur Release Records

This directory contains release-specific records and frozen historical release documentation.

## Published Release Line

The latest published GitHub release/tag is **v0.37.1**. Remote release/tag state was reconciled on 2026-09-20.

- [v0.37.1 — Post-Release Reliability and Authority Hardening](v0.37.1.md)
- [v0.37.0](v0.37.0.md)

`pyproject.toml` on current development `main` reports **1.0.0**. That metadata reflects the Version 1.0 candidate/development line; no `v1.0.0` GitHub release/tag is published as of the reconciliation date. Development metadata, qualification evidence, and publication are separate states.

## Historical Changelog Archive

The former root `CHANGELOG.md` contained detailed historical entries through v0.12.0 plus earlier releases. During the 2026-09-11 documentation reconciliation it was preserved unchanged as:

- [legacy-changelog-through-v0.12.0.md](legacy-changelog-through-v0.12.0.md)

Do not rewrite this archive to match current architecture or terminology. It is historical evidence of how those releases were described at the time.

## Which Document to Use

- Use [`../../STATUS.md`](../../STATUS.md) for the current development state and next work.
- Use [`../../CHANGELOG.md`](../../CHANGELOG.md) for the concise release index and unreleased ledger.
- Use release files in this directory for exact release claims.
- Use [`../engineering/release-qualification.md`](../engineering/release-qualification.md) for candidate/release qualification rules.
- Use PR qualification records and Git history for exact candidate evidence when a release document does not cover later development.

Open pull requests, research branches, and experiments are not release claims.
