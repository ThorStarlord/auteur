"""Structure proposals — re-exports from proposal_models, proposal_generation,
proposal_application, and proposal_resolution.
"""
from auteur.structure.proposal_application import apply_proposal_to_blueprint  # noqa: F401
from auteur.structure.proposal_generation import (  # noqa: F401
    propose_repairs_from_audit_diagnostics,
    propose_repairs_from_diagnostic_report,
    propose_repairs_from_diagnostics,
    propose_story_engine,
)
from auteur.structure.proposal_models import (  # noqa: F401
    ProposalDecision,
    ProposalOption,
    ProposalSelection,
    ProposalType,
    StructureProposal,
)
from auteur.structure.proposal_resolution import (  # noqa: F401
    load_resolved_rules,
    resolve_proposal,
    write_audit_repair_proposals,
)
