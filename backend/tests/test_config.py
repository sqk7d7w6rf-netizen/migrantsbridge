"""Tests for settings and constants."""

import pytest

from app.config import Settings
from app.constants import ChannelType


class TestSettings:
    def test_telegram_fields_exist(self):
        s = Settings(
            _env_file=None,
            TELEGRAM_BOT_TOKEN="bot123",
            TELEGRAM_WEBHOOK_SECRET="sec",
        )
        assert s.TELEGRAM_BOT_TOKEN == "bot123"
        assert s.TELEGRAM_WEBHOOK_SECRET == "sec"

    def test_zapier_fields_exist(self):
        s = Settings(
            _env_file=None,
            ZAPIER_API_KEY="zap-key",
            ZAPIER_WEBHOOK_URL="https://hooks.zapier.com/abc",
        )
        assert s.ZAPIER_API_KEY == "zap-key"
        assert s.ZAPIER_WEBHOOK_URL == "https://hooks.zapier.com/abc"

    def test_defaults_are_empty_strings(self):
        s = Settings(_env_file=None)
        assert s.TELEGRAM_BOT_TOKEN == ""
        assert s.TELEGRAM_WEBHOOK_SECRET == ""
        assert s.ZAPIER_API_KEY == ""
        assert s.ZAPIER_WEBHOOK_URL == ""


class TestChannelType:
    def test_telegram_channel_exists(self):
        assert ChannelType.TELEGRAM == "telegram"

    def test_all_expected_channels_present(self):
        names = {c.value for c in ChannelType}
        assert names >= {"email", "sms", "in_app", "push", "whatsapp", "telegram"}
