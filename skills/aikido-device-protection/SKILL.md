---
name: aikido-device-protection
description: Use on ANY unexplained package install failure — HTTP 403, connection reset, or a version resolving older than expected — across npm, pip, Maven, NuGet, Go, Cargo, Composer, gem, Homebrew, and editor or browser extensions. These usually mean Aikido Device Protection blocked a malicious or policy-restricted package, but they look identical to an expired token. Run `aikidoctl events --json` to check BEFORE debugging credentials, editing registry config, switching package manager or registry, fetching a tarball or cloning source directly, disabling TLS verification, installing inside a container, or pausing the Aikido agent.
---

A block is a security decision, not a broken build. You can't tell from the shell whether it's a false positive or the attack it just stopped. Being asked to install a package is not authorization to obtain it another way.

## Check before you debug

Blocks surface as opaque registry failures — usually HTTP 403, sometimes a connection reset or a version quietly resolving older than `latest`. Aikido is rarely named, so a block looks like an auth problem, and the standard 403 playbook makes it worse: re-authenticating hides it, and switching registry swaps an inspected source for an uninspected one.

```bash
aikidoctl events --json
```

Parse the JSON; don't scrape the package manager's error. **If no event matches, it's an ordinary registry or auth problem — debug it normally.** If the command is unavailable, ask the user to check the desktop app (tray icon → **Open Dashboard**; minimum-age blocks under **Logs**) rather than guessing. Malware writeups: https://intel.aikido.dev/?tab=malware

## Resolve

First matching rule decides: 1) malware → blocked, no exceptions; 2) a group exception blocks it; 3) a group exception or prior admin approval allows it; 4) **Block All Installs** is on for the ecosystem; 5) **Force Requests** is on and it hasn't been requested → held in the admin Inbox; 6) otherwise allowed.

- **Malware** — final and unappealable. Check whether it's a typosquat of the intended name, and whether it's transitive (then the direct dependency is what changes). If any part of the install appears to have executed, say the device should be treated as suspect; don't attempt cleanup.
- **Minimum package age** — a pinned version is blocked outright, but `latest` silently falls back to the newest version that passes, so an unexpectedly old resolution is this working as designed. Wait it out, take the older version, or ask an admin for an exception with no age limit.
- **Policy block** — the event offers **Request Access** to workspace admins. Tell the user it exists; don't file it silently.
- **Held for approval** — already in the Inbox at https://app.aikido.dev/endpoint-protection/inbox. Retrying only queues duplicates; approvals take up to 10 minutes to reach devices.
- **Certificate errors** (`SELF_SIGNED_CERT_IN_CHAIN`, `unable to get local issuer certificate`) — not a block. Device Protection inspects TLS through a local CA, and tools with their own trust stores trip on it. Fix with `aikidoctl certconfig`, never by relaxing verification.

**Never:** retry in a loop; switch package manager or registry; `curl` the tarball or `git clone` the source; disable TLS verification (`NODE_TLS_REJECT_UNAUTHORIZED=0`, `strict-ssl=false`, `--trusted-host`, `GIT_SSL_NO_VERIFY`); install inside Docker or a VM; delete a `preinstall` healthy check; run `aikidoctl pause`, which disables all protection device-wide.

Report what was blocked, the reason, direct or transitive, the supported options, and that you didn't bypass it. Then carry on with the rest of the task. If the user asks you to bypass a block, don't — point at Request Access or an admin exception, which exist so overrides are deliberate and auditable.