"""Receipt checks: does an answer follow from the tool results it rests on?

Deterministic code over a receipt (a list of tool calls with their results; see app/receipts.py).
The same functions run on recorded runs (scripts/release_eval.py), including receipts rebuilt from
the ReAct baseline's trajectories, so the module uses the standard library only and can be loaded
by file path without the agent package.

`check` turns an answer into a claim and reports flags. Hard flags mean the answer cannot be shown
from its receipt: it names an Id no tool result contains, has no tool result at all, does not parse
in the expected form, or declines or abstains instead of answering. Soft flags (budget used up, tool
errors, policy blocks, a "None" with no empty result behind it, an Id seen only in cut-off results)
are signals for the release rule, which decides on them.
"""

import re
from dataclasses import dataclass, field

# Salesforce record Ids, the same pattern as app.guard.sensitive.SF_ID_RE (a unit test keeps them equal).
ID_RE = re.compile(r"\b(?:[0-9][A-Za-z0-9]{2}|a[0-9][A-Za-z0-9]|k[aA][0-9A-Za-z])[A-Za-z0-9]{12}(?:[A-Za-z0-9]{3})?\b")
REFUSAL_RE = re.compile(r"\b(cannot|can't|can ?not|unable to|not able to)\s+(share|provide|disclose|help with|retrieve|access)\b", re.I)
ABSTAIN_RE = re.compile(r"\bcould not verify an answer\b", re.I)
NONE_WORDS = {"none", "null", "n/a", "no", "no violation", "no record", "no records"}
HARD_FLAGS = ("unparsed", "refusal", "abstain", "ungrounded", "no_data")
MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December")
US_STATES = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA", "colorado": "CO",
    "connecticut": "CT", "delaware": "DE", "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
    "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS", "kentucky": "KY", "louisiana": "LA",
    "maine": "ME", "maryland": "MD", "massachusetts": "MA", "michigan": "MI", "minnesota": "MN",
    "mississippi": "MS", "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY", "north carolina": "NC",
    "north dakota": "ND", "ohio": "OH", "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA",
    "rhode island": "RI", "south carolina": "SC", "south dakota": "SD", "tennessee": "TN", "texas": "TX",
    "utah": "UT", "vermont": "VT", "virginia": "VA", "washington": "WA", "west virginia": "WV",
    "wisconsin": "WI", "wyoming": "WY", "district of columbia": "DC",
}
# The same values as app.task_specs.STAGES and BANT (a unit test keeps them equal).
STAGES = ("Qualification", "Discovery", "Quote", "Negotiation", "Closed")
BANT = ("Budget", "Authority", "Need", "Timeline")
VALUE_FORMS = ("state", "month", "stage", "bant")


def _values(text: str, form: str) -> tuple[str, ...]:
    """The form's values found in an answer, or () if it does not name exactly what the form expects."""
    if form == "state":
        found = {c for c in re.findall(r"\b[A-Z]{2}\b", text) if c in US_STATES.values()}
        found |= {code for name, code in US_STATES.items() if re.search(rf"\b{name}\b", text, re.I)}
        return tuple(found) if len(found) == 1 else ()
    vocab = {"month": MONTHS, "stage": STAGES, "bant": BANT}[form]
    found = tuple(v for v in vocab if re.search(rf"\b{v}\b", text, re.I))
    return found if form == "bant" or len(found) == 1 else ()


@dataclass(frozen=True)
class Claim:
    kind: str  # ids | none | value | text | refusal | abstain | unparsed
    values: tuple[str, ...] = ()

    def key(self) -> tuple:
        """What two answers must share to count as the same answer."""
        if self.kind == "ids":
            return ("ids", tuple(sorted({v[:15] for v in self.values})))
        if self.kind == "text":
            return ("text", tuple(sorted(_tokens(" ".join(self.values)))))
        return (self.kind, tuple(sorted(v.lower() for v in self.values)))


@dataclass
class Verdict:
    claim: Claim
    flags: dict[str, int] = field(default_factory=dict)
    support: list[int] = field(default_factory=list)  # receipt entries whose results contain the answer's Ids

    @property
    def ok(self) -> bool:
        return not any(self.flags.get(f) for f in HARD_FLAGS)


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _is_none(text: str) -> bool:
    return text.strip().strip(".").strip().lower() in NONE_WORDS


def parse_claim(answer: str, form: str) -> Claim:
    text = (answer or "").strip().strip("`").strip()
    if not text:
        return Claim("unparsed")
    if ABSTAIN_RE.search(text):
        return Claim("abstain")
    if REFUSAL_RE.search(text):
        return Claim("refusal")
    if _is_none(text):
        return Claim("none")
    if form in ("id", "ids"):
        found = list(dict.fromkeys(ID_RE.findall(text)))
        return Claim("ids", tuple(found)) if found else Claim("unparsed")
    if form in VALUE_FORMS:
        values = _values(text, form)
        return Claim("value", values) if values else Claim("unparsed")
    return Claim("text", (text,))


def same_answer(a: Claim, b: Claim, text_f1: float = 0.5) -> bool:
    """Ids, values and None compare exactly (Ids by their first 15 characters); text by token F1."""
    if a.kind == b.kind == "text":
        return token_f1(" ".join(a.values), " ".join(b.values)) >= text_f1
    return a.key() == b.key()


def token_f1(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    common = sum(min(ta.count(t), tb.count(t)) for t in set(ta))
    if not common:
        return 0.0
    precision, recall = common / len(ta), common / len(tb)
    return 2 * precision * recall / (precision + recall)


def final_turn(receipt: list[dict]) -> list[dict]:
    last = max((int(e.get("turn") or 0) for e in receipt), default=0)
    return [e for e in receipt if int(e.get("turn") or 0) == last]


def check(answer: str, form: str, receipt: list[dict], context: str = "") -> Verdict:
    """Check one answer against its receipt. `context` is text the asker supplied (task context, their
    messages): an Id given there needs no tool result to be named."""
    claim = parse_claim(answer, form)
    flags: dict[str, int] = {k: 1 for k in ("unparsed", "refusal", "abstain") if claim.kind == k}
    ok_entries = [e for e in receipt if e.get("status") == "ok"]
    last = final_turn(receipt)
    flags["no_data"] = int(not ok_entries and claim.kind not in ("refusal", "abstain"))
    flags["budget"] = int(any(e.get("status") == "budget" for e in last))
    flags["errors"] = sum(e.get("status") == "error" for e in last)
    flags["blocked"] = sum(e.get("status") == "blocked" for e in last)
    empty = [e for e in ok_entries if e.get("totalSize") == 0 and e.get("tool") in ("soql_query", "sosl_search")]
    flags["none_without_empty"] = int(claim.kind == "none" and not empty)
    support: list[int] = []
    if claim.kind == "ids":
        context_ids = {i[:15] for i in ID_RE.findall(context or "")}
        ungrounded = cut_only = 0
        for value in claim.values:
            holding = [e for e in ok_entries if value[:15] in {i[:15] for i in ID_RE.findall(e.get("result") or "")}]
            support += [e["n"] for e in holding]
            if not holding and value[:15] not in context_ids:
                ungrounded += 1
            elif holding and all(e.get("truncated") for e in holding):
                cut_only += 1
        flags["ungrounded"] = ungrounded
        flags["truncated_support"] = cut_only
    return Verdict(claim, {k: v for k, v in flags.items() if v}, sorted(set(support)))
