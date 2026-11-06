---
name: newstore-aws-cli
description: >-
  Refreshes expired Newstore AWS SSO credentials for kubectl, EKS, and AWS CLI.
  Use immediately when a Newstore AWS or kubectl command fails with ExpiredToken,
  ExpiredTokenException, "credentials are expired", SSO session expired,
  "Unable to connect to the server" from aws eks get-token, or unauthenticated
  AWS CLI — including mid-task when the original request was not authentication.
  Do not ask the user to run aws-sso-profile or refresh SSO first. Newstore
  profiles only (for example newstore-s-team-data-provisioning:AWSAdministratorAccess).
metadata:
  short-description: "Refresh expired Newstore AWS CLI sessions"
---

# Newstore AWS CLI authentication

Use only in the Newstore context. Do not use for Personal work or an unrelated AWS account. Do not edit `~/.aws/config`, change the selected profile, or create AWS resources as part of authentication.

## Mid-task trigger

Invoke this skill as soon as a Newstore AWS-backed command fails for expired or missing credentials. Auth is a new task; re-pick even if this skill was not selected at conversation start and even if the user did not mention AWS or SSO.

Do not stop and ask the user to refresh SSO, run `aws-sso-profile`, or retry after they log in. Authenticate in this shell, then rerun the failed command.

The only user action allowed is completing an on-screen browser OTP/MFA/security challenge. Never handle or expose passwords, OTPs, or recovery codes.

## Profile

Keep the profile name quoted. Prefer, in order:

1. The profile already used in the failed command or this conversation.
2. A profile the user just named.
3. If none is known, stop and ask for the profile name (and role ARN if that is also missing). Do not invent an account or role.

Example: `newstore-s-team-data-provisioning:AWSAdministratorAccess`.

## Workflow

1. Inspect only that profile’s credential-process definition:

   ```bash
   PROFILE_NAME='newstore-s-team-data-provisioning:AWSAdministratorAccess'
   CREDENTIAL_PROCESS="$(aws configure get credential_process --profile "$PROFILE_NAME")"
   ```

   Extract the role ARN (the current Newstore format contains `--arn`):

   ```bash
   ROLE_ARN="$(printf '%s\n' "$CREDENTIAL_PROCESS" | sed -nE 's/.*--arn(=|[[:space:]]+)([^[:space:]]+).*/\2/p')"
   ```

   If no role ARN is present, stop and ask for the intended role ARN; do not invent an account or role.

2. Authenticate the AWS SSO browser session when needed. Run `aws-sso login` and use the connected Chrome browser for the sign-in flow. If the CLI does not open a visible tab, read the `StartUrl` from `~/.config/aws-sso/config.yaml` and open that exact URL in Chrome; never guess an SSO URL. If credentials, an OTP, or an MFA/security challenge are required, leave the page ready and ask the user to complete it.

3. Force-refresh the role credentials with the modern subcommand-first syntax. Do not replay a legacy `credential_process` string such as `aws-sso -u open ... process ...`, because the global flags may be rejected before the subcommand:

   ```bash
   ROLE_ARN='arn:aws:iam::...:role/AWSAdministratorAccess'
   AWS_SSO_JSON="$(aws-sso process --arn "$ROLE_ARN" --sts-refresh)"
   ```

   Treat `AWS_SSO_JSON` as secret material. Do not print it, save it to a file, or include its fields in commentary or logs.

4. Use the temporary credentials only in the shell that performs the requested AWS operation. Unset profile selectors so the broken/expired `credential_process` is not invoked again:

   ```bash
   unset AWS_PROFILE AWS_DEFAULT_PROFILE
   export AWS_ACCESS_KEY_ID="$(printf '%s' "$AWS_SSO_JSON" | jq -r '.AccessKeyId')"
   export AWS_SECRET_ACCESS_KEY="$(printf '%s' "$AWS_SSO_JSON" | jq -r '.SecretAccessKey')"
   export AWS_SESSION_TOKEN="$(printf '%s' "$AWS_SSO_JSON" | jq -r '.SessionToken')"
   aws sts get-caller-identity
   ```

   Run the user-requested AWS CLI command in this same shell. These environment credentials are also inherited by AWS-backed tools such as `kubectl` when their exec plugin invokes `aws eks get-token`.

5. Report the authentication result and the requested command result, but never report credential values. If `aws-sso process --sts-refresh` still fails after the browser session is authenticated, stop after the failed refresh and report the exact non-secret error instead of retrying in a loop.

## Important boundary

This workflow authenticates the terminal for the current command only; it does not repair the profile’s persisted `credential_process`. A permanent profile repair is a separate task and requires explicit user direction.
