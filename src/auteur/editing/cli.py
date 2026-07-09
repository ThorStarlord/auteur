from __future__ import annotations

from pathlib import Path

from auteur.editing.formatters import (
    format_edit_apply_success,
    format_edit_error,
    format_edit_patch_status_success,
    format_edit_review_success,
)
from auteur.editing.handlers import (
    EditApplyData,
    EditPatchStateData,
    EditReviewData,
    handle_edit_accept,
    handle_edit_apply,
    handle_edit_reject,
    handle_edit_review,
)
from auteur.editing.serializers import write_patch_proposals, write_revised_draft, write_review_artifacts


def register_edit_subcommands(sub) -> None:
    parser = sub.add_parser("edit", help="Review and apply controlled post-draft repairs.")
    commands = parser.add_subparsers(dest="edit_command", required=True)

    p = commands.add_parser("review", help="Run deterministic edit passes against a draft.")
    p.add_argument("project", type=Path)
    p.add_argument("chapter", type=int)
    p.add_argument("--passes", default="aiisms")
    p.add_argument("--draft", default=None)

    p = commands.add_parser("accept", help="Accept one patch proposal.")
    p.add_argument("project", type=Path)
    p.add_argument("chapter", type=int)
    p.add_argument("patch_id")
    p.add_argument("--draft", default=None)

    p = commands.add_parser("reject", help="Reject one patch proposal.")
    p.add_argument("project", type=Path)
    p.add_argument("chapter", type=int)
    p.add_argument("patch_id")
    p.add_argument("--draft", default=None)

    p = commands.add_parser("apply", help="Apply one accepted patch proposal.")
    p.add_argument("project", type=Path)
    p.add_argument("chapter", type=int)
    p.add_argument("--patch", dest="patch_id", required=True)
    p.add_argument("--draft", default=None)


def handle_edit_command(args) -> int:
    if args.edit_command == "review":
        result = handle_edit_review(args.project, args.chapter, args.passes, args.draft)
        if not result.is_success:
            print(format_edit_error(result.error or "edit review failed"))
            return result.exit_code
        data: EditReviewData = result.data
        write_review_artifacts(data.report, data.artifact_dir)
        print(format_edit_review_success(data.artifact_dir))
        return result.exit_code

    if args.edit_command == "accept":
        return _write_patch_state_result(
            handle_edit_accept(args.project, args.chapter, args.patch_id, args.draft),
            "accepted",
        )

    if args.edit_command == "reject":
        return _write_patch_state_result(
            handle_edit_reject(args.project, args.chapter, args.patch_id, args.draft),
            "rejected",
        )

    if args.edit_command == "apply":
        result = handle_edit_apply(args.project, args.chapter, args.patch_id, args.draft)
        data = result.data
        if isinstance(data, EditApplyData):
            write_patch_proposals(data.patches, data.artifact_dir / "patch_proposals.yaml")
            if data.revised_text is not None:
                revised_path = write_revised_draft(data.revised_text, data.artifact_dir)
                print(format_edit_apply_success(data.patch_id, revised_path))
            elif data.stale:
                print(format_edit_error(result.error or "patch is stale"))
            return result.exit_code
        print(format_edit_error(result.error or "edit apply failed"))
        return result.exit_code

    return 1


def _write_patch_state_result(result, status: str) -> int:
    if not result.is_success:
        print(format_edit_error(result.error or "patch update failed"))
        return result.exit_code
    data: EditPatchStateData = result.data
    write_patch_proposals(data.patches, data.artifact_dir / "patch_proposals.yaml")
    print(format_edit_patch_status_success(data.patch_id, status))
    return result.exit_code

