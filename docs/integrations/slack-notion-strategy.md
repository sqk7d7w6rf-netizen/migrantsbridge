# Slack & Notion Integration Strategy

This document describes the best strategy and a phased action plan for using
Slack and Notion effectively at MigrantsBridge, and how both are wired into the
platform today.

## Roles

The two tools play complementary, non-overlapping roles. Keeping the boundary
clear is what makes them effective together.

- **Slack = real-time operational layer.** Fast, ephemeral, human-facing.
  Use it for automated alerts and reminders, human-handoff (when an automated
  workflow needs a person), the daily KPI pulse, and day-to-day team chat.
  Messages are signals to act now; they are not the system of record.

- **Notion = durable single-source-of-truth.** Slow-moving, structured,
  long-lived. Use it for Standard Operating Procedures (SOPs), the AI agent
  prompt library, the case knowledge base, and project/KPI tracking. Anything
  that must be findable in three months lives in Notion, not in a Slack thread.

Rule of thumb: if it needs a decision *now*, it goes to Slack; if it needs to be
*remembered*, it goes to Notion.

## Integration model

The MigrantsBridge platform is the hub. It emits domain events (case created,
appointment reminder due, daily KPIs computed, etc.) and fans them out to Slack
and Notion through dedicated, no-op-if-unconfigured adapters.

- **Platform → Slack.** Outbound messages go through `ChannelType.SLACK`
  notifications dispatched to the `send_slack` Celery task, or directly through
  the `slack_adapter` singleton (`app/integrations/slack.py`). The adapter posts
  to `chat.postMessage` with a bot token, falls back to an incoming webhook, and
  no-ops with a warning when neither is configured.

- **Platform → Notion.** Durable records (cases, KPI snapshots, knowledge
  entries) are written through the `notion_adapter` singleton
  (`app/integrations/notion.py`), e.g. `create_page` into the database referenced
  by `NOTION_CASES_DATABASE_ID`. The adapter no-ops when `NOTION_API_KEY` is
  unset.

- **Daily KPI pulse.** `compute_daily_kpis` caches KPI snapshots in Redis once a
  day. Shortly after, the `post_daily_pulse_to_slack` Celery beat task reads the
  same cached snapshot and posts a short digest to Slack. Both are registered in
  the Celery beat schedule (`app/core/celery_app.py`).

## Channel & workspace structure

### Slack channels

- `#general` — organization-wide announcements and non-urgent updates.
- `#ops-alerts` — automated reminders, appointment notifications, and
  human-handoff prompts emitted by the platform. This is the default target for
  `SLACK_DEFAULT_CHANNEL`.
- `#leadership` — the daily KPI pulse and weekly CEO review material.
- `#tech` (optional) — system/error notifications for the engineering team.

### Notion teamspace

- **SOPs** — operational runbooks and process documentation.
- **Agent Prompt Library** — versioned prompt templates used by the AI
  workflow engine, with change history and ownership.
- **Case Knowledge Base** — durable, structured case records and learnings;
  the platform logs cases/KPIs here via `NOTION_CASES_DATABASE_ID`.
- **KPI Dashboard** — daily/weekly/monthly KPI tracking, fed from the same
  metrics that drive the Slack pulse.

## Phased action plan

1. **Foundations.** Create the Slack workspace and channels above, and the
   Notion teamspace and databases. Provision credentials (see Setup) and set the
   five env vars. With no credentials, all adapters safely no-op, so this is a
   zero-risk first step.

2. **Wire platform → Slack.** Enable `ChannelType.SLACK` notifications for
   operational events (reminders, human-handoff). Confirm `send_slack` delivers
   to `#ops-alerts` and that the `post_daily_pulse_to_slack` beat task posts the
   daily digest to `#leadership`.

3. **Wire platform → Notion.** Use `notion_adapter.create_page` to log cases and
   KPI snapshots into the cases database. Build the KPI Dashboard and Case
   Knowledge Base views on top of that data.

4. **Governance, access & retention.** Define channel/database ownership, access
   controls, and retention rules. Keep Slack for transient signals and Notion as
   the durable record; periodically archive stale Slack threads into Notion where
   they have lasting value.

## Setup

Set the following environment variables (also listed in `.env.example`):

| Variable | Purpose | How to obtain |
| --- | --- | --- |
| `SLACK_BOT_TOKEN` | Bot OAuth token (`xoxb-...`) for `chat.postMessage` | Create a Slack app, add the `chat:write` bot scope, install it to the workspace, and copy the Bot User OAuth Token. |
| `SLACK_DEFAULT_CHANNEL` | Default outbound channel | Use a channel name (e.g. `#ops-alerts`) or channel id; invite the bot to that channel. |
| `SLACK_WEBHOOK_URL` | Incoming-webhook fallback | Enable Incoming Webhooks on the Slack app and create a webhook for the target channel. Used only when no bot token is set. |
| `NOTION_API_KEY` | Notion internal integration token (`secret_...`) | Create a Notion internal integration and copy its token. |
| `NOTION_CASES_DATABASE_ID` | Database id for cases/KPIs | Open the target Notion database, copy its id from the URL, and **share the database with the integration**. |

All five default to empty strings, so the platform runs normally without them;
each adapter logs a warning and no-ops until its credentials are provided.
