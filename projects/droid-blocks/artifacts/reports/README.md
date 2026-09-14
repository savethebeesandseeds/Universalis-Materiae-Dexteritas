# Evaluation reports

Official held-out reports are written here only after a policy artifact has
been frozen, reloaded, and accepted by the protocol-eligibility checks.

Files named `*-validation-summary.json` are non-official, validation-only
provenance summaries. They must state that no held-out decision was emitted and
that no test rollout was executed. They are not substitutes for the exclusive
report created by `evaluate-policy`.

Held-out governance is scoped to a release. The pending v3 split and outcomes
cannot influence the v3 artifact, checkpoint, acceptance rule, or claim. Once
the v3 decision is fixed in its official report, its evaluated worlds,
topologies, traces, and outcomes may be explicitly relabeled as known data for
future-version curriculum, replay, diagnostics, or training. A descendant that
uses them must not count them as unseen evidence; it needs a fresh,
preregistered, versioned challenge split kept outside that descendant's own
development loop. No official v3 held-out report exists yet, so the current v3
split remains untouched and pending explicit approval.
