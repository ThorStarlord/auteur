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
        self.assertEqual(report["integrity"]["extraction"], "3/3")
        self.assertEqual(report["integrity"]["downstream"], "36/36")

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


if __name__ == "__main__":
    unittest.main()
