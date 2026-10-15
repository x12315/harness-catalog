#!/usr/bin/env node
/** Wait for a new matching log entry; exit 0 on match, 124 on timeout, 2 on error. */
import { existsSync, readFileSync, watch } from "node:fs";
import { basename, dirname, resolve } from "node:path";

const [name, expression, duration] = process.argv.slice(2);
const seconds = Number(duration);
if (!name || !expression || !Number.isFinite(seconds) || seconds <= 0) {
  console.error("usage: wait-for-log.mjs <file> <regex> <timeout-seconds>");
  process.exit(2);
}

let pattern;
try {
  pattern = new RegExp(expression, "m");
} catch (error) {
  console.error(`invalid regex: ${error.message}`);
  process.exit(2);
}

const file = resolve(name);
let offset = 0;
let overlap = "";
let observer;
let timer;

function finish(code, message) {
  clearTimeout(timer);
  observer?.close();
  console.error(message);
  process.exit(code);
}

function check() {
  try {
    if (!existsSync(file)) return;
    const bytes = readFileSync(file);
    if (bytes.length < offset) offset = 0;
    const next = overlap + bytes.subarray(offset).toString("utf8");
    offset = bytes.length;
    if (pattern.test(next)) finish(0, "log checkpoint observed");
    overlap = next.slice(-4096);
  } catch (error) {
    finish(2, `cannot read log: ${error.message}`);
  }
}

try {
  observer = watch(dirname(file), (_event, entry) => {
    if (!entry || entry.toString() === basename(file)) check();
  });
  observer.on("error", (error) => finish(2, `cannot watch log: ${error.message}`));
} catch (error) {
  finish(2, `cannot watch log: ${error.message}`);
}
timer = setTimeout(() => finish(124, "log checkpoint timed out"), seconds * 1000);
check();
