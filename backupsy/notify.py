"""Send a simple webhook notification (Slack/Discord/generic) on backup success or failure."""

from __future__ import annotations

import logging

import requests

from .config import NotifyConfig

logger = logging.getLogger("backupsy.notify")


def send_notification(notify: NotifyConfig, success: bool, message: str) -> None:
    if success and not notify.on_success:
        return
    if not success and not notify.on_failure:
        return

    url = notify.webhook_url()
    if not url:
        return

    status = "✅ SUCCESS" if success else "❌ FAILURE"
    payload_text = f"[backupsy] {status}: {message}"

    # Works out of the box for Slack ("text") and Discord ("content") webhooks.
    payload = {"text": payload_text, "content": payload_text}

    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.warning("Failed to send notification: %s", e)
