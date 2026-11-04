# checkable

A research prototype for teams whose agents answer business questions from a database. It releases an answer only
when the answer can be checked, and reports how often released answers are wrong, with a bound you can defend.

The ideas come from [crmroute](../README.md), a CRM agent tested on Salesforce's CRMArena benchmarks in three
pre-registered rounds. This package carries the parts that do not depend on Salesforce or the benchmark. It has no
dependencies beyond Python 3.10.

## What it does

| Module | What it gives you |
|---|---|
| `receipts` | A `Recorder` that wraps your read-only query function and keeps every query and its rows as a receipt. `recheck` re-runs receipts later and says which still return the same rows. |
| `periods` | The period a question names ("winter of 2023", "the past 3 quarters", "last month") and every defensible window for it. Winter 2023 can mean December 2022 to February 2023, December 2023 to February 2024, or January to March 2023. |
| `interpret` | `check` re-runs the agent's deciding query once per reading and says whether its answer holds under all of them. `learn` finds which readings your organisation uses, from questions it has already answered, so the check asks only those. Each check prints a reading table that explains the decision. |
| `release` | Release rules over repeated runs (agreement, refused warning flags, withheld question types, a reading check). `certify` runs fixed-sequence Learn-then-Test on questions with known answers and picks the widest rule whose error rate is certified at most alpha. |

## Try it

```
python examples/winter_demo.py
```

The demo builds a small SQLite table and walks through a case that came up for real in crmroute. The agent reads
"winter of 2023" one way, and the organisation reads it another. The check holds the answer back, and the reading
table shows why.

## Use it

```python
from checkable import Recorder, check, learn, run_readings, Question, Run, agreement_rule, certify

recorder = Recorder(run_sql)                 # your read-only query function: str -> list[dict]
answer = my_agent(question, query=recorder)  # the agent queries through the recorder
receipts = recorder.receipts                 # keep these with the answer

def query_for(reading):                      # the agent's deciding query, rewritten for one reading
    return deciding_sql.format(start=reading.start, end=reading.end)

conventions = learn([(run_readings(q, today, query_for_q, derive, run_sql), key) for q, today, query_for_q, key in answered])
result = check(question, today, answer, query_for, derive, run_sql, conventions=conventions)
print(result.table())                        # pass | fail | unchecked | no_readings, and why

# Calibrate a release rule on questions with known answers (k runs each), strictest rule first.
rules = [agreement_rule(refuse_flags=["tool_error"], withhold_kinds=["free_text"]), agreement_rule()]
cert = certify(calibration_questions, rules, alpha=0.10, delta=0.10)
print(cert.table())                          # commit cert.rule before looking at any test question
```

## What it was measured on

Every number below is from crmroute's runs, not from this package's toy demo. The full write-ups are in
`results/`.

- **Round 3, the original CRMArena org, a held-out test half of 333 questions.** The rule certified on the other
  half released 144 answers with 7 wrong: 4.9%, with an exact one-sided 95% bound of 8.9%
  (`results/checkable3_answers.md`).
- **The reading check on fresh questions.** Readings were pinned from 510 earlier questions' keys. It held back
  8 of 9 wrong unanimous answers in six question types, at a cost of 17.1% of the right ones. On the three
  pre-registered types, it held back 3 of 4 wrong answers at a cost of 5.6% (`results/checkable3_secondary.md`).
  It is not proven in general. On monthly-trend and top-issue questions it held back too many right answers
  during development.
- **Parity.** On all 1,170 round-3 and development questions, `periods` gives the same readings as crmroute's own
  code (`tests/test_checkable_parity.py`).

## Limits

- The certificate assumes new questions are exchangeable with the calibration ones. "Wrong" means wrong against
  the labels you calibrate on, which can themselves be wrong.
- The reading catalog covers dates only: seasons, the year a winter belongs to, rolling or calendar windows, and
  whether today counts. Readings of other phrases ("top", "active customer") need your own slots. You can pass
  extra slots, but no derivation of them is built in.
- `check` needs you to write `query_for` and `derive` for each question type. crmroute did this for six CRM
  question types; free-text answers are not covered.
- Each ingredient has published precedent: receipts, invariance checks over interpretations, and Learn-then-Test.
  What is new here is putting them together in a CRM setting.

## Licence

MIT, as the rest of the repository.
