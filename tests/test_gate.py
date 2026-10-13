import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import evaluate_claim, introduced_numbers

EVIDENCE = {
    "r1:1": "The checkout was confusing and I could not find the delivery option.",
    "r2:1": "I found checkout confusing, especially the delivery section.",
    "r3:1": "Checkout worked well for me."
}

class GateTests(unittest.TestCase):
    def test_passes_grounded_multi_respondent_claim(self):
        result = evaluate_claim({
            "id": "c1",
            "text": "Checkout and delivery were confusing for some respondents.",
            "evidence_ids": ["r1:1", "r2:1"]
        }, EVIDENCE)
        self.assertEqual(result["decision"], "PASS")

    def test_flags_introduced_number(self):
        result = evaluate_claim({
            "id": "c2",
            "text": "Users abandon checkout within 5 minutes because delivery is confusing.",
            "evidence_ids": ["r1:1", "r2:1"]
        }, EVIDENCE)
        self.assertIn("introduced_numeric_claim", result["flags"])

    def test_flags_single_respondent_generalisation(self):
        result = evaluate_claim({
            "id": "c3",
            "text": "Most users find checkout confusing.",
            "evidence_ids": ["r1:1"]
        }, EVIDENCE)
        self.assertIn("overgeneralisation_risk", result["flags"])

    def test_missing_evidence_fails(self):
        result = evaluate_claim({
            "id": "c4",
            "text": "Users love the product.",
            "evidence_ids": ["missing:1"]
        }, EVIDENCE)
        self.assertEqual(result["decision"], "FAIL")

if __name__ == "__main__":
    unittest.main()
