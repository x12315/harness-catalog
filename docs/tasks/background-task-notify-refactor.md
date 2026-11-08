# Background task notification Skill separation

## Goal and scope
Extract background task handoff/completion notifications into the independent Catalog-owned `background-task-notify` Skill. Restore `loop-engineering` to engineering feedback loops. Preserve the already tested Engine `harness task` implementation and all existing unrelated changes.

User-approved scope: refactor, test, report. Maintain notification coverage in the four current Profiles without changing their tools, extensions, models or instructions. Generate adapter files through compose, never edit generated files directly. No host notification permission changes, session reload, commits or pushes.

## Completion criteria
- Notification trigger, handoff, verification and retry guidance belongs solely to the new Skill; it does not depend on loop-engineering.
- Loop-engineering no longer advertises or implements notification handoff.
- Own-Skill Git whitelist and all four Profile references are correct; generated Pi/Codex profiles discover the independent Skill.
- Content/configuration regression tests, existing task backend regressions, and harness doctor report actual exit codes.
- Distinguish current test results from previous Sandbox acceptance. Once the backend status race was found and minimally fixed, rerun actual Sandbox notification acceptance for the changed code.

## Progress
- Read current Catalog entry docs, Profile schema, both Skill sources and Engine task API guide.
- Confirmed four explicit Profile allowlists currently expose notification guidance only through loop-engineering.
- Existing Engine and Catalog dirty changes preserved. Pre-refactor source snapshot: `/Users/montana/.local/state/harness/refactors/background-task-notify-20261104T181223`.
- New independent Skill, whitelist entry and four Profile declarations created. Notification body/trigger removed from loop-engineering without resetting unrelated prior edits. Updated README ownership descriptions and generated eight adapter profiles through compose.
- Content/configuration tests: 9/9 passed, including all four source/Pi/Codex bindings, loop checkpoint helper, and an isolated minimal Catalog containing only the new Skill (loop-engineering neither installed nor selected). First run exposed an overly literal test assertion (不要 versus 不能), corrected without weakening the guide's meaning.
- Backend regression initially failed: a missing executable could be reported as interrupted instead of failed. Diagnosed a read-state/process-exit race. Two deterministic tests reproduced stale business results and stale notification receipts before the fix. Minimal Engine exception to the preserve-implementation scope: reread the final persisted state after observing worker exit before classifying interruption/unknown. Worker, notifier and public CLI contract otherwise unchanged. Backend tests now 14/14 passed.

- Baseline comparison confirmed the only change to each of the four source Profiles is adding `background-task-notify`; all model/tool/extension/instruction fields preserved.
- Fresh Sandbox run `/Users/montana/ahsb-build/runs/macos-background-notification/20261104T102002Z-88063`: guest rc 0, assert PASS, runner exit 0. Real file verification, failed command 23, detached launcher exit and notification-only retry all passed. Success OS receipt 2.319s, failure 1.456s; success AX text and actual failure/retry screenshot reviewed. No host notifier app or preferences changed.
- Full control plane passed all 12 layers (exit 0); existing doctor-benchmark unit tests passed (exit 0): `/tmp/background-skill-refactor-validation.log`. First doctor attempt exited 1 because its nested control plane reached the unchanged 150s total budget during Pi model scope RPC. Failure preserved; no unrelated time budgets or checking paths changed.
- Standard doctor recheck passed (exit 0): `/tmp/background-skill-refactor-doctor-recheck.log`; control plane 127.154s, complete verify 128.140s. Covers both-repo interface/hygiene, generated profiles, dependencies, secrets, Pi/Codex discovery/runtime, adapter exports and all 27 exact projections. Runtime discovery found 55 Skills including the new owned Skill; ownership counts 44 shared + 11 owned, no unregistered resources.
- Final content/configuration rerun 9/9 passed; backend 14/14 passed. Both repositories' diff whitespace checks pass. New Skill and contract test are visible to Git under the new whitelist. All ten current backend/fixture input hashes still match this task's successful Sandbox snapshot.
- No release or check scheduler changes; no performance benchmark claimed. All temporary test Catalogs and owned Sandbox clones cleaned up; base VM and unrelated dirty changes preserved.

## Final status and activation
The requested Skill separation, Profile wiring, generated outputs and testing are complete. The backend exception was limited to the race discovered by testing; worker/notifier execution and public CLI contract are otherwise unchanged. First failed assertions, deterministic red tests and the timed-out doctor attempt are preserved above rather than represented as passes.

Running agents still need `/reload` or Profile reselection to load `background-task-notify`; no session has been force-refreshed. Host notification setup/permission was not changed or tested outside Sandbox. No commit/push performed.
