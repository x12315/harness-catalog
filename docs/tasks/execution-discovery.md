# Separate shortest-path insight from pragmatic engineering judgment

## Goal

Improve Harness behavior after it proposed custom robot motion before discovering the existing Set1/Set2 preset path. User explicitly separates two concerns: (1) extend ponytail from minimal coding to discovering the shortest feasible execution path; (2) choose a suitable independent form for evidence-driven engineering risk/gap identification and repair, not procedural safety assurances.

## Scope and constraints

Catalog changes only unless discovery proves an Engine interface gap. Keep mandatory permission, credential and truthfulness boundaries; do not edit or discard existing dirty safety/lock/generated changes. No robot/camera/serial actions. No commits or pushes. Third-party installed content must not become a silently modified cache: preserve original per-file snapshot, use original authored Catalog skill source or a fixed reviewed upstream dependency. Generated artifacts change through compose only.

## Acceptance

- ponytail triggers for authorized operational/troubleshooting tasks as well as coding; existing UI/commands/protocols and tested paths are discovered before new implementation; discovery is bounded by decision-relevant evidence, not an exhaustive research ritual.
- Independent engineering-judgment instruction is always available across profiles, identifies concrete failure mechanisms/unknowns and adds proportionate verifiable protections; neither existing chains nor tests constitute blanket proof, and unknown command outcomes do not trigger blind retries.
- No compulsory long checklist, duplicated safety skill, new generic control framework or automatic behavior/runtime bypass.
- Preserve existing minimal-code guidance where it applies, without code-first output requirements on non-code tasks.
- Validate ownership, Profile discovery, generated entries, source content and representative decision scenarios; run compose/reconcile/doctor. Report prompt content checks separately from actual model behavior validation; remind reload.

## Findings / progress

- Catalog `/Users/montana/.agents`, Engine `/Users/montana/agent-harness`, API v1. All three profiles already select ponytail.
- Initial ponytail was an ignored third-party install from DietrichGebert/ponytail with a coding-only trigger and code-first output. It has no local source override mechanism; modifying it in place would be lost on restore and misdeclare its origin.
- Repository instruction entries support independent brief/standard/detailed source texts plus selection.json; suitable for shared engineering judgment without weakening mandatory safety.
- Existing dirty changes include mandatory safety source/generated artifacts and documentation-writer lock source. Preserve them.

## Completed

- Snapshot and per-file identity: `/Users/montana/.local/state/harness/content-changes/20261020T101118Z/`. Original skill had one file, read completely and retained outside the Catalog; replacement is original authored content, not vendored third-party text.
- Used pinned official `skills@1.7.0 remove ponytail --global --yes`, then created Catalog-owned same-name `skills/ponytail/SKILL.md` and `.gitignore` whitelist. Asserted lock difference removes only ponytail and every other lock entry, including dirty documentation-writer source, remains unchanged. Three Profiles keep the existing ponytail reference. No manual lock edit, hidden cache patch, commit or push.
- ponytail now covers finding and validating operational paths as well as code, prioritizes actual existing UI/configuration/services and decision-relevant evidence, retains minimal implementation when needed, removes coding-only/code-first and fixed three-line reporting demands. `skills/ponytail/evals.md` records independent calibration scenarios, not a mandatory runtime process.
- Added independent `instructions/repository/25-engineering-judgment{,.brief,.detailed}.md`, selected standard globally. Risk/gap judgment is available across Profiles without loading ponytail and remains separate from path selection. Existing mandatory safety source is byte-identical to its pre-change dirty snapshot.
- `harness compose --apply` regenerated global AGENTS and three Codex profiles. Read-only compose/reconcile/catalog verify and diff checks passed:17 modules,3 Profiles,44 declared third-party +7 own =51 installed; no missing or unregistered skills,25 exact projections valid.
- Static content checks cover independent selection, three source detail levels, source ownership, all Profile references and generated entries. An isolated read-only agent exercised four hypothetical decisions (existing Home path; pre-submit query failure; ambiguous delete outcome; already authorized privilege with a non-code fix) without executing them. These checks do not demonstrate real hardware safety or broad model behavioral reliability.
- Final `harness doctor` exit0 in42.84s; report `doctor.json`, log `doctor.log` and `content-checks.json` in the snapshot directory. No Engine code or check execution path changed; no benchmark or control-plane implementation change required.

## Follow-up: add paths only when needed

User clarifies that the organizing principle is not “write code only when needed” but “add execution paths only when needed.” Updated ponytail description, decision framing, addition section, full intensity and examples accordingly. Existing-path discovery/repair and code reading remain available; new commands, interfaces, procedures, manual transfers, approvals and control channels receive the same necessity test as new code. A concrete gap favors repairing the original path when appropriate, not automatically creating another system; genuine requested new capability is not refused merely for requiring a path addition. README and two calibration cases updated; the independent engineering-judgment instruction remains unchanged. Pre-change snapshots: `/Users/montana/.local/state/harness/content-changes/20261020T101859Z/`.

## Follow-up: structural fitness and compatibility rationale

Added the user's constraint to ponytail: verify the relevant existing path is well-formed (clear responsibility/contracts, state and resource ownership, observable failure/recovery), not merely present or once runnable. Before starting a separate path, explain the concrete new requirement versus existing contract/design constraint, supporting evidence, and why local repair/extension/composition is inappropriate; state coexistence/migration boundaries without discarding still-valid capabilities. Avoid both blind reuse and replacement based on taste or vague incompatibility. This is a decision requirement when proposing a replacement, not a universal reporting checklist or demand to audit the whole facility. Added two calibration cases; independent risk instruction unchanged. Snapshot: `/Users/montana/.local/state/harness/content-changes/20261020T115920Z/`.

## Remaining / activation

Implementation and installed-state verification complete. Existing running agents need `/reload` or Profile reselection to load new skill descriptions and instructions. No automatic reload, robot action or promise of universally safe behavior. Observe future real tasks against concrete outcomes and refine targeted counterexamples rather than adding procedural checklists.
