# Limitations

Everything these results do not show. The [README](../README.md#limitations) lists the most important.

- **No real use.** Every task is a templated benchmark question on the benchmark's own orgs, which hold
  generated data, asked by a simulated user. Nobody has used crmroute for real work, and it runs only locally.
- **Judge and simulated user.** Both are local qwen3:8b for every system, not the paper's GPT-4o, so the numbers are comparable across the four systems here but not with the paper's tables. The 8B simulated user sometimes misplays its role (it asks the agent for the Id it should give, or repeats a question until the turn limit), which adds noise to multi-turn results. The judge check (κ = 0.95, 39 of 40 agree) covers only 40 items, and its labels were AI-assisted, with every row reviewed by me. It rules out a badly miscalibrated judge, not occasional errors or blind spots the drafting model shares with the judge.
- **ReAct context cap.** Requests above 250K input tokens are scored as the baseline's failure rather than sent. This ended 17 ReAct tasks on the CRMArena-Pro test set (7 with the privacy prompt) and 1 of 90 on the original CRMArena org, and no crmroute task. Counted as ReAct successes instead, crmroute's lead over plain ReAct is no longer significant; its lead over ReAct with the privacy prompt is (`results/robustness_checks.md`).
- **Dev tuning.** The per-task hints encode the benchmark's answer-key conventions, learned on dev tasks and checked against the orgs (`results/dev_tuning.md`); the dev tuning pass took 3.8 Flash from 52.0% to 61.0% on the same 100 dev tasks. ReAct got no such tuning. The hints transfer to test because test uses the same orgs and task generators. Removing them cost 5.3 points single-turn and 10.5 multi-turn on test, drops the sample cannot confirm (`results/ablation_hints.md`); the general rules and answer forms, also partly written from dev, were not ablated. Unchanged on the original CRMArena org, they kept crmroute ahead of ReAct but by a margin n=90 cannot confirm (+5.6 and +6.7 points).
- **Which requests the guard screens.** The benchmark's customer-facing flag, set per task type, decides which sessions get the policy check, so the guard only has to separate confidential requests from two business task types. A deployment would have to screen every customer question, which this does not measure.
- **Router examples and the fresh set.** The router's example file includes 220 of the 408 fresh confidential requests with their labels, and the router's type is a hint to the policy classifier. On the 188 fresh requests outside the file, the fixed agent refused 97.9%, not the overall 99.0%.
- **Sample sizes.** With n=114 business tasks the 95% margin is about ±9 points, with n=38 multi-turn about ±16, and with 42 refusal cases about ±15. A difference is reported as a win only when its paired bootstrap interval excludes zero.
- **Routing fit.** About 11 dev tasks per type per model; the table is noisy by construction. A new org needs its own dev runs with at least 8 tasks per type per model: one Pro org's dev split is too small, and a table borrowed from the other Pro org gave mixed results (+1.9 and -4.8 points, both intervals spanning zero; `results/routing_transfer.json`).
- **Generalization.** Every org measured here (CRMArena-Pro's B2B and B2C, the original CRMArena) comes from the same benchmark family, with templated questions and task context. Transfer to a company's own data and phrasing is untested.
- **knowledge_qa** stays weak: answers are graded by token F1 against short reference phrases, and the agent often grounds its answer in a different article than the reference.
- **Costs** are list-price estimates from usage metadata (cached and thinking tokens included), not an invoice; free-tier runs are counted at list price although they were not billed. A budget alert on the Google Cloud project could not be verified from here (the Budget API is not enabled).
- **Answer keys** are used as released. An open issue by another user questions two of them ([CRMArena issue #24](https://github.com/SalesforceAIResearch/CRMArena/issues/24), no reply yet); I have not checked it.
- **Guard coverage:** on test, 3 of 42 confidential requests were answered (order quantity limits and a product
  exclusion rule). The policy now covers that rule family; the 4 fresh confidential requests still answered read
  like customer-service and financing questions the policy allows, a trade-off kept so that ordinary
  customer-service questions are not refused (`results/fresh_summary.md`).
- **False refusals:** customer-facing business requests are refused far more often than the guard's own count
  suggests. The guard refused 1 of 16 on test (routed, multi-turn) and 1 of 76 on fresh (measured agent only), but
  the solver also declined requests the guard had allowed, replying that the information is confidential: 5 of 16 on
  test in each system (4 of the 6 single-turn knowledge_qa tasks) and 15 of 76 for the fixed agent on fresh (13 of
  36 single-turn knowledge_qa). These counts were first published as guard refusals only and corrected on
  2026-10-31 (`results/robustness_checks.md`, section 2). The test and fresh records do not keep the tool calls, so
  why the solver declined is not visible in them (the checkable-answers runs keep them as receipts).
- **Checkable answers** are certified for one distribution at a time: single-turn templated tasks on the org a
  rule was calibrated on, with this image, these models and this judge. The guarantee is about the calibration
  split (risk at most 10% with 90% confidence) and carries to new tasks only as far as they are exchangeable with
  it; on test the exact 95% upper bound was 12.4% in round 1, 8.0% in round 2 and 8.9% in round 3 (the original
  org). Coverage met round 1's 40% target by 0.5 points and missed the 50% target by 5.0 points in round 2 and
  6.8 in round 3. A receipt check sees whether the cited records exist and were read, not whether they answer
  the question, and the 9 wrong released answers of rounds 1 and 2 and the 7 of round 3 all passed it with three
  runs agreeing. Round 3's convention check covers dates only, failed its own go/no-go checks and is supported on
  fresh tasks for three task types (`results/checkable3_secondary.md`). Round 2's competence map is learned from round 1's runs on the same benchmark: it withholds task
  types that went wrong before and cannot see a type whose errors are new. "Right" is the benchmark's grading
  against its answer key (qwen3:8b as judge), not a person's check; round 3's blinded audit of that key was not
  conducted, and the author's own review found keys that follow rules their task policy does not state
  (`results/checkable3_review.md`). Free-text, BANT and multi-turn answers are
  never released, and three runs cost about three times one run (1.83 and 1.63 runs with adaptive repeats).
  Eight tasks ended in an error in round 1 (three Vertex AI "missing thought_signature" rejections, four expired
  credentials after the host slept, one dropped connection) and eleven in round 2 (dropped connections, the
  harness's 15-minute limit, one MAX_TOKENS ending; one task timed out three times on slow model calls before it
  finished); all were redone by resuming with identical pins (`results/checkable_notebook.md`). Round 3 redid
  three tasks the same way, all dropped connections (946 and 1015 in development, 988 in calibration), and 18 of
  ReAct's tasks ended at the harness's 250K-token cap, counted as its answers (`docs/checkable3_devlog.md`).
- **Prompt Guard** is untested here (no benchmark task is an injection attempt) and fails open: on Groq's free tier, 122 and 159 Prompt Guard calls in the two fresh runs got `429 Too Many Requests` under parallel load, and screening continued without the injection score. A deployment needs a paid tier or a fail-closed rule for it.
- **Stakeholder interviews: not conducted.** `docs/scoping.md` is the unfilled template, and the sensitive-data map (`agent/app/guard/sensitive_fields.yaml`) is a starter built from the schema and the dev split, not from stakeholder input. Every guard result above was measured with that starter map; replacing it with an interview-based never-share list would need a new measurement.
- **Conversations without a logged-in identity:** the harness gives multi-turn tasks no session identity, so the agent binds the first Contact Id the customer states. A deployment must take it from authentication.
- **Published run records** have three redactions: the Google Cloud project id, email addresses at gmail.com and salesforce.com that ReAct's queries returned from the orgs' User records, and local paths. The hints ablation's records, published separately, needed only the first and last (they hold no email addresses). The checkable-answers records of both rounds, also published separately, have the same three redactions (round 2's local paths include those of the worktree some of its streams ran from); their receipts hold the tool results as the agent saw them. Server and container logs are not published.
- **Qdrant local mode:** only one process can open an index folder at a time, so the search server and the retrieval eval need separate copies.
