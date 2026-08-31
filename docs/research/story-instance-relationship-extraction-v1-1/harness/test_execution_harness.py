import json
import unittest

from execution_harness import (
    RunState,
    RunStateMachine,
    build_evaluator_packet,
    build_model_packet,
    canonical_projection,
    qualify_synthetic,
    route_derived,
    sha256_text,
    validate_extractor,
)


def valid_relation(name="FACT-A"):
    return {
        "relation_type": "CAUSAL_SUPPORT",
        "source_fact_refs": [name],
        "target_ref": "FACT-B",
        "member_roles": [],
        "authority_class": "DETERMINISTIC_DERIVATION",
        "evidence_refs": [name, "FACT-B"],
        "rationale": "synthetic rationale",
        "support": "strong",
    }


class HarnessTests(unittest.TestCase):
    def test_h1_routes_valid_repetition_one_projection_to_three_probes(self):
        payload = {"relations": [valid_relation()], "abstentions": []}
        status, violations = validate_extractor(payload, {"FACT-A", "FACT-B"})
        self.assertEqual(status, "STRUCTURE_VALID")
        self.assertFalse(violations)
        projection = canonical_projection(payload)
        routes = [route_derived(1, probe, 1, status, projection)
                  for probe in ("P03", "P04", "P05")]
        self.assertEqual({r["projection"] for r in routes}, {projection})

    def test_h2_routes_two_relation_projection_to_repetition_two(self):
        payload = {"relations": [valid_relation("FACT-A"), valid_relation("FACT-C")],
                   "abstentions": []}
        status, _ = validate_extractor(payload, {"FACT-A", "FACT-B", "FACT-C"})
        projection = canonical_projection(payload)
        self.assertEqual(status, "STRUCTURE_VALID")
        self.assertEqual(route_derived(2, "P03", 2, status, projection)["projection"],
                         projection)

    def test_h3_invalid_routes_as_exact_b0_packet(self):
        b0 = "synthetic B0 packet"
        route = route_derived(3, "P03", 3, "FORMAT_INVALID", None)
        self.assertEqual(build_model_packet(b0, route["projection"]), b0)

    def test_h4_misrouting_valid_projection_as_empty_fails(self):
        payload = {"relations": [valid_relation("FACT-A"), valid_relation("FACT-C")],
                   "abstentions": []}
        status, _ = validate_extractor(payload, {"FACT-A", "FACT-B", "FACT-C"})
        with self.assertRaises(ValueError):
            route_derived(2, "P03", 2, status, None)

    def test_h5_cross_repetition_route_fails(self):
        projection = canonical_projection({"relations": [valid_relation()], "abstentions": []})
        with self.assertRaises(ValueError):
            route_derived(2, "P03", 3, "STRUCTURE_VALID", projection)

    def test_h6_evaluator_packet_detects_changed_source(self):
        source = "exact source response"
        packet, record = build_evaluator_packet(source, "EVAL:")
        self.assertTrue(record["exact_match"])
        self.assertEqual(record["source_sha256"], record["embedded_sha256"])
        with self.assertRaises(ValueError):
            build_evaluator_packet(source + " altered", "EVAL:", embedded=packet)

    def test_h7_unblind_refuses_incomplete_schedule(self):
        machine = RunStateMachine(expected_calls=78)
        machine.transition(RunState.EXTRACTION_CAPTURED)
        with self.assertRaises(ValueError):
            machine.transition(RunState.UNBLIND_ALLOWED, completed_calls=77,
                               integrity_ok=True)

    def test_h8_full_synthetic_qualification(self):
        report = qualify_synthetic()
        self.assertEqual(report["positions"], 78)
        self.assertEqual(report["illegal_transitions_accepted"], 0)
        self.assertTrue(report["pre_unblind_ready"])
        self.assertEqual(report["packet_integrity"]["extraction"], "3/3")
        self.assertEqual(report["packet_integrity"]["downstream"], "36/36")

    def test_snapshot_rules(self):
        b0 = "B0"
        overlay = canonical_projection({"relations": [valid_relation()], "abstentions": []})
        self.assertNotEqual(build_model_packet(b0, overlay), b0)
        self.assertEqual(build_model_packet(b0, None), b0)
        self.assertEqual(sha256_text(b0), sha256_text(build_model_packet(b0, None)))

    def test_full_dry_run_reconciles_every_position(self):
        report = qualify_synthetic()
        self.assertEqual(report["schedule"]["extractor"], 3)
        self.assertEqual(report["schedule"]["generator"], 36)
        self.assertEqual(report["schedule"]["extraction_evaluator"], 3)
        self.assertEqual(report["schedule"]["downstream_evaluator"], 36)
        self.assertEqual(report["schedule"]["total"], 78)
        self.assertEqual(report["snapshots"]["invalid_derived_equals_b0"], True)

    def test_p02_is_identical_across_all_conditions(self):
        report = qualify_synthetic()
        self.assertTrue(report["snapshots"]["p02_all_conditions_equal"])
        self.assertTrue(report["snapshots"]["p02_r_gold_has_no_overlay"])

    def test_downstream_projection_rejects_accepted_authority(self):
        from execution_harness import ensure_downstream_representable

        payload = {"relations": [valid_relation()], "abstentions": []}
        payload["relations"][0]["authority_class"] = "ACCEPTED"
        with self.assertRaises(ValueError):
            ensure_downstream_representable(payload)

    def test_validator_requires_rich_record_fields_and_types(self):
        payload = {"relations": [valid_relation()], "abstentions": []}
        del payload["relations"][0]["rationale"]
        status, violations = validate_extractor(payload, {"FACT-A", "FACT-B"})
        self.assertEqual(status, "FORMAT_INVALID")
        self.assertTrue(any("required" in item for item in violations))

    def test_pressure_members_match_distinct_sources(self):
        relation = {
            "relation_type": "PRESSURE_GROUP",
            "source_fact_refs": ["FACT-A", "FACT-B"],
            "target_ref": "FACT-C",
            "member_roles": [
                {"fact_ref": "FACT-A", "role": "first"},
                {"fact_ref": "FACT-A", "role": "duplicate"},
            ],
            "authority_class": "INTERPRETIVE",
            "evidence_refs": ["FACT-A", "FACT-B", "FACT-C"],
            "rationale": "synthetic rationale",
            "support": "moderate",
        }
        status, violations = validate_extractor(
            {"relations": [relation], "abstentions": []},
            {"FACT-A", "FACT-B", "FACT-C"},
        )
        self.assertEqual(status, "FORMAT_INVALID")
        self.assertTrue(any("member" in item for item in violations))

    def test_canonical_sort_handles_differing_member_roles(self):
        left = valid_relation()
        right = valid_relation("FACT-C")
        left["member_roles"] = [{"fact_ref": "FACT-A", "role": "alpha"}]
        right["member_roles"] = [{"fact_ref": "FACT-C", "role": "beta"}]
        payload = {"relations": [right, left], "abstentions": []}
        self.assertEqual(canonical_projection(payload), canonical_projection(
            {"relations": [left, right], "abstentions": []}))

    def test_h7_distinguishes_call_count_and_integrity_failures(self):
        machine = RunStateMachine(expected_calls=78)
        ready = {"unique_positions": 78, "routing_all_exact": True,
                 "integrity_all_exact": True, "sealed_condition_map": True}
        for state in list(RunState)[1:-1]:
            if state == RunState.PRE_UNBLIND_READY:
                machine.transition(state, reconciliation=ready)
            elif state == RunState.PRE_UNBLIND_FROZEN:
                machine.transition(state, reconciliation=ready)
            else:
                machine.transition(state)
        with self.assertRaisesRegex(ValueError, "call accounting"):
            machine.transition(RunState.UNBLIND_ALLOWED, completed_calls=77,
                               integrity_ok=True)
        with self.assertRaisesRegex(ValueError, "integrity"):
            machine.transition(RunState.UNBLIND_ALLOWED, completed_calls=78,
                               integrity_ok=False)


if __name__ == "__main__":
    unittest.main()
