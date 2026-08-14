#!/usr/bin/env python3
"""Recommend a locally available research route using transparent weighted phrases."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Route:
    strong: tuple[str, ...]
    weak: tuple[str, ...]
    priority: int


ROUTES: dict[str, Route] = {
    "board-meeting": Route(
        strong=("school board meeting", "board meeting agenda", "board meeting minutes", "board packet", "meeting recording"),
        weak=("school board", "agenda item", "minutes", "meeting calendar", "public meeting"),
        priority=90,
    ),
    "school-system-assessment-contact-research": Route(
        strong=("district assessment director", "assessment director", "assessment directors", "assessment coordinator", "accountability director", "testing coordinator", "district assessment", "school system leadership", "district leadership contacts"),
        weak=("school district", "school districts", "district contact", "district leaders", "assessment office", "accountability office"),
        priority=85,
    ),
    "research-conference-presenter-roster": Route(
        strong=("conference speakers", "conference presenters", "speaker roster", "presenter roster", "panelists and moderators"),
        weak=("conference", "speakers", "presenters", "panelists", "moderators", "summit"),
        priority=80,
    ),
    "organizational-roster-building": Route(
        strong=("organization roster", "organisational roster", "universe of organizations", "list of organizations", "build a roster", "map the field"),
        weak=("roster", "organizations", "organisations", "sector", "universe", "market landscape"),
        priority=75,
    ),
    "coordinated-efficient-contact-research": Route(
        strong=("contact research", "find contacts", "leadership contacts", "email addresses", "phone numbers", "contact routes"),
        weak=("contact", "email", "phone", "names and roles", "official directory"),
        priority=70,
    ),
    "stakeholder-identification": Route(
        strong=("stakeholder map", "stakeholder analysis", "influence interest", "engagement plan", "decision rights", "affected stakeholders"),
        weak=("stakeholder", "influence", "engagement", "affected groups", "missing voices"),
        priority=65,
    ),
    "deep-research": Route(
        strong=("deep research", "comprehensive research", "literature review", "systematic review", "evidence map", "state of knowledge", "policy scan", "market scan", "adversarial analysis", "triangulate sources", "authoritative brief"),
        weak=("comprehensive", "thorough", "contested", "compare options", "hypothesis", "strategy", "landscape", "decision grade"),
        priority=50,
    ),
    "current-info-search": Route(
        strong=("latest", "latest information", "current status", "breaking news", "today", "right now", "newly released", "check current", "verify current", "look up current"),
        weak=("current", "recent", "news", "updated", "pricing", "schedule", "regulation", "officeholder", "version"),
        priority=40,
    ),
}


def _contains(text: str, phrase: str) -> bool:
    pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
    return re.search(pattern, text) is not None


def classify(question: str, available: set[str] | None = None) -> dict:
    text = " ".join(question.casefold().split())
    candidates = []

    for name, route in ROUTES.items():
        if available is not None and name not in available:
            continue
        strong_hits = [phrase for phrase in route.strong if _contains(text, phrase)]
        weak_hits = [phrase for phrase in route.weak if _contains(text, phrase)]
        explicit = _contains(text, name)
        score = (6 if explicit else 0) + 3 * len(strong_hits) + len(weak_hits)
        if score:
            candidates.append({
                "route": name,
                "score": score,
                "priority": route.priority,
                "explicit": explicit,
                "strong_hits": strong_hits,
                "weak_hits": weak_hits,
            })

    candidates.sort(key=lambda item: (-item["score"], -item["priority"], item["route"]))
    public_candidates = [{k: v for k, v in item.items() if k != "priority"} for item in candidates]

    if not candidates:
        recommendation = "general-research"
        confidence = "fallback"
        reason = "No available specialist signals matched."
    else:
        top = candidates[0]
        runner_up = candidates[1] if len(candidates) > 1 else None
        margin = top["score"] - runner_up["score"] if runner_up else top["score"]
        has_strong_basis = top["explicit"] or bool(top["strong_hits"]) or top["score"] >= 2
        clear_lead = runner_up is None or margin >= 2 or (top["score"] >= 2 and runner_up["score"] <= 1)
        if len(candidates) == 1 and top["score"] == 1:
            recommendation = "general-research"
            confidence = "low-signal fallback"
            hits = top["strong_hits"] + top["weak_hits"]
            reason = f"Only one weak specialist signal matched: {', '.join(repr(hit) for hit in hits)}."
        elif has_strong_basis and clear_lead:
            recommendation = top["route"]
            confidence = "high" if top["explicit"] or top["score"] >= 5 else "moderate"
            hits = top["strong_hits"] + top["weak_hits"]
            reason = f"Matched {', '.join(repr(hit) for hit in hits) or 'the explicit skill name'}."
        else:
            recommendation = "clarify"
            confidence = "ambiguous"
            names = ", ".join(item["route"] for item in candidates[:2])
            reason = f"The leading routes are too close: {names}."

    return {
        "question": question,
        "recommendation": recommendation,
        "confidence": confidence,
        "reason": reason,
        "candidates": public_candidates,
        "note": "Use this result as a transparent recommendation; output intent and user instructions control the final route.",
    }


def _self_test() -> None:
    cases = {
        "Find the latest pricing for this assessment platform": "current-info-search",
        "Build a comprehensive literature review on score comparability": "deep-research",
        "Find the next school board meeting agenda and packet": "board-meeting",
        "Build a roster of education philanthropy organizations": "organizational-roster-building",
        "Create a stakeholder map for a new graduation policy": "stakeholder-identification",
        "Investigate formative assessment practices": "general-research",
    }
    for question, expected in cases.items():
        actual = classify(question)["recommendation"]
        if actual != expected:
            raise AssertionError(f"{question!r}: expected {expected!r}, got {actual!r}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--question", help="Research request to classify.")
    parser.add_argument("--available", help="Comma-separated installed route names. Omit to evaluate all registered routes.")
    parser.add_argument("--output", choices=("json", "human"), default="human")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        _self_test()
        print("self-test passed")
        return
    if not args.question:
        parser.error("--question is required unless --self-test is used")

    available = None
    if args.available:
        available = {item.strip() for item in args.available.split(",") if item.strip()}
    result = classify(args.question, available)

    if args.output == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Recommendation: {result['recommendation']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Reason: {result['reason']}")
        if result["candidates"]:
            print("Alternatives:")
            for item in result["candidates"][:3]:
                print(f"  - {item['route']} (score {item['score']})")


if __name__ == "__main__":
    main()
