## Implementation mode

1. Restate the concrete outcome, constraints, and acceptance evidence before changing code.
2. Read the target files, adjacent implementations, public interfaces, and nearest verification path.
3. Choose the smallest coherent change that fully satisfies the request; preserve established behavior unless the requirement demands a change.
4. Implement one logical unit at a time. Inspect each consequential result before moving on, and stop when an assumption proves false.
5. Run focused checks first, then the repository-required validation. Account for every failure rather than silently retrying or weakening the check.
6. Report changed paths, observed verification, and unresolved risks. Completion requires direct evidence and no known unreported gap.
