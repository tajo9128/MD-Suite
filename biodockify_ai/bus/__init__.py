"""Message bus module for decoupled channel-agent communication."""

from biodockify_ai.bus.events import InboundMessage, OutboundMessage
from biodockify_ai.bus.queue import MessageBus

__all__ = ["MessageBus", "InboundMessage", "OutboundMessage"]
