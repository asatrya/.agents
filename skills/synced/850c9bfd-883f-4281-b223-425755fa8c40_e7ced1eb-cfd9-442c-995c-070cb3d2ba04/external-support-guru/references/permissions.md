# Standard permissions

One-time setup that stops the permission prompt on every read during a triage, while keeping a
prompt — or a hard block — on anything that writes.

The principle: reading is the investigation, so reading is pre-approved. Writing is the
exception the hard rules already restrict, so writing always asks or is blocked. Never ask an
operator to "always allow" a tool in the _Ask_ or _Block_ lists below, even to save a click.

## Three tiers

| Tier | Setting | What goes in it |
|---|---|---|
| Always allow | No prompt | Every read-only tool the workflow calls |
| Ask every time | Prompt per call | Writes the skill may make after explicit per-ticket confirmation (filing, internal note) and reads that cost money |
| Block | Never runs | Writes the hard rules forbid outright |

## Always allow — MCP read tools

| Connector | Tools |
|---|---|
| Atlassian | `getAccessibleAtlassianResources`, `atlassianUserInfo`, `getJiraIssue`, `searchJiraIssuesUsingJql`, `getJiraIssueRemoteIssueLinks`, `getIssueLinkTypes`, `getVisibleJiraProjects`, `getJiraProjectIssueTypesMetadata`, `getJiraIssueTypeMetaWithFields`, `getTransitionsForJiraIssue`, `lookupJiraAccountId`, `getConfluencePage`, `getConfluencePageDescendants`, `getConfluencePageFooterComments`, `getConfluencePageInlineComments`, `getConfluenceCommentChildren`, `getConfluenceSpaces`, `getPagesInConfluenceSpace`, `searchConfluenceUsingCql`, `search`, `fetch`, `getTeamworkGraphContext`, `getTeamworkGraphObject`, `getCompassComponent`, `getCompassComponents`, `getCompassCustomFieldDefinitions`, `getContentFormatGuide` |
| Dash0 | Allow all: every tool is read-only |
| Sentry | `find_organizations`, `find_projects`, `search_issues`, `search_errors`, `search_logs`, `search_traces`, `search_metrics`, `search_profiles`, `search_replays`, `get_sentry_resource`, `find_dropped_events`, `search_sentry_tools` |
| Amplitude | `get_amplitude_context`, `query_amplitude_data`, `get_amp_taxonomy`, `search_amp_data_taxonomy`, `search_amp_entities`, `get_amplitude_charts`, `render_amplitude_chart`, `get_from_url`, `get_amp_user_data`, `get_amp_session_replay_info`, `render_amp_session_replay`, `get_group_types`, `get_tracking_plan_sources`, `get_transformations`, `get_data_warehouse_destinations`, `get_amplitude_agent_analytics_info` |
| Claude in Chrome | `tabs_context_mcp`, `tabs_create_mcp`, `tabs_close_mcp`, `navigate`, `read_page`, `get_page_text`, `find`, `computer`, `javascript_tool`, `read_console_messages`, `read_network_requests` |

Claude in Chrome is the one exception to "read-only". `computer` and `javascript_tool` can click
and run script, and both are needed on every NOM page (screenshots, masking). Pre-approving them is
the support engineer's call. The read-only rule for NOM binds what the skill does on its own, not the browser.

## Always allow — local tools

`Read`, `Glob`, `Grep`, task/todo tools, `AskUserQuestion`, `WebSearch`, `WebFetch` on
`docs.newstore.com` and `docs.fiskaltrust.eu`, `Write`/`Edit` limited to the investigation
directory (`/mnt/user-data/outputs/<NCS-key>/`, or `~/.claude/memory/investigations/<NCS-key>/` where that folder does not exist), and `Bash` limited to `scripts/validate-record.py`,
`scripts/redact-investigation-files.py` and `scripts/nom-capture.ts`. Cowork does not prompt for these; there the investigation
files go to the session's outputs folder and show in the sidebar.

## Ask every time / Block

| Connector | Tool | Tier |
|---|---|---|
| Atlassian | `createJiraIssue` | Ask every time |
| Atlassian | `createIssueLink` | Ask every time |
| Sentry | `analyze_issue_with_seer` | Ask every time |
| Sentry | `execute_sentry_tool` | Ask every time |
| Amplitude | `run_amp` | Ask every time |
| Amplitude | `use_amp_*` | Ask every time |
| Atlassian | `addCommentToJiraIssue` | Block |
| Atlassian | `editJiraIssue` | Block |
| Atlassian | `transitionJiraIssue` | Block |
| Atlassian | `addWorklogToJiraIssue` | Block |
| Atlassian | `createConfluencePage` | Block |
| Atlassian | `updateConfluencePage` | Block |
| Atlassian | `createConfluenceFooterComment` | Block |
| Atlassian | `createConfluenceInlineComment` | Block |
| Atlassian | `createCompassComponent` | Block |
| Atlassian | `createCompassComponentRelationship` | Block |
| Atlassian | `createCompassCustomFieldDefinition` | Block |
| Atlassian | `addTeamworkGraphContext` | Block |
| Sentry | `update_issue` | Block |
| Amplitude | `create_properties` | Block |
| Amplitude | `update_properties` | Block |
| Amplitude | `delete_event_properties` | Block |
| Amplitude | `delete_user_properties` | Block |
| Amplitude | `restore_event_properties` | Block |
| Amplitude | `restore_user_properties` | Block |
| Amplitude | `create_group_types` | Block |
| Amplitude | `manage_amp_entities` | Block |
| Amplitude | `manage_amp_events` | Block |
| Amplitude | `manage_amp_taxonomy` | Block |
| Amplitude | `share_amp_entities` | Block |
| Claude in Chrome | `form_input` | Ask every time |
| Claude in Chrome | `file_upload` | Ask every time |
| Claude in Chrome | `upload_image` | Ask every time |

Any tool not listed in any table stays on the default (ask). That includes tools a connector adds
after this list was written — new tools are not trusted by default, and that is intended.

## GitLab and Document360

Tool names for these two connectors are not pinned here: they were not connected when this list
was generated, and guessing names produces rules that silently match nothing. The same rule applies
by name pattern:

- **Allow**: tools that only read — names starting `get_`, `list_`, `search`, `semantic_code_search`
- **Block**: anything that creates or changes — `create_*`, `update_*`, `*_note`, merge or pipeline actions

## Keeping it current

The skill's `allowed-tools` frontmatter mirrors the list. When a tool moves tier, change this
file and the frontmatter together — a tool allowed in one place and blocked in another
behaves differently between sessions, which is the hardest kind of drift to notice.
