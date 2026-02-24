"""Chat channels module with plugin architecture."""

from biodockify_ai.channels.base import BaseChannel
from biodockify_ai.channels.manager import ChannelManager

__all__ = ["BaseChannel", "ChannelManager"]
