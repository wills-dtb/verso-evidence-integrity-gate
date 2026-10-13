from __future__ import annotations
import json
import re
import sys
from hashlib import sha256
from pathlib import Path
from typing import Dict, List, Any

STOPWORDS = {
    "the","a","an","and","or","to","of","in","on","for","with","is","are","was",
    "were","be","been","that","this","it","they","their","them","most","users",
    "customers","people","respondents","say","said","find","found"
}

def tokens(text: str) -> set[str]:
    return {
        t for t in re.findall(r"[a-zA-ZÀ-ÿ0-9]+", text.lower())
        if len(t) > 2 and t not in STOPWORDS
    }

def numbers(text: str) -> set[str]:
    return set(re.findall(r"\b\d+(?:\.\d+)?%?\b", text))

def support_score(claim: str, excerpts: List[str]) -> float:
    claim_tokens = tokens(claim)
    if not claim_tokens:
        return 0.0
    evidence_tokens = tokens(" ".join(excerpts))
    return round(len(claim_tokens & evidence_tokens) / len(claim_tokens), 3)

def introduced_numbers(claim: str, excerpts: List[str]) -> List[str]:
    evidence_nums = numbers(" ".join(excerpts))
    return sorted(numbers(claim) - evidence_nums)

def audit_hash(claim: str, evidence_ids: List[str]) -> str:
    payload = claim + "|" + "|".join(sorted(evidence_ids))
    return sha256(payload.encode()).hexdigest()[:16]

def evaluate_claim(claim: Dict[str, Any], evidence: Dict[str, str]) -> Dict[str, Any]:
    evidence_ids = claim.get("evidence_ids", [])
    excerpts = [evidence[eid] for eid in evidence_ids if eid in evidence]
    distinct_respondents = {eid.split(":")[0] for eid in evidence_ids if ":" in eid}
    score = support_score(claim["text"], excerpts)
    new_numbers = introduced_numbers(claim["text"], excerpts)
    flags = []

    if len(distinct_respondents) < 2:
        flags.append("too_few_independent_respondents")

    if score < 0.35:
        flags.append("weak_textual_support")

    if new_numbers:
        flags.append("introduced_numeric_claim")

    claim_text = claim["text"].lower()
    if any(q in claim_text for q in ["most ", "majority", "almost all", "nearly all"]):
        if len(distinct_respondents) < 4:
            flags.append("overgeneralisation_risk")

    if not excerpts:
        flags.append("missing_evidence")

    if "missing_evidence" in flags or (score < 0.20 and new_numbers):
        decision = "FAIL"
    elif flags:
        decision = "REVIEW"
    else:
        decision = "PASS"

    return {
        "claim_id": claim["id"],
        "decision": decision,
        "support_score": score,
        "distinct_respondents": len(distinct_respondents),
        "introduced_numbers": new_numbers,
        "flags": flags,
        "evidence_ids": evidence_ids,
        "audit_hash": audit_hash(claim["text"], evidence_ids),
    }

def evaluate_study(study: Dict[str, Any]) -> Dict[str, Any]:
    evidence = study["evidence"]
    results = [evaluate_claim(c, evidence) for c in study["claims"]]
    return {
        "study_id": study["study_id"],
        "summary": {
            "pass": sum(r["decision"] == "PASS" for r in results),
            "review": sum(r["decision"] == "REVIEW" for r in results),
            "fail": sum(r["decision"] == "FAIL" for r in results),
        },
        "claims": results,
    }

def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python app.py <study.json>")
    study = json.loads(Path(sys.argv[1]).read_text())
    print(json.dumps(evaluate_study(study), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
