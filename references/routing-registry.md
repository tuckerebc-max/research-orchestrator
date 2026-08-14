# Routing registry

Use this registry to select the narrowest available workflow. Verify that a listed skill is available before routing. A route describes the primary work product, not merely words appearing in the request.

| Route | Choose when the primary task is | Typical signals | Do not choose when |
|---|---|---|---|
| `current-info-search` | Verify a bounded recent or changeable fact | latest, current, today, breaking, new release, price, schedule, rule, officeholder, version | The user needs a comprehensive multi-source report |
| `deep-research` | Produce a rigorous, reusable investigation with adversarial comparison and citation verification | deep research, literature review, evidence map, policy scan, market scan, contested question, compare options, hypothesis | A quick current lookup will answer the question |
| `board-meeting` | Research or summarize public school-board meetings from official records | school board, agenda, minutes, packet, recording, meeting calendar, agenda item | The request concerns corporate boards or general governance |
| `school-system-assessment-contact-research` | Build district leadership and assessment/accountability contact records from an organization universe | district assessment director, accountability leader, testing coordinator, school-system leadership, district workbook | The roster spans general organizations or only one quick contact lookup |
| `organizational-roster-building` | Define a sector/geography and build an evidence-backed universe of organizations | organization roster, universe, sector scan, list organizations, map the field | The organization list already exists and the task is to find people |
| `coordinated-efficient-contact-research` | Find verified public names, roles, emails, phones, and official contact routes for an existing organization roster | contact research, leadership contacts, email addresses, phone numbers, contact routes | The task is to discover the organization universe first |
| `research-conference-presenter-roster` | Build a time-bounded roster of presenters, panelists, moderators, and organizations | conference speakers, presenter roster, panelists, moderators, summit participants | The user only needs a conference schedule or general event summary |
| `stakeholder-identification` | Identify affected parties, decision rights, influence, interests, missing voices, and engagement plans | stakeholder map, influence-interest, engagement plan, decision rights, affected groups | The task is only to compile factual organization or contact records |
| General fallback | Answer a bounded research question that has no specialist workflow | investigate, look into, explain with sources, find evidence, compare a small set | The answer is high-stakes or comprehensive enough for `deep-research` |

## Post-research handoffs

After research is complete, route artifact production only when requested:

- Use `board-deck-builder` for a governance or board decision deck.
- Use `narrative-engine` to turn supplied findings into a narrative blueprint, speech, or presentation story.
- Use `documents` for a polished DOCX and `presentations` for a PPTX.
- Use `spreadsheets` for structured XLSX/CSV deliverables.
- Use `agent-decision-receipts` when the user needs an auditable record of a recommendation, delegation, exception, or rollback.

Do not re-run research during a production handoff unless the user requests verification or the artifact exposes a material evidence gap.

## Ambiguity rules

- Prefer output intent over isolated keywords. “Summarize these board minutes” routes to `board-meeting`; “identify stakeholders affected by the board's decision” routes to `stakeholder-identification`.
- Prefer the more specialized route when its required inputs are present.
- Run roster discovery before contact enrichment when no stable organization universe exists.
- Route to `deep-research` when rigor and decision risk outweigh speed, even if a general fallback could technically answer.
- Route to `current-info-search` when freshness is the main difficulty, even if the topic is otherwise ordinary.
- If two routes remain plausible and would produce different artifacts, ask one question that contrasts those artifacts and recommend the likelier route.

## Classifier use

Run:

```text
python scripts/classify_request.py --question "..." --available "deep-research,current-info-search,..." --output json
```

The script uses weighted phrases and reports alternatives. It does not inspect skill installation automatically and does not replace contextual judgment.
