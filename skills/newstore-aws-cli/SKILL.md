---
name: newstore-aws-cli
description: >-
  Refreshes expired Newstore AWS SSO credentials for kubectl, EKS, and AWS CLI.
  Use immediately when a Newstore AWS or kubectl command fails with ExpiredToken,
  ExpiredTokenException, "credentials are expired", SSO session expired,
  "InvalidClientTokenId", "unknown flag -u" from aws-sso, "Unable to connect to
  the server" from aws eks get-token, or unauthenticated AWS CLI — including
  mid-task when the original request was not authentication. Also use when the
  user asks for credentials for a Newstore account or stage (staging,
  production, recovery). Do not ask the user to run aws-sso-profile or refresh
  SSO first. Newstore profiles only (for example
  newstore-s-team-sfcc:AWSAdministratorAccess).
metadata:
  short-description: "Refresh expired Newstore AWS CLI sessions"
---

# Newstore AWS CLI authentication

Use only in the Newstore context. Do not use for Personal work or an unrelated AWS account. Do not edit `~/.aws/config`, change the selected profile, or create AWS resources as part of authentication.

## Mid-task trigger

Invoke this skill as soon as a Newstore AWS-backed command fails for expired or missing credentials. Auth is a new task; re-pick even if this skill was not selected at conversation start and even if the user did not mention AWS or SSO.

Do not stop and ask the user to refresh SSO, run `aws-sso-profile`, or retry after they log in. Authenticate in this shell, then rerun the failed command.

The only user action allowed is completing an on-screen browser OTP/MFA/security challenge. Never handle or expose passwords, OTPs, or recovery codes.

## Workflow

Three steps: log in, pick the profile, load the credentials.

### 1. Log in

```bash
aws-sso login
```

This opens the SSO sign-in in the browser. If the user must complete a browser sign-in, OTP, or MFA challenge, ask them to do that and wait. If it prints nothing and exits 0, the login succeeded; confirm in step 2 (the header shows `Expires in: <time>`).

If the CLI does not open a visible tab, read `StartUrl` from `~/.config/aws-sso/config.yaml` and open that exact URL; never guess an SSO URL.

### 2. Find the profile with `aws-sso list`

```bash
aws-sso list
```

Read the **whole** output. Do not truncate it with `head`/`tail`: the role list is short, and a cut-off list can hide the account you need.

The `Expires` column shows `Expired` for every role right after login. That is expected: role credentials are fetched when a profile is loaded in step 3.

Account aliases follow `newstore-<stage>-<team>`, where the stage letter is:

| Letter | Stage |
|---|---|
| `s` | staging |
| `p` | production |
| `r` | recovery |

Examples: `newstore-s-team-sfcc` is the SFCC staging account, `newstore-p-team-sfcc` is SFCC production, `newstore-r-team-sfcc` is SFCC recovery.

The profile name is in the `Profile` column, for example `newstore-s-team-sfcc:AWSAdministratorAccess`. Pick it in this order:

1. The profile already used in the failed command or this conversation.
2. A profile the user just named.
3. The row that matches the team and stage the user asked for.

If the stage or team is ambiguous, or the matching row is missing from the list, stop and ask. Do not guess, and never fall back to a different stage. In particular, do not pick production (`p`) because it is the only match you can find. Do not invent an account or role.

If you need to match an account ID from a manifest (for example a Flux `apps/<stage>` overlay) to a stage, match it against the `AccountIdPad` column.

### 3. Load the credentials

```bash
eval $(aws-sso -L error eval -p '<profile>')
```

For example `eval $(aws-sso -L error eval -p 'newstore-s-team-sfcc:AWSAdministratorAccess')`.

Rules for this step:

- **Never pipe or redirect the `eval`** (no `| tail`, no `2>&1 | ...`). A pipe runs `eval` in a subshell and the exported variables are lost.
- **Each Bash tool call is a fresh shell.** The variables do not carry over between calls. Start every call that needs AWS access with the `eval` line, then run the command in that same call.
- **Verify** in the same call:

  ```bash
  eval $(aws-sso -L error eval -p '<profile>'); aws sts get-caller-identity
  ```

  Check that `Account` is the account you expect for the stage you picked.
- **Never print credential values.** To check what is set, use `env | grep -i '^AWS_' | sed 's/=.*/=<set>/'`. Do not echo `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, or `AWS_SESSION_TOKEN`, and do not save them to files or include them in commentary.
- The session lasts until `AWS_SSO_SESSION_EXPIRATION`. On expiry, repeat from step 1.

The environment credentials are inherited by AWS-backed tools such as `kubectl`, whose exec plugin runs `aws eks get-token`.

### Fallback: `aws-sso exec`

If `eval` cannot be used, run a single command with credentials without touching the environment or config:

```bash
aws-sso exec --profile '<profile>' -- <command>
```

## Do not use these

- **`aws-sso-profile <profile>`**: a shell function that exports variables into your interactive shell. In a Bash tool call it prints nothing and leaves no variables set.
- **`aws ... --profile <profile>`**: the `credential_process` lines that `aws-sso` generated into `~/.aws/config` may use the old `aws-sso -u open ...` syntax, which `aws-sso` 2.x rejects with `unknown flag -u`. The failure looks like `Error when retrieving credentials from custom-process`. Use step 3 instead, which does not go through the config file.

## Failures

- `InvalidClientTokenId` or `ExpiredToken` after step 3: the variables were probably not exported. Check for a pipe on the `eval`, or run the `eval` in the same call as the command.
- `aws-sso login` prints nothing and `aws-sso list` shows no roles: the login did not complete. Ask the user to finish the browser sign-in.
- Step 3 still fails after a fresh login: stop and report the exact non-secret error. Do not retry in a loop.

## Important boundary

This workflow authenticates the terminal for the current command only; it does not repair the persisted `credential_process` lines in `~/.aws/config`. Regenerating them (`aws-sso config-profiles`) rewrites that file and is a separate task that needs explicit user direction.
