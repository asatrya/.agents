#!/usr/bin/env node
/**
 * NOM evidence capture in a dedicated Chrome profile, driven over CDP.
 *
 *   node nom-capture.ts open <tenant> <order-id>
 *   node nom-capture.ts goto <nom-url>
 *   node nom-capture.ts controls
 *   node nom-capture.ts click "<visible text>"
 *   node nom-capture.ts fill "<field label>" "<value>"
 *   node nom-capture.ts shot <investigation-dir> <view-name> [--note "what it shows"]
 *   node nom-capture.ts close
 *
 * Every command prints JSON. Exit codes: 0 ok, 1 error, 2 usage, 3 sign-in needed, 4 refused.
 * `shot` masks the live page with mask-nom-pii.js first and refuses to capture unless the
 * mask reports safe, so an unmasked image never exists.
 * On retailer tenants `click` refuses final actions and fails every NOM write request made while
 * it runs, so a flow can be walked up to its last step and no further. Test tenants allow writes.
 */
import { spawn } from "node:child_process";
import { appendFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PORT = Number(process.env.NOM_CHROME_PORT ?? 9333);
const PROFILE = process.env.NOM_CHROME_PROFILE ?? join(homedir(), ".newstore-support", "nom-chrome");
const CHROME = process.env.CHROME_PATH ?? "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const LAST_URL = join(PROFILE, "last-nom-url");
const MASK_SCRIPT = join(dirname(fileURLToPath(import.meta.url)), "mask-nom-pii.js");
const NOM_HOST = /^manager\.[a-z0-9-]+\.p\.newstore\.net$/i;
const CLICKABLE = "button, a, summary, [role=tab], [role=button], [aria-expanded]";
const TEST_TENANTS = new Set(["dodici", "dodici-staging"]);
// The step that commits a flow. A false refusal is the cheap error.
const FINAL_ACTIONS =
	/\b(confirm|submit|save|ok|yes|proceed|apply|send|resend|approve|accept|decline|reject|delete|remove|sync|reindex|upload|import|done|finish|pay|place order|log ?out|sign ?out)\b/i;
const FIELDS = "input, textarea, select";

class Refused extends Error {
	readonly code: number;
	constructor(message: string, code = 4) {
		super(message);
		this.code = code;
	}
}

await main(process.argv.slice(2)).then(
	(result) => {
		print(result);
		process.exit(0);
	},
	(err: Error) => {
		print({ ok: false, error: err.message });
		process.exit(err instanceof Refused ? err.code : 1);
	},
);

async function main([command, ...args]: string[]): Promise<object> {
	switch (command) {
		case "open":
			return open(args[0], args[1]);
		case "goto":
			return goto(args[0]);
		case "controls":
			return controls();
		case "click":
			return click(args.join(" "));
		case "fill":
			return fill(args[0], args[1]);
		case "shot":
			return shot(args);
		case "close":
			return close();
		default:
			throw new Refused("usage: open <tenant> <order-id> | goto <url> | controls | click <text> | fill <label> <value> | shot <dir> <name> [--note text] | close", 2);
	}
}

async function open(tenant?: string, orderId?: string): Promise<object> {
	if (!tenant || !orderId || !/^[a-z0-9-]+$/.test(tenant)) {
		throw new Refused("usage: open <tenant> <order-id>", 2);
	}
	await ensureChrome();
	const url = `https://manager.${tenant}.p.newstore.net/sales/orders/${encodeURIComponent(orderId)}`;
	const page = (await findNomTab()) ?? (await newTab());
	return requireSignedIn(await navigate(page, url));
}

async function goto(url?: string): Promise<object> {
	if (!url || !NOM_HOST.test(safeHost(url))) {
		throw new Refused("goto only opens NOM pages: https://manager.<tenant>.p.newstore.net/...", 2);
	}
	return requireSignedIn(await navigate(await requireNomTab(), url));
}

async function controls(): Promise<object> {
	const page = await requireNomTab();
	await mask(page);
	const labels = await page.evaluate<string[]>(`(() => {
		const seen = new Set();
		for (const el of document.querySelectorAll(${JSON.stringify(CLICKABLE)})) {
			const text = (el.innerText || el.getAttribute('aria-label') || '').trim().replace(/\\s+/g, ' ');
			if (text && text.length <= 60 && el.offsetParent !== null) seen.add(text);
		}
		return [...seen].slice(0, 120);
	})()`);
	const testTenant = TEST_TENANTS.has(tenantOf(await page.url()));
	return { ok: true, url: await page.url(), controls: labels.map((text) => ({ text, allowed: testTenant || !FINAL_ACTIONS.test(text) })) };
}

async function click(text: string): Promise<object> {
	if (!text) {
		throw new Refused("usage: click <visible text>", 2);
	}
	const page = await requireNomTab();
	const testTenant = TEST_TENANTS.has(tenantOf(await page.url()));
	if (!testTenant && FINAL_ACTIONS.test(text)) {
		throw new Refused(`"${text}" commits the flow. On a retailer tenant, stop before it; test the write on dodici.`);
	}
	const blocked = testTenant ? [] : await blockWrites(page);
	const clicked = await page.evaluate<boolean>(`(() => {
		const want = ${JSON.stringify(text)};
		for (const el of document.querySelectorAll(${JSON.stringify(CLICKABLE)})) {
			const label = (el.innerText || el.getAttribute('aria-label') || '').trim().replace(/\\s+/g, ' ');
			if (label !== want || el.offsetParent === null) continue;
			el.click();
			return true;
		}
		return false;
	})()`);
	if (!clicked) {
		throw new Refused(`No visible control labelled "${text}". Run \`controls\` to list them.`, 1);
	}
	await page.settle();
	if (!testTenant) {
		await page.send("Fetch.disable");
	}
	return {
		ok: true,
		clicked: text,
		url: await page.url(),
		...(blocked.length && { blockedWrites: blocked, note: "NOM tried to write and the request was failed. The flow cannot go further on this tenant." }),
	};
}

async function fill(label?: string, value?: string): Promise<object> {
	if (!label || value === undefined) {
		throw new Refused("usage: fill <field label> <value>", 2);
	}
	const page = await requireNomTab();
	const filled = await page.evaluate<boolean>(`(() => {
		const want = ${JSON.stringify(label)};
		const value = ${JSON.stringify(value)};
		const norm = (s) => (s || '').trim().replace(/\\s+/g, ' ');
		for (const el of document.querySelectorAll(${JSON.stringify(FIELDS)})) {
			const names = [el.getAttribute('aria-label'), el.placeholder, el.labels && el.labels[0] && el.labels[0].innerText];
			if (!names.some((n) => norm(n) === want) || el.offsetParent === null) continue;
			if (el.tagName === 'SELECT') {
				const option = [...el.options].find((o) => norm(o.text) === value);
				if (!option) return false;
				el.value = option.value;
			} else {
				// React tracks the native setter; assigning .value directly is ignored.
				Object.getOwnPropertyDescriptor(Object.getPrototypeOf(el), 'value').set.call(el, value);
			}
			el.dispatchEvent(new Event('input', { bubbles: true }));
			el.dispatchEvent(new Event('change', { bubbles: true }));
			return true;
		}
		return false;
	})()`);
	if (!filled) {
		throw new Refused(`No visible field labelled "${label}" (or no option "${value}").`, 1);
	}
	return { ok: true, filled: label, url: await page.url() };
}

/** Fails every NOM request that could write until Fetch.disable. Returns the list it fills. */
async function blockWrites(page: Cdp): Promise<string[]> {
	const blocked: string[] = [];
	page.on("Fetch.requestPaused", ({ requestId, request }) => {
		if (isRead(request)) {
			void page.send("Fetch.continueRequest", { requestId });
			return;
		}
		blocked.push(`${request.method} ${request.url}`);
		void page.send("Fetch.failRequest", { requestId, errorReason: "BlockedByClient" });
	});
	await page.send("Fetch.enable", { patterns: [{ urlPattern: "*", requestStage: "Request" }] });
	return blocked;
}

function isRead(request: { method: string; url: string; postData?: string }): boolean {
	if (["GET", "HEAD", "OPTIONS"].includes(request.method)) {
		return true;
	}
	if (!/(^|\.)newstore\.(net|com|io)$/i.test(safeHost(request.url))) {
		return true;
	}
	if (/\/(oauth|token)\b/i.test(new URL(request.url).pathname)) {
		return true;
	}
	return isGraphqlRead(request.postData);
}

function isGraphqlRead(body?: string): boolean {
	try {
		const ops = [JSON.parse(body ?? "")].flat();
		return ops.length > 0 && ops.every((op) => typeof op?.query === "string" && !/\bmutation\s*[\w({]/.test(op.query));
	} catch {
		return false;
	}
}

function tenantOf(url: string): string {
	return NOM_HOST.test(safeHost(url)) ? safeHost(url).split(".")[1] : "";
}

async function shot(args: string[]): Promise<object> {
	const noteAt = args.indexOf("--note");
	const note = noteAt >= 0 ? args.slice(noteAt + 1).join(" ") : "";
	const [dir, name] = noteAt >= 0 ? args.slice(0, noteAt) : args;
	if (!dir || !name || !/^[a-z0-9][a-z0-9-]*$/.test(name)) {
		throw new Refused("usage: shot <investigation-dir> <view-name> [--note text]; view-name is kebab-case, e.g. payment-timeline", 2);
	}
	const page = await requireNomTab();
	const report = await mask(page);
	if (!report.safe) {
		throw new Refused(`Not captured: ${report.note} Remaining: ${JSON.stringify(report.remaining)}`);
	}
	const png = await page.screenshot();
	// A re-render or lazy load during capture restores real values; only an unchanged page counts.
	const after = await mask(page);
	const fresh = Object.entries(after.masked).filter(([kind, n]) => kind !== "already_masked" && n > 0);
	if (!after.safe || fresh.length) {
		throw new Refused("Not captured: the page changed during capture and new personal data appeared. Run shot again.");
	}
	const shotsDir = join(resolve(dir), "screenshots");
	mkdirSync(shotsDir, { recursive: true });
	const file = join(shotsDir, `${name}.png`);
	writeFileSync(file, png);
	const counts = Object.entries(report.masked).map(([k, v]) => `${k}×${v}`).join(", ") || "nothing masked";
	appendFileSync(join(resolve(dir), "evidence-log.md"), `- \`screenshots/${name}.png\` · ${report.url} · ${counts} · ${note}\n`);
	return { ok: true, file, url: report.url, masked: report.masked };
}

async function close(): Promise<object> {
	if (!existsSync(PROFILE)) {
		return { ok: true, signedOut: true, note: "No NOM Chrome profile exists, so there is no session to clear." };
	}
	await ensureChrome();
	const browser = await connect((await cdpJson("/json/version")).webSocketDebuggerUrl);
	await browser.send("Storage.clearCookies");
	const url = existsSync(LAST_URL) ? readFileSync(LAST_URL, "utf8").trim() : "";
	if (!url) {
		await browser.send("Browser.close").catch(() => undefined);
		return { ok: true, signedOut: true, note: "Cookies cleared. No NOM page was ever opened in this profile, so there was nothing to reload." };
	}
	const page = (await findNomTab()) ?? (await newTab());
	await page.send("Storage.clearDataForOrigin", { origin: new URL(url).origin, storageTypes: "all" });
	if ((await navigate(page, url)).signedIn) {
		throw new Refused("The order still renders after clearing the session. Sign out by hand and record it as outstanding in access-log.md.");
	}
	await browser.send("Browser.close").catch(() => undefined);
	return { ok: true, signedOut: true, note: "Session cleared, sign-in page confirmed, NOM Chrome closed. Any user or role granted for this investigation still needs removing." };
}

async function navigate(page: Cdp, url: string): Promise<{ ok: boolean; signedIn: boolean; url: string }> {
	await page.send("Page.navigate", { url });
	await page.settle();
	const state = await page.evaluate<{ host: string; path: string; password: boolean }>(
		"({ host: location.hostname, path: location.pathname, password: !!document.querySelector('input[type=password]') })",
	);
	const signedIn = NOM_HOST.test(state.host) && !state.password && !/log-?in|sign-?in|auth/i.test(state.path);
	if (signedIn) {
		mkdirSync(PROFILE, { recursive: true });
		writeFileSync(LAST_URL, url);
	}
	return { ok: true, signedIn, url: await page.url() };
}

function requireSignedIn(state: { ok: boolean; signedIn: boolean; url: string }): object {
	if (!state.signedIn) {
		throw new Refused(
			`NOM is asking for sign-in (${state.url}). The operator signs in in the NOM Chrome window, then runs the command again. Never enter credentials.`,
			3,
		);
	}
	return state;
}

async function mask(page: Cdp): Promise<MaskReport> {
	return JSON.parse(await page.evaluate<string>(readFileSync(MASK_SCRIPT, "utf8"))) as MaskReport;
}

async function ensureChrome(): Promise<void> {
	if (await chromeRunning()) {
		return;
	}
	if (!existsSync(CHROME)) {
		throw new Error(`Chrome not found at ${CHROME}. Set CHROME_PATH.`);
	}
	mkdirSync(PROFILE, { recursive: true });
	spawn(CHROME, [`--remote-debugging-port=${PORT}`, `--user-data-dir=${PROFILE}`, "--no-first-run", "--no-default-browser-check"], {
		detached: true,
		stdio: "ignore",
	}).unref();
	for (let i = 0; i < 40; i++) {
		if (await chromeRunning()) {
			return;
		}
		await sleep(250);
	}
	throw new Error("NOM Chrome did not start.");
}

async function chromeRunning(): Promise<boolean> {
	return cdpJson("/json/version").then(
		() => true,
		() => false,
	);
}

async function findNomTab(): Promise<Cdp | undefined> {
	const targets = (await cdpJson("/json/list")) as { type: string; url: string; webSocketDebuggerUrl: string }[];
	const target = targets.find((t) => t.type === "page" && NOM_HOST.test(safeHost(t.url)));
	return target ? connect(target.webSocketDebuggerUrl) : undefined;
}

async function requireNomTab(): Promise<Cdp> {
	if (!(await chromeRunning())) {
		throw new Refused("NOM Chrome is not running. Start with `open <tenant> <order-id>`.", 1);
	}
	const page = await findNomTab();
	if (!page) {
		throw new Refused("No NOM tab is open. Start with `open <tenant> <order-id>`.", 1);
	}
	return page;
}

async function newTab(): Promise<Cdp> {
	const target = await cdpJson("/json/new?about:blank", "PUT");
	return connect(target.webSocketDebuggerUrl);
}

async function cdpJson(path: string, method = "GET"): Promise<any> {
	const res = await fetch(`http://127.0.0.1:${PORT}${path}`, { method, signal: AbortSignal.timeout(2000) });
	if (!res.ok) {
		throw new Error(`CDP ${path}: HTTP ${res.status}`);
	}
	return res.json();
}

function safeHost(url: string): string {
	try {
		return new URL(url).hostname;
	} catch {
		return "";
	}
}

function print(result: object): void {
	process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

function sleep(ms: number): Promise<void> {
	return new Promise((r) => setTimeout(r, ms));
}

function connect(url: string): Promise<Cdp> {
	return new Promise((resolve, reject) => {
		const ws = new WebSocket(url);
		ws.addEventListener("open", () => resolve(cdpSession(ws)), { once: true });
		ws.addEventListener("error", () => reject(new Error(`cannot connect to ${url}`)), { once: true });
	});
}

function cdpSession(ws: WebSocket): Cdp {
	let nextId = 0;
	const pending = new Map<number, { resolve: (v: any) => void; reject: (e: Error) => void }>();
	const handlers = new Map<string, (params: any) => void>();
	ws.addEventListener("message", (event) => {
		const msg = JSON.parse(String(event.data));
		if (msg.method) {
			handlers.get(msg.method)?.(msg.params);
			return;
		}
		const waiter = pending.get(msg.id);
		if (!waiter) {
			return;
		}
		pending.delete(msg.id);
		msg.error ? waiter.reject(new Error(msg.error.message)) : waiter.resolve(msg.result);
	});

	const session: Cdp = {
		on(method, handler) {
			handlers.set(method, handler);
		},

		send(method, params = {}) {
			const id = ++nextId;
			ws.send(JSON.stringify({ id, method, params }));
			return new Promise((resolve, reject) => pending.set(id, { resolve, reject }));
		},

		async evaluate<T>(expression: string): Promise<T> {
			const { result, exceptionDetails } = await session.send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
			if (exceptionDetails) {
				throw new Error(`page script failed: ${exceptionDetails.exception?.description ?? exceptionDetails.text}`);
			}
			return result.value as T;
		},

		url() {
			return session.evaluate<string>("location.href");
		},

		/** Waits until the SPA stops rendering: document complete and body text stable for ~1.5 s, at most 20 s. */
		async settle() {
			let last = "";
			let stable = 0;
			for (let i = 0; i < 40 && stable < 3; i++) {
				await sleep(500);
				const now = await session
					.evaluate<string>("document.readyState + ':' + (document.body ? document.body.innerText.length : 0)")
					.catch(() => "");
				stable = now.startsWith("complete") && now === last ? stable + 1 : 0;
				last = now;
			}
		},

		async screenshot() {
			const { cssContentSize } = await session.send("Page.getLayoutMetrics");
			const clip = { x: 0, y: 0, width: cssContentSize.width, height: Math.min(cssContentSize.height, 12000), scale: 1 };
			const { data } = await session.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: true, clip });
			return Buffer.from(data, "base64");
		},
	};
	return session;
}

type MaskReport = { url: string; safe: boolean; masked: Record<string, number>; remaining: unknown[]; note: string };

type Cdp = {
	on(method: string, handler: (params: any) => void): void;
	send(method: string, params?: object): Promise<any>;
	evaluate<T>(expression: string): Promise<T>;
	url(): Promise<string>;
	settle(): Promise<void>;
	screenshot(): Promise<Buffer>;
};
