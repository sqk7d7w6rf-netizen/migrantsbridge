"""Celery tasks for Talart Thai vegetable business AI agents."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone

from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)

# Slack channel IDs
SLACK_VEGBIZ_DAILY = "C0B8HLRV8D9"
SLACK_VEGBIZ_ORDERS = "C0B8Q2DTYD8"
SLACK_VEGBIZ_REPORTS = "C0B88HXTW8P"
SLACK_CEO_CHANNEL = "C0B9B76MFCG"

# Default commission rates (update in settings or pass as args)
COMMISSION_RETAIL = 12
COMMISSION_B2B = 8
COMMISSION_FROZEN = 20


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _slack_post(channel_id: str, text: str) -> bool:
    try:
        import httpx
        from app.config import settings

        if not getattr(settings, "SLACK_BOT_TOKEN", None):
            logger.warning("SLACK_BOT_TOKEN not configured")
            return False

        resp = httpx.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {settings.SLACK_BOT_TOKEN}"},
            json={"channel": channel_id, "text": text, "mrkdwn": True},
            timeout=10,
        )
        return resp.json().get("ok", False)
    except Exception:
        logger.exception("Slack post failed for channel %s", channel_id)
        return False


@celery_app.task(bind=True, max_retries=2)
def morning_buy_advisor(
    self,
    yesterday_sales: dict,
    freezer_stock: dict,
    restaurant_orders: list[dict],
    price_notes: str = "",
) -> dict:
    """Agent 1: 5:30am — What to buy at wholesale market today.

    Posts buying brief to #vegbiz-daily.
    """

    async def _run():
        from app.integrations.claude import claude_client
        from app.prompts.vegetable_biz import (
            MORNING_BUY_ADVISOR_SYSTEM,
            MORNING_BUY_ADVISOR_USER,
        )

        today = datetime.now(timezone.utc).strftime("%A, %B %d, %Y")

        result = await claude_client.generate_json(
            system_prompt=MORNING_BUY_ADVISOR_SYSTEM,
            user_message=MORNING_BUY_ADVISOR_USER.format(
                date=today,
                yesterday_sales=json.dumps(yesterday_sales, indent=2, ensure_ascii=False),
                freezer_stock=json.dumps(freezer_stock, indent=2, ensure_ascii=False),
                restaurant_orders=json.dumps(restaurant_orders, indent=2, ensure_ascii=False),
                price_notes=price_notes or "No price notes today",
            ),
        )

        buy_list = result.get("buy_today", [])
        margin = result.get("expected_margin_pct", 0)
        spend = result.get("estimated_day_spend_thb", 0)
        revenue = result.get("expected_revenue_thb", 0)

        high_priority = [b for b in buy_list if b.get("priority") == "high"]
        frozen_packs = result.get("frozen_packs_to_prepare", [])
        bulk = result.get("bulk_opportunity")

        lines = [
            f"*Morning Buy Brief — {today}* 🌅",
            f"_{result.get('one_line_brief', '')}_",
            "",
            f"*Buy today (฿{spend:,} est → ฿{revenue:,} revenue, {margin:.0f}% margin):*",
        ]
        for item in high_priority:
            lines.append(f"🔴 {item['item']} — {item['quantity_kg']}kg ({item['reason']})")
        for item in [b for b in buy_list if b.get("priority") != "high"]:
            lines.append(f"🟡 {item['item']} — {item['quantity_kg']}kg ({item['reason']})")

        if frozen_packs:
            lines.append("\n*Prep frozen packs today:*")
            for pack in frozen_packs:
                lines.append(
                    f"• {pack['pack_name']} × {pack['portions']} "
                    f"({', '.join(pack.get('items_needed', []))})"
                )

        if bulk:
            lines.append(f"\n🚨 *BULK BUY ALERT:* {bulk}")

        if not result.get("restaurant_orders_covered"):
            lines.append("\n⚠️ *WARNING: Not all restaurant orders can be covered today*")

        _slack_post(SLACK_VEGBIZ_DAILY, "\n".join(lines))
        logger.info("Morning buy brief posted")
        return result

    try:
        return _run_async(_run())
    except Exception as exc:
        logger.exception("Morning buy advisor task failed")
        raise self.retry(exc=exc, countdown=120)


@celery_app.task(bind=True, max_retries=2)
def afternoon_waste_reducer(
    self,
    remaining_stock: dict,
    sales_pace: dict,
    freezer_space_pct: int = 60,
) -> dict:
    """Agent 2: 3pm — Markdown vs freeze decision for remaining stock.

    Eliminates end-of-day waste. Posts action plan to #vegbiz-daily.
    """

    async def _run():
        from app.integrations.claude import claude_client
        from app.prompts.vegetable_biz import (
            WASTE_REDUCER_SYSTEM,
            WASTE_REDUCER_USER,
        )

        today = datetime.now(timezone.utc).strftime("%A, %B %d")

        result = await claude_client.generate_json(
            system_prompt=WASTE_REDUCER_SYSTEM,
            user_message=WASTE_REDUCER_USER.format(
                date=today,
                remaining_stock=json.dumps(remaining_stock, indent=2, ensure_ascii=False),
                sales_pace=json.dumps(sales_pace, indent=2, ensure_ascii=False),
                freezer_space_pct=freezer_space_pct,
            ),
        )

        saved = result.get("estimated_waste_value_saved_thb", 0)
        markdowns = result.get("markdown_now", [])
        to_freeze = result.get("freeze", [])
        packs = result.get("process_into_packs", [])
        discard = result.get("discard", [])

        lines = [
            f"*3pm Stock Action — {today}* ⏰",
            f"*{result.get('action_summary', 'Check stock and act now.')}*",
            f"Est. waste value saved: ฿{saved:,}",
        ]

        if markdowns:
            lines.append("\n*MARKDOWN NOW (sell before closing):*")
            for m in markdowns:
                lines.append(
                    f"🏷️ {m['item']} {m['qty_remaining_kg']}kg → "
                    f"-{m['suggested_discount_pct']}% ({m['reason']})"
                )

        if to_freeze:
            lines.append("\n*FREEZE (prep before 5pm):*")
            for f in to_freeze:
                lines.append(f"❄️ {f['item']} {f['qty_kg']}kg — {f.get('notes', 'freeze as-is')}")

        if packs:
            lines.append("\n*PROCESS INTO PACKS:*")
            for p in packs:
                lines.append(f"📦 {p['pack_name']} × {p['qty_packs']} portions")

        if discard:
            lines.append("\n*Discard (genuine waste):*")
            for d in discard:
                lines.append(f"🗑️ {d['item']} {d['qty_kg']}kg — {d['reason']}")

        _slack_post(SLACK_VEGBIZ_DAILY, "\n".join(lines))
        logger.info("3pm waste reduction posted")
        return result

    try:
        return _run_async(_run())
    except Exception as exc:
        logger.exception("Waste reducer task failed")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=2)
def weekly_commission_report(
    self,
    sales_data: list[dict],
    previous_week_total: float = 0,
    commission_retail: int = COMMISSION_RETAIL,
    commission_b2b: int = COMMISSION_B2B,
    commission_frozen: int = COMMISSION_FROZEN,
) -> dict:
    """Agent 3: Sunday 8pm — Calculate and post weekly commission to CEO.

    Posts to #vegbiz-reports and CEO channel.
    """

    async def _run():
        from app.integrations.claude import claude_client
        from app.prompts.vegetable_biz import (
            COMMISSION_CALCULATOR_SYSTEM,
            COMMISSION_CALCULATOR_USER,
        )

        system = COMMISSION_CALCULATOR_SYSTEM.format(
            commission_rate_retail=commission_retail,
            commission_rate_b2b=commission_b2b,
            commission_rate_frozen=commission_frozen,
        )

        result = await claude_client.generate_json(
            system_prompt=system,
            user_message=COMMISSION_CALCULATOR_USER.format(
                sales_data=json.dumps(sales_data, indent=2, ensure_ascii=False),
                commission_rate_retail=commission_retail,
                commission_rate_b2b=commission_b2b,
                commission_rate_frozen=commission_frozen,
                previous_week_total=f"{previous_week_total:,.0f}",
            ),
        )

        total_commission = result.get("total_commission_thb", 0)
        total_gross = result.get("total_gross_sales_thb", 0)
        waste_pct = result.get("waste_pct", 0)
        vs_last = result.get("vs_last_week_pct", 0)
        trend_icon = "📈" if vs_last > 0 else ("📉" if vs_last < 0 else "➡️")

        sales_by_cat = result.get("sales_by_category", {})
        retail = sales_by_cat.get("fresh_retail", {})
        b2b = sales_by_cat.get("restaurant_b2b", {})
        frozen = sales_by_cat.get("frozen_packs", {})

        message = (
            f"*Weekly Commission Report — {result.get('week_ending', 'this week')}* 💰\n\n"
            f"*Total gross sales: ฿{total_gross:,}*\n"
            f"Fresh retail: ฿{retail.get('gross_thb', 0):,} → commission ฿{retail.get('commission_thb', 0):,}\n"
            f"Restaurant B2B: ฿{b2b.get('gross_thb', 0):,} → commission ฿{b2b.get('commission_thb', 0):,}\n"
            f"Frozen packs: ฿{frozen.get('gross_thb', 0):,} → commission ฿{frozen.get('commission_thb', 0):,}\n\n"
            f"*YOUR COMMISSION: ฿{total_commission:,}*\n"
            f"Due by: {result.get('payment_due_date', 'next Monday')}\n\n"
            f"Waste rate: {waste_pct:.1f}% | vs last week: {trend_icon} {abs(vs_last):.1f}%\n"
            f"Best seller: {result.get('best_selling_item', '?')} | "
            f"Worst: {result.get('worst_selling_item', '?')}\n\n"
            f"*Next week:* {result.get('next_week_recommendation', '')}"
        )

        if result.get("anomalies"):
            message += "\n\n*Flags:*\n" + "\n".join(f"• {a}" for a in result["anomalies"])

        _slack_post(SLACK_VEGBIZ_REPORTS, message)
        _slack_post(SLACK_CEO_CHANNEL, message)
        logger.info("Weekly commission report posted: ฿%s", total_commission)
        return result

    try:
        return _run_async(_run())
    except Exception as exc:
        logger.exception("Commission report task failed")
        raise self.retry(exc=exc, countdown=120)


@celery_app.task(bind=True, max_retries=1)
def price_scout_alert(
    self,
    todays_prices: dict,
    price_history: dict,
    retail_prices: dict,
    freezer_capacity_pct: int = 60,
) -> dict:
    """Agent 4: Triggered when new price data is logged.

    Detects bulk-buy opportunities and margin alerts.
    """

    async def _run():
        from app.integrations.claude import claude_client
        from app.prompts.vegetable_biz import (
            PRICE_SCOUT_SYSTEM,
            PRICE_SCOUT_USER,
        )

        result = await claude_client.generate_json(
            system_prompt=PRICE_SCOUT_SYSTEM,
            user_message=PRICE_SCOUT_USER.format(
                todays_prices=json.dumps(todays_prices, indent=2, ensure_ascii=False),
                price_history=json.dumps(price_history, indent=2, ensure_ascii=False),
                retail_prices=json.dumps(retail_prices, indent=2, ensure_ascii=False),
                freezer_capacity_pct=freezer_capacity_pct,
            ),
        )

        bulk_signals = result.get("bulk_buy_signals", [])
        margin_alerts = result.get("margin_alerts", [])
        avoids = result.get("avoid_today", [])

        lines = [f"*Price Scout Alert* 🔍", f"_{result.get('top_opportunity_today', '')}_"]

        if bulk_signals:
            lines.append("\n*🚨 BULK BUY NOW:*")
            for s in bulk_signals:
                lines.append(
                    f"• {s['item']}: ฿{s['current_price_thb_kg']}/kg "
                    f"(avg ฿{s['avg_30d_price']}/kg, -{s['drop_pct']:.0f}%) "
                    f"→ buy {s['recommended_buy_kg']}kg, "
                    f"est profit ฿{s['estimated_profit_if_held_thb']:,}"
                )

        if avoids:
            lines.append("\n*❌ Skip today (prices spiked):*")
            for a in avoids:
                lines.append(f"• {a['item']}: ฿{a['current_price_thb_kg']}/kg (+{a['spike_pct']:.0f}%)")

        if margin_alerts:
            lines.append("\n*⚠️ Margin alerts:*")
            for m in margin_alerts:
                lines.append(
                    f"• {m['item']}: retail ฿{m['your_retail_price']}/kg, "
                    f"cost ฿{m['current_wholesale']}/kg, "
                    f"margin {m['current_margin_pct']:.0f}% → {m['suggested_action']}"
                )

        if result.get("seasonal_note"):
            lines.append(f"\n_Seasonal: {result['seasonal_note']}_")

        if bulk_signals:
            _slack_post(SLACK_VEGBIZ_DAILY, "\n".join(lines))

        return result

    try:
        return _run_async(_run())
    except Exception as exc:
        logger.exception("Price scout task failed")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=2)
def generate_restaurant_pitch(
    self,
    restaurant_name: str,
    restaurant_type: str,
    size: str,
    location: str,
    current_supplier: str = "Unknown",
    likely_needs: str = "Thai vegetables",
) -> dict:
    """Agent 5: Generate a B2B pitch email for a restaurant standing order.

    Returns the pitch and posts to #vegbiz-orders.
    """

    async def _run():
        from app.integrations.claude import claude_client
        from app.prompts.vegetable_biz import (
            RESTAURANT_PITCH_SYSTEM,
            RESTAURANT_PITCH_USER,
        )

        result = await claude_client.generate_json(
            system_prompt=RESTAURANT_PITCH_SYSTEM,
            user_message=RESTAURANT_PITCH_USER.format(
                restaurant_name=restaurant_name,
                restaurant_type=restaurant_type,
                size=size,
                location=location,
                current_supplier=current_supplier,
                likely_needs=likely_needs,
            ),
        )

        message = (
            f"*Restaurant Pitch Ready — {restaurant_name}* 📨\n\n"
            f"*Subject:* {result.get('email_subject', '')}\n\n"
            f"{result.get('email_body', '')}\n\n"
            f"*Starter order value:* "
            f"฿{result.get('suggested_starter_order', {}).get('estimated_weekly_value_thb', 0):,}/week\n"
            f"*Follow up:* {result.get('follow_up_timeline', '3 days if no reply')}"
        )

        _slack_post(SLACK_VEGBIZ_ORDERS, message)
        logger.info("Restaurant pitch generated for %s", restaurant_name)
        return result

    try:
        return _run_async(_run())
    except Exception as exc:
        logger.exception("Restaurant pitch task failed")
        raise self.retry(exc=exc, countdown=60)
