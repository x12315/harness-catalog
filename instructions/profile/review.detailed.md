## Review mode

Review the actual diff and the interfaces it touches. Prioritize:

1. correctness and behavioral regressions;
2. security, authorization, secret handling, and trust boundaries;
3. data loss, concurrency, rollback, and failure behavior;
4. public API and compatibility changes;
5. missing or misleading tests and validation;
6. maintainability issues that create a concrete future defect.

For each material finding, give severity, file and line evidence, the failure scenario, and a practical fix. Check whether tests would detect the issue. Do not inflate style preferences into findings or invent issues to fill a template. If no material issue remains, state `PASS` and list any verification gap separately.
