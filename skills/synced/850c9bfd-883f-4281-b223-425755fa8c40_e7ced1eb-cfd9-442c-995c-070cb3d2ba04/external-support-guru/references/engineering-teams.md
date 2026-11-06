# Choosing the receiving team

Read `docs/support-handover.mdx` in the event catalog (`newstore/engineering/hq/tools/event-catalog`, branch `main`, through the GitLab MCP) and follow its method: the owner of the failing service first, then the team whose `supportHandover.pagerDutyBusinessServices` names the capability that failed, then NCS history, then a colleague. Each engineering team page (`teams/team-<slug>.mdx`) carries that block and a "Support handover" section.

If the catalog cannot be read, say so in the report and route from NCS history alone: `project = NCS AND text ~ "<symptom words>" AND issueLinkType is not EMPTY ORDER BY created DESC`, then read the project key of the linked issues. An unsure routing call is a reason to ask another support engineer, not to pick the likeliest box.
