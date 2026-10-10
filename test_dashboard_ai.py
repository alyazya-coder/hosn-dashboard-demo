from __future__ import annotations

from pathlib import Path
import unittest
import warnings

from hosn_dashboard_ai import (
    FEATURE_ORDER,
    decision_from_features,
    load_model_bundle,
    load_scenario_summaries,
)


class DashboardIntegrationTests(unittest.TestCase):
    root = Path(__file__).resolve().parent

    @classmethod
    def setUpClass(cls):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            cls.bundle = load_model_bundle(cls.root)
        cls.scenarios = load_scenario_summaries(cls.root)

    def test_measured_model_contract(self):
        self.assertTrue(self.bundle.report["acceptance_gate"]["accepted"])
        self.assertIs(self.bundle.report["synthetic_data"], False)
        self.assertEqual(tuple(self.bundle.model.feature_order), FEATURE_ORDER)

    def test_three_recorded_scenarios_replay(self):
        expected = {
            "1": ("HANDOVER", "RULES", False, "CLEAR"),
            "2": ("HANDOVER", "AI", True, "CONFLICT"),
            "3": ("STAY", "AI", True, "CONFLICT"),
        }
        for number, summary in self.scenarios.items():
            features = summary["recording_checks"][-1]["controller_decision"][
                "controller_result"
            ]["features"]
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                decision = decision_from_features(features, self.bundle.model)
            self.assertEqual(
                (decision.decision, decision.source, decision.ai_called, decision.rule_status),
                expected[number],
            )


if __name__ == "__main__":
    unittest.main()

