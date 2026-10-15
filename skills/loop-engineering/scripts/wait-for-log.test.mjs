import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { appendFileSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { test } from "node:test";

const tool = fileURLToPath(new URL("./wait-for-log.mjs", import.meta.url));

function run(file, pattern, seconds) {
  const child = spawn(process.execPath, [tool, file, pattern, String(seconds)]);
  return new Promise((resolve) => child.once("exit", resolve));
}

test("observes existing and appended checkpoints, but bounds missing ones", async () => {
  const dir = mkdtempSync(join(tmpdir(), "wait-for-log-"));
  const log = join(dir, "build.log");
  try {
    writeFileSync(log, "existing\n");
    assert.equal(await run(log, "^existing$", 1), 0);
    const pending = run(log, "^ready$", 2);
    setTimeout(() => appendFileSync(log, "ready\n"), 250);
    assert.equal(await pending, 0);
    assert.equal(await run(log, "^missing$", 0.1), 124);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});
