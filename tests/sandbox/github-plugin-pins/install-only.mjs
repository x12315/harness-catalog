/**
 * Install or inspect the two reviewed Git pins using the real relocated Pi SDK.
 * CLI: env -i PATH=... HOME=<scratch> SDK_ROOT=<runtime root>
 * PLUGIN_AGENT_DIR=<cache owner> PLUGIN_CWD=<scratch cwd> node install-only.mjs install|resolve
 * Never persists settings, imports plugin entry points, or creates a Pi session.
 * `install` may reconcile existing managed checkouts: review/authorize that cache first.
 * `resolve` only inspects installed sources and fails on missing/mismatched refs.
 */
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { existsSync, lstatSync, readFileSync, realpathSync, writeFileSync } from 'node:fs';
import { isAbsolute, join, relative, sep } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const mode = process.argv[2];
assert(['install', 'resolve'].includes(mode) && process.argv.length === 3, 'Expected install|resolve');
for (const key of ['SDK_ROOT', 'PLUGIN_AGENT_DIR', 'PLUGIN_CWD', 'HOME']) {
  assert(process.env[key] && isAbsolute(process.env[key]), `${key} must be an explicit absolute path`);
  assert(lstatSync(process.env[key]).isDirectory(), `${key} must exist as a real directory`);
}
assert(!process.env.NODE_OPTIONS && !process.env.NODE_PATH, 'Launch without Node injection variables');
const sdkRoot = realpathSync(process.env.SDK_ROOT);
const agentDir = realpathSync(process.env.PLUGIN_AGENT_DIR);
const cwd = realpathSync(process.env.PLUGIN_CWD);
const home = realpathSync(process.env.HOME);
assert(home !== agentDir && home !== cwd, 'HOME must be a separate scratch directory');
const ignoredEnvironment = Object.keys(process.env).filter(key => /^(PI_|HARNESS_|AI_AGENT$)/.test(key)).sort();
const path = process.env.PATH;
const tmpdir = process.env.TMPDIR;
const npmUserConfig = join(home, 'npm-user-isolated.config');
const npmGlobalConfig = join(home, 'npm-global-isolated.config');
for (const file of [npmUserConfig, npmGlobalConfig]) {
  if (!existsSync(file)) writeFileSync(file, '', { flag: 'wx', mode: 0o600 });
  assert(lstatSync(file).isFile() && !lstatSync(file).isSymbolicLink());
  assert.equal(readFileSync(file).length, 0, 'Isolated npm config must stay empty');
}
for (const key of Object.keys(process.env)) delete process.env[key];
Object.assign(process.env, {
  PATH: path, HOME: home, LANG: 'en_US.UTF-8',
  PI_CODING_AGENT_DIR: agentDir, PI_OFFLINE: '1', PI_TELEMETRY: '0',
  PI_SKIP_VERSION_CHECK: '1', GIT_TERMINAL_PROMPT: '0', GIT_CONFIG_NOSYSTEM: '1',
  GIT_CONFIG_GLOBAL: '/dev/null', NPM_CONFIG_USERCONFIG: npmUserConfig, NPM_CONFIG_GLOBALCONFIG: npmGlobalConfig,
});
if (tmpdir) process.env.TMPDIR = tmpdir;
process.chdir(cwd);
const pins = JSON.parse(readFileSync(new URL('./pins.json', import.meta.url), 'utf8'));
const packageRoot = join(sdkRoot, 'node_modules/@earendil-works/pi-coding-agent');
const managerFile = join(packageRoot, 'dist/core/package-manager.js');
const settingsFile = join(packageRoot, 'dist/core/settings-manager.js');
const { DefaultPackageManager } = await import(pathToFileURL(managerFile).href);
const { SettingsManager } = await import(pathToFileURL(settingsFile).href);
assert.equal(typeof DefaultPackageManager, 'function', 'SDK DefaultPackageManager API mismatch');
assert.equal(typeof SettingsManager?.inMemory, 'function', 'SDK inMemory API mismatch');
const settings = SettingsManager.inMemory({
  packages: pins.map(pin => pin.source),
  npmCommand: ['npm', '--ignore-scripts', '--no-audit', '--no-fund'],
  enableInstallTelemetry: false,
}, { projectTrusted: false });
assert.equal(settings.isProjectTrusted(), false);
assert.deepEqual(settings.getProjectSettings(), {});
const settingsBefore = settings.getSettings();
const manager = new DefaultPackageManager({ cwd, agentDir, settingsManager: settings });
for (const method of ['install', 'resolveExtensionSources', 'getInstalledPath', 'setProgressCallback']) {
  assert.equal(typeof manager[method], 'function', `SDK ${method} API mismatch`);
}
const progress = [];
manager.setProgressCallback(event => {
  progress.push(event);
  console.log(JSON.stringify({ marker: 'github-plugin-pins/progress', ...event }));
});
const commands = [];
function git(root, args) {
  commands.push({ command: 'git', args, cwd: root });
  return execFileSync('git', ['-C', root, ...args], { encoding: 'utf8', timeout: 30000 });
}
function digest(bytes) {
  return createHash('sha256').update(bytes).digest('hex');
}
function inspect(pin) {
  const installedPath = manager.getInstalledPath(pin.source, 'user', { installMissing: false });
  assert(installedPath, `Missing installed package ${pin.source}`);
  const root = realpathSync(installedPath);
  assert(root.startsWith(join(agentDir, 'git') + sep), 'Cache escaped explicit agentDir');
  const head = git(root, ['rev-parse', 'HEAD']).trim();
  assert.equal(head, pin.head);
  const paths = git(root, ['ls-files', '-z', '--', 'extensions', 'package.json']).split('\0').filter(Boolean).sort();
  assert.deepEqual(paths, Object.keys(pin.files).sort(), 'Tracked resource scope changed');
  const hash = createHash('sha256');
  const files = {};
  for (const entry of paths) {
    const full = join(root, entry);
    assert(!lstatSync(full).isSymbolicLink(), 'Unexpected resource symlink');
    const bytes = readFileSync(full);
    files[entry] = digest(bytes);
    assert.equal(files[entry], pin.files[entry], `Resource differs: ${entry}`);
    hash.update(entry).update('\0').update(bytes).update('\0');
  }
  const contentSetSha256 = hash.digest('hex');
  assert.equal(contentSetSha256, pin.contentSetSha256);
  const manifest = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
  assert.equal(manifest.name, pin.name, 'Profile package name changed');
  for (const field of ['dependencies', 'optionalDependencies', 'devDependencies']) {
    assert.equal(Object.keys(manifest[field] ?? {}).length, 0, `Unexpected ${field}`);
  }
  for (const lifecycle of ['preinstall', 'install', 'postinstall', 'prepare', 'prepublish']) {
    assert(!manifest.scripts?.[lifecycle], `Unexpected lifecycle script ${lifecycle}`);
  }
  assert.equal(git(root, ['diff', 'HEAD', '--', 'extensions', 'package.json']), '', 'Tracked resources dirty');
  const status = git(root, ['status', '--porcelain=v1', '--untracked-files=all']);
  const generatedLockfile = existsSync(join(root, 'package-lock.json'));
  return { name: pin.name, source: pin.source, head, installedPath: root, files,
    contentSetSha256, status, generatedLockfile, lockfileExcludedFromResourceHash: true };
}
if (mode === 'install') {
  for (const pin of pins) {
    commands.push({ api: 'DefaultPackageManager.install', source: pin.source, local: false });
    await manager.install(pin.source);
  }
}
const packagesBefore = pins.map(inspect);
const candidateSources = settings.getPackages();
assert.deepEqual(candidateSources, pins.map(pin => pin.source));
commands.push({ api: 'DefaultPackageManager.resolveExtensionSources', installMissing: false, sources: candidateSources });
const resolved = await manager.resolveExtensionSources(candidateSources, { installMissing: false });
assert.deepEqual(Object.keys(resolved).sort(), ['extensions', 'prompts', 'skills', 'themes']);
assert.equal(resolved.extensions.length, 2);
for (const type of ['skills', 'prompts', 'themes']) assert.deepEqual(resolved[type], []);
for (const pin of pins) {
  const pkg = packagesBefore.find(pkg => pkg.source === pin.source);
  const resource = resolved.extensions.find(resource => resource.metadata.source === pin.source);
  assert(resource, `Not resolved: ${pin.source}`);
  assert.equal(resource.enabled, true);
  assert.equal(resource.metadata.scope, 'user');
  assert.equal(resource.metadata.origin, 'package');
  assert.equal(realpathSync(resource.metadata.packageRoot), pkg.installedPath);
  assert.equal(relative(pkg.installedPath, realpathSync(resource.path)), pin.entry);
}
const packages = pins.map(inspect);
assert.deepEqual(packages, packagesBefore, 'Installed-only resolve changed checkout state');
assert.deepEqual(settings.getSettings(), settingsBefore, 'SDK altered candidate settings');
assert.deepEqual(settings.drainErrors(), [], 'SDK settings errors');
assert(!progress.some(event => event.type === 'error'), 'SDK reported errors');
assert(!progress.some(event => mode === 'resolve'), 'Resolve unexpectedly installed or refreshed');
console.log(JSON.stringify({ marker: 'github-plugin-pins/sdk-result', mode, passed: true,
  sdkRoot, sdkVersion: JSON.parse(readFileSync(join(packageRoot, 'package.json'), 'utf8')).version,
  sdkFiles: { packageManager: digest(readFileSync(managerFile)), settingsManager: digest(readFileSync(settingsFile)) },
  helperPath: fileURLToPath(import.meta.url), agentDir, cwd, home, ignoredEnvironment,
  settingsStorage: 'inMemory', settingsPersisted: false, pluginsExecuted: false,
  npmCommand: settings.getNpmCommand(), lockfilePolicy: 'report generated package-lock.json; exclude from tracked resource hash',
  commands, packages, resolved }));
