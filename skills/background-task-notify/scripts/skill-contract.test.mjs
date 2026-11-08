import assert from "node:assert/strict";
import { cpSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { test } from "node:test";

const catalog = fileURLToPath(new URL("../../../", import.meta.url));
const text = (path) => readFileSync(join(catalog, path), "utf8");
const json = (path) => JSON.parse(text(path));
const skill = text("skills/background-task-notify/SKILL.md");
const loop = text("skills/loop-engineering/SKILL.md");
const profiles = ["heavy", "medium", "ultralight", "feiyu"];

test("the independent Skill has standard metadata and explicit notification triggers", () => {
  const header = skill.match(/^---\n([\s\S]*?)\n---\n/)[1];
  const allowed = new Set(["name", "description", "license", "compatibility", "metadata", "allowed-tools"]);
  for (const [, field] of header.matchAll(/^([a-z][\w-]*):/gm)) assert.ok(allowed.has(field), field);
  assert.match(header, /^name: background-task-notify$/m);
  assert.match(header, /^description: .*完成后告诉我.*下载完通知我/m);
  assert.match(header, /ownership: catalog-original/);
  assert.ok(text(".gitignore").split("\n").includes("!/skills/background-task-notify/"));
});

test("notification handoff and engineering feedback have no Skill dependency", () => {
  assert.doesNotMatch(loop, /harness task|background-task-notify|后台任务|完成后告诉我|下载完通知我/);
  assert.match(loop, /可观察信号、检查点和预算/);
  assert.match(loop, /## 缩短回路/);
  assert.match(loop, /## 可复用的日志检查点/);
  assert.doesNotMatch(skill, /loop-engineering/);
});

test("the notification guide retains readiness, verification, detachment and retry boundaries", () => {
  for (const command of ["notify status", "notify setup", "start", "status <ID>", "list", "notify <ID>"]) {
    assert.ok(skill.includes(`harness task ${command}`), command);
  }
  for (const contract of ["authorization: authorized", "alerts: enabled", "--verify=", "presentInNotificationCenter", "只补发通知，不重复执行工作", "不重复执行", "不会主动发送聊天消息"]) {
    assert.ok(skill.includes(contract), contract);
  }
  assert.match(skill, /不提供跨退出登录、关机或重启的自动恢复/);
  assert.match(skill, /(?:不能|不要)把交接成功说成工作已完成/);
});

test("the notification Skill composes without loop-engineering installed or selected", () => {
  const status = spawnSync("harness", ["status", "--json"], { encoding: "utf8", timeout: 10_000 });
  assert.equal(status.status, 0, status.stderr);
  const engine = JSON.parse(status.stdout).engine;
  const fixture = mkdtempSync(join(tmpdir(), "background-notify-catalog-"));
  try {
    cpSync(join(engine, "examples/minimal"), fixture, { recursive: true });
    const skillDir = join(fixture, "skills/background-task-notify");
    mkdirSync(skillDir, { recursive: true });
    cpSync(join(catalog, "skills/background-task-notify/SKILL.md"), join(skillDir, "SKILL.md"));
    writeFileSync(join(fixture, ".gitignore"), text(".gitignore").replace(/^!\/skills\/(?!background-task-notify\/)[^\n]+\n/gm, ""));
    const profilePath = join(fixture, "profiles/work.json");
    const profile = JSON.parse(readFileSync(profilePath, "utf8"));
    profile.skills = ["background-task-notify"];
    writeFileSync(profilePath, JSON.stringify(profile));
    const result = spawnSync("harness", [`--catalog=${fixture}`, "compose", "--apply"], { encoding: "utf8", timeout: 10_000 });
    assert.equal(result.status, 0, result.stdout + result.stderr);
    assert.deepEqual(JSON.parse(readFileSync(join(fixture, "adapters/pi/profiles/work.json"), "utf8")).skills, ["background-task-notify"]);
    const codex = readFileSync(join(fixture, "adapters/codex/profiles/work.config.toml"), "utf8");
    assert.match(codex, /skills\/background-task-notify\/SKILL\.md"\s+enabled = true/);
    assert.doesNotMatch(codex, /loop-engineering/);
    assert.equal(existsSync(join(fixture, "skills/loop-engineering")), false);
  } finally {
    rmSync(fixture, { recursive: true, force: true });
  }
});

for (const name of profiles) {
  test(`${name} independently declares both Skills and compiles their Pi/Codex bindings`, () => {
    const source = json(`profiles/${name}.json`);
    const pi = json(`adapters/pi/profiles/${name}.json`);
    for (const id of ["background-task-notify", "loop-engineering"]) {
      assert.equal(source.skills.filter(value => value === id).length, 1);
      assert.equal(pi.skills.filter(value => value === id).length, 1);
      const blocks = [...text(`adapters/codex/profiles/${name}.config.toml`).matchAll(/\[\[skills\.config\]\]\s+path = "([^"]+)"\s+enabled = (true|false)/g)];
      const matches = blocks.filter(([, path]) => path.endsWith(`/skills/${id}/SKILL.md`));
      assert.equal(matches.length, 1, `${id}: one Codex binding`);
      assert.equal(matches[0][2], "true", `${id}: enabled in Codex`);
    }
    assert.deepEqual(pi.tools, source.adapters.pi.tools);
    assert.deepEqual(pi.extensions, source.adapters.pi.extensions);
    assert.equal(pi.defaultProvider, source.adapters.pi.model.provider);
    assert.equal(pi.defaultModel, source.adapters.pi.model.id);
  });
}
