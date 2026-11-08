# Feiyu Harness

## Goal and scope

Create a new `feiyu` Profile labeled `肥鱼harness`, referencing medium and ultralight, incorporating ultralight's current skill additions, and targeting the previously requested DeepSeek V4 Flash. Do not modify the existing Profile sources or global defaults. No dependency installation, credential changes, commits, or pushes are requested.

## Acceptance

- New Catalog source uses existing instruction entries with medium-weight execution guidance and an explicit skill allowlist combining medium and ultralight.
- Pi recommends the locally available DeepSeek Flash model and a supported thinking level; tools/extensions include ultralight's subagent capability.
- Codex has an explicitly documented supported alternative, not an automatic fallback to DeepSeek.
- Generate native adapter configurations, apply exact projections, and pass `harness doctor`; preserve unrelated working-tree changes.
- Document launch/switch commands and distinguish runtime/configuration checks from actual model-quality validation.

## Progress and evidence

- `harness status --json`: Catalog `/Users/montana/.agents`, Engine `/Users/montana/agent-harness`, API v1; composition and 25 existing projections healthy.
- Read Catalog/Profiles/Engine READMEs, profile schema, existing three Profiles, adjacent instruction entries, and relevant skills.
- `pi --list-models deepseek`: `deepseek/deepseek-flash` is available. Installed catalog names that ID DeepSeek V4.1 Flash and supports low/high/max, not medium. Reuse this available ID rather than inventing a V4 ID; document alias semantics.
- Existing unrelated modifications are present in both repositories. Preserve them; do not reset, stage, commit, or push.

- Created `profiles/feiyu.json`: medium's three standard instructions and Codex alternative, exact union of 42 skills, ultralight's tool/extension lists, Pi `deepseek/deepseek-flash` with `high` thinking.
- Updated `profiles/README.md` with intent, alias semantics, runtime/model-selection caveats, and launch/switch commands.
- Targeted assertions passed: instruction/Codex parity with medium, exact 42-skill union, tool/extension parity with ultralight.
- `harness compose --apply` exited 0: created only the two feiyu adapter files (17 modules, 4 Profiles).
- `harness bootstrap --apply` exited 0: 25 existing projections unchanged, one new Codex feiyu projection created.
- Pre-change public source/generated snapshots: `/var/folders/nw/m2218_wx4kz8hd2k0r4xfyqr0000gn/T/feiyu-harness-DMObBs` (no credentials or session content).

- Preservation/generated-output assertions passed: original three Profile sources and their six generated adapters, root README and AGENTS unchanged from snapshot; feiyu Pi fields match source; native Pi/Codex projections resolve to exact Catalog-owned files.
- `git diff --check` exited 0.
- `harness doctor` exited 0. All stages passed: composition, bootstrap dry-run (26 exact projections), reconcile (44 declared + 7 own skills), secrets scan, both-repository separation, adapter contract, subagent tool boundary, Pi discovery, real Profile control canary (zero model turns), all four Pi and Codex Profiles, and control plane. Verify duration: 82.179 seconds. Observed installed runtimes: Pi 1.1.0 / codex-cli 0.157.1.

## Completion and validation limits

All configuration acceptance items are complete. No Engine files, dependencies, global defaults, or old Profile sources were changed. No commit or push was made. Actual DeepSeek model-quality/API task evaluation was not run; doctor proves installed configuration/runtime discovery, not model task quality. The local available Flash alias currently names V4.1, not a pinned V4.0 release.

## Next use

- Existing Pi: `/harness switch feiyu`, then confirm actual model (hot switching can preserve the current model).
- External terminal, explicit Flash selection: `pi-profile feiyu --model deepseek/deepseek-flash --thinking high`.
- Codex alternative only: `codex -p feiyu`.

No blocker or unfinished configuration work.
