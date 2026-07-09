"""Desktop notification wrapper using plyer."""

import logging
from typing import Optional

try:
    from plyer import notification
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

logger = logging.getLogger(__name__)


class Notifier:
    """Handles desktop notifications."""

    def __init__(self, app_name: str = "ChatSpy", enabled: bool = True):
        """Initialize notifier.

        Args:
            app_name: Application name for notifications
            enabled: Whether notifications are enabled
        """
        self.app_name = app_name
        self.enabled = enabled and NOTIFICATIONS_AVAILABLE

        if not NOTIFICATIONS_AVAILABLE:
            logger.warning("Plyer not available, notifications disabled")

    def notify(
        self,
        title: str,
        message: str,
        timeout: int = 5,
    ) -> None:
        """Send a desktop notification.

        Args:
            title: Notification title
            message: Notification message
            timeout: Notification timeout in seconds
        """
        if not self.enabled:
            return

        try:
            notification.notify(
                title=f"{self.app_name} - {title}",
                message=message,
                app_name=self.app_name,
                timeout=timeout,
            )
            logger.debug(f"Notification sent: {title}")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")

    def notify_new_message(self, sender: str, message: str, timeout: int = 5) -> None:
        """Send notification for new message.

        Args:
            sender: Message sender
            message: Message content (will be truncated if too long)
            timeout: Notification timeout in seconds
        """
        # Truncate long messages
        preview = message[:50] + "..." if len(message) > 50 else message
        self.notify(sender, preview, timeout)

    def notify_peer_online(self, username: str, timeout: int = 3) -> None:
        """Send notification when peer comes online.

        Args:
            username: Peer's username
            timeout: Notification timeout in seconds
        """
        self.notify("Peer Online", f"{username} is now online", timeout)

    def notify_peer_offline(self, username: str, timeout: int = 3) -> None:
        """Send notification when peer goes offline.

        Args:
            username: Peer's username
            timeout: Notification timeout in seconds
        """
        self.notify("Peer Offline", f"{username} went offline", timeout)

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable notifications.

        Args:
            enabled: Whether to enable notifications
        """
        if NOTIFICATIONS_AVAILABLE:
            self.enabled = enabled
        else:
            self.enabled = False
            logger.warning("Cannot enable notifications - plyer not available")
