"""Celery tasks for Migrants Learning Center AI agents."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)

SLACK_TEACHERS_CHANNEL = "C0B81E9QP63"
SLACK_CEO_CHANNEL = "C0B9B76MFCG"
SLACK_OPS_CHANNEL = "C0B8GU75EPL"
SLACK_AGENTS_CHANNEL = "C0B8LGRR83W"

STATUS_EMOJI = {"green": "🟢", "amber": "🟡", "red": "🔴"}


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _slack_post(channel_id: str, text: str) -> bool:
    """Post a message to Slack via the Zapier webhook or direct Slack SDK."""
    try:
        import httpx
        from app.config import settings

        if not getattr(settings, "SLACK_BOT_TOKEN", None):
            logger.warning("SLACK_BOT_TOKEN not configured — skipping Slack post")
            return False

        resp = httpx.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {settings.SLACK_BOT_TOKEN}"},
            json={"channel": channel_id, "text": text, "mrkdwn": True},
            timeout=10,
        )
        data = resp.json()
        if not data.get("ok"):
            logger.error("Slack post failed: %s", data.get("error"))
            return False
        return True
    except Exception:
        logger.exception("Error posting to Slack channel %s", channel_id)
        return False


@celery_app.task(bind=True, max_retries=2)
def review_lesson_plans(self, lesson_plans: list[dict]) -> dict:
    """Agent 1: Review all submitted lesson plans and post CEO summary.

    lesson_plans: list of dicts with keys: teacher_name, band, plan_text
    """

    async def _run():
        from app.integrations.claude import claude_client
        from app.prompts.learning_center import (
            LESSON_PLAN_REVIEW_SYSTEM,
            LESSON_PLAN_REVIEW_USER,
        )

        today = datetime.now(timezone.utc).strftime("%A, %B %d, %Y")
        plans_formatted = "\n\n".join(
            f"--- {p['teacher_name']} ({p['band']}) ---\n{p['plan_text']}"
            for p in lesson_plans
        )

        result = await claude_client.generate_json(
            system_prompt=LESSON_PLAN_REVIEW_SYSTEM,
            user_message=LESSON_PLAN_REVIEW_USER.format(
                lesson_plans=plans_formatted,
                date=today,
            ),
        )

        status = result.get("overall_readiness", "amber")
        emoji = STATUS_EMOJI.get(status, "🟡")

        lines = [
            f"{emoji} *Lesson Plan Review — {today}*",
            f"Submitted: {result.get('submitted_count', '?')}/6",
        ]

        if result.get("missing_teachers"):
            lines.append(f":warning: Missing: {', '.join(result['missing_teachers'])}")

        if result.get("welfare_flags"):
            lines.append(f"\n*Welfare Flags ({len(result['welfare_flags'])}):*")
            for flag in result["welfare_flags"]:
                lines.append(f"• {flag['band']}: {flag['concern']} (via {flag['teacher']})")

        if result.get("curriculum_gaps"):
            high_gaps = [g for g in result["curriculum_gaps"] if g.get("severity") == "high"]
            if high_gaps:
                lines.append(f"\n*High-Priority Curriculum Gaps:*")
                for gap in high_gaps:
                    lines.append(f"• {gap['band']}: {gap['issue']}")

        if result.get("ceo_action_required"):
            lines.append("\n*Actions Required:*")
            for action in result["ceo_action_required"]:
                lines.append(f"→ {action}")

        if result.get("commendations"):
            lines.append("\n*Commendations:*")
            for c in result["commendations"]:
                lines.append(f"★ {c}")

        message = "\n".join(lines)
        _slack_post(SLACK_CEO_CHANNEL, message)
        logger.info("Lesson plan review posted to #ceo-pulse")
        return result

    try:
        return _run_async(_run())
    except Exception as exc:
        logger.exception("Lesson plan review task failed")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=2)
def compile_weekly_kpis(self, kpi_data: dict, previous_week_summary: str = "") -> dict:
    """Agent 4: Compile weekly KPIs and post executive summary to #ceo-pulse.

    kpi_data: dict with raw counts for all 5 KPIs
    """

    async def _run():
        from app.integrations.claude import claude_client
        from app.prompts.learning_center import (
            WEEKLY_KPI_COMPILER_SYSTEM,
            WEEKLY_KPI_COMPILER_USER,
        )

        import json

        week_ending = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")

        result = await claude_client.generate_json(
            system_prompt=WEEKLY_KPI_COMPILER_SYSTEM,
            user_message=WEEKLY_KPI_COMPILER_USER.format(
                kpi_data=json.dumps(kpi_data, indent=2),
                week_ending=week_ending,
                previous_week=previous_week_summary or "No previous data",
            ),
        )

        overall = result.get("overall_status", "amber")
        emoji = STATUS_EMOJI.get(overall, "🟡")
        kpis = result.get("kpis", {})

        def kpi_line(name: str, display: str, key: str) -> str:
            k = kpis.get(key, {})
            e = STATUS_EMOJI.get(k.get("status", "amber"), "🟡")
            note = f" — {k['note']}" if k.get("note") else ""
            return f"{e} {display}: {k.get('value', '?')} (target {k.get('target', '?')}){note}"

        lines = [
            f"{emoji} *Weekly KPI Report — Week ending {week_ending}*",
            f"_{result.get('one_sentence_summary', '')}_",
            "",
            kpi_line("lesson_plans", "Lesson plans", "lesson_plans"),
            kpi_line("attendance_rate", "Attendance", "attendance_rate"),
            kpi_line("welfare_flags", "Welfare flags open", "welfare_flags"),
            kpi_line("tech_adoption_t5", "Tech adoption T5", "tech_adoption_t5"),
            kpi_line("tech_adoption_t6", "Tech adoption T6", "tech_adoption_t6"),
            kpi_line("ops_compliance", "Ops checklists", "ops_compliance"),
        ]

        if result.get("top_risk"):
            lines += ["", f":rotating_light: *Top Risk:* {result['top_risk']}"]

        if result.get("ceo_30min_agenda"):
            lines += ["", "*Friday 30-min Agenda:*"]
            for item in result["ceo_30min_agenda"]:
                lines.append(f"• {item}")

        trend = result.get("trend_vs_last_week", "stable")
        trend_icon = {"improving": "📈", "stable": "➡️", "declining": "📉"}.get(trend, "➡️")
        lines.append(f"\nTrend vs last week: {trend_icon} {trend.capitalize()}")

        _slack_post(SLACK_CEO_CHANNEL, "\n".join(lines))
        logger.info("Weekly KPI report posted to #ceo-pulse")
        return result

    try:
        return _run_async(_run())
    except Exception as exc:
        logger.exception("Weekly KPI compile task failed")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=1)
def classify_welfare_message(self, message: str, posted_by: str, timestamp: str) -> dict:
    """Agent 3: Classify an ops message for welfare urgency and escalate if needed."""

    async def _run():
        from app.integrations.claude import claude_client
        from app.prompts.learning_center import (
            WELFARE_ESCALATION_SYSTEM,
            WELFARE_ESCALATION_USER,
        )

        result = await claude_client.generate_json(
            system_prompt=WELFARE_ESCALATION_SYSTEM,
            user_message=WELFARE_ESCALATION_USER.format(
                message=message,
                posted_by=posted_by,
                timestamp=timestamp,
            ),
        )

        urgency = result.get("urgency", "LOW")

        if urgency in ("CRITICAL", "HIGH") and result.get("notify_ceo"):
            urgency_emoji = {"CRITICAL": "🚨", "HIGH": "⚠️"}.get(urgency, "⚠️")
            ceo_msg = (
                f"{urgency_emoji} *WELFARE ALERT — {urgency}*\n\n"
                f"{result.get('summary', message)}\n\n"
                f"*Immediate action:* {result.get('immediate_action', 'Review immediately')}\n"
                f"*Category:* {result.get('category', 'unknown')}\n"
                f"*Students affected:* {result.get('student_count_affected', 'unknown')}\n"
                f"*Posted by:* {posted_by} at {timestamp}"
            )
            _slack_post(SLACK_CEO_CHANNEL, ceo_msg)
            logger.info("Welfare escalation posted — urgency: %s", urgency)

        return result

    try:
        return _run_async(_run())
    except Exception as exc:
        logger.exception("Welfare classification task failed")
        raise self.retry(exc=exc, countdown=30)


@celery_app.task(bind=True, max_retries=2)
def track_buddy_program(
    self,
    week_number: int,
    t5_activities: list[str],
    t6_activities: list[str],
    buddy_notes: str = "",
) -> dict:
    """Agent 6: Assess buddy program progress and alert CEO if intervention needed."""

    async def _run():
        from app.integrations.claude import claude_client
        from app.prompts.learning_center import (
            BUDDY_PROGRAM_TRACKER_SYSTEM,
            BUDDY_PROGRAM_TRACKER_USER,
        )

        today = datetime.now(timezone.utc)
        program_start = today - timedelta(weeks=week_number - 1)
        day28 = (program_start + timedelta(days=28)).strftime("%B %d, %Y")

        result = await claude_client.generate_json(
            system_prompt=BUDDY_PROGRAM_TRACKER_SYSTEM,
            user_message=BUDDY_PROGRAM_TRACKER_USER.format(
                week_number=week_number,
                t5_activities="\n".join(t5_activities) if t5_activities else "None reported",
                t6_activities="\n".join(t6_activities) if t6_activities else "None reported",
                buddy_notes=buddy_notes or "No buddy notes submitted",
                date=today.strftime("%A, %B %d, %Y"),
                day28_date=day28,
            ),
        )

        t5_status = result.get("t5_status", "at_risk")
        t6_status = result.get("t6_status", "at_risk")
        status_emoji = {"on_track": "🟢", "at_risk": "🟡", "blocked": "🔴"}

        lines = [
            f"*Buddy Program — Week {week_number}/4*",
            f"T5: {status_emoji.get(t5_status, '🟡')} {t5_status.replace('_', ' ').title()} "
            f"({len(result.get('t5_tasks_completed', []))}/{len(result.get('t5_tasks_completed', [])) + len(result.get('t5_tasks_missing', []))} tasks)",
            f"T6: {status_emoji.get(t6_status, '🟡')} {t6_status.replace('_', ' ').title()} "
            f"({len(result.get('t6_tasks_completed', []))}/{len(result.get('t6_tasks_completed', [])) + len(result.get('t6_tasks_missing', []))} tasks)",
        ]

        if result.get("buddy_interventions_needed"):
            lines.append("\n*Interventions needed:*")
            for inv in result["buddy_interventions_needed"]:
                lines.append(f"• {inv['teacher']} ↔ {inv['buddy']}: {inv['action']}")

        if result.get("week_assessment"):
            lines.append(f"\n_{result['week_assessment']}_")

        if result.get("ceo_checkpoint_needed"):
            lines.append(
                "\n:rotating_light: *CEO checkpoint required before next week starts.*"
            )

        _slack_post(SLACK_CEO_CHANNEL, "\n".join(lines))
        logger.info("Buddy program report posted for week %d", week_number)
        return result

    try:
        return _run_async(_run())
    except Exception as exc:
        logger.exception("Buddy program tracking task failed")
        raise self.retry(exc=exc, countdown=60)
