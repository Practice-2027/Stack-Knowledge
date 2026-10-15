"""
agent_framework.py
==================
Core Multi-Agent Framework for the Task Automation System.

This module provides the foundational building blocks for building autonomous,
collaborative agents:
  1. Message: Standardized communication packet between agents.
  2. Tool: Encapsulated capability or function executable by agents.
  3. BaseAgent: Abstract base agent with state, memory, and lifecycle methods.
  4. MessageBus: Central communication hub routing messages between agents.

No external paid APIs or complex cloud services are required.
"""

from __future__ import annotations
import uuid
import datetime
import threading
from typing import Callable, Any, Dict, List, Optional


class MessageType:
    """Enumeration of standard message categories exchanged across the bus."""
    TASK = "TASK"       # Delegation or request to perform work
    RESULT = "RESULT"   # Completion notification and payload output
    ERROR = "ERROR"     # Failure notification or execution exception
    INFO = "INFO"       # Status update, diagnostic, or synchronization log


class Message:
    """
    Standard communication packet passed between agents via the MessageBus.

    Attributes:
        sender (str): Name of the agent sending the message.
        receiver (str): Name of the target agent (or '*' for broadcast).
        content (Any): The message payload (string, dict, or structured data).
        message_type (str): TASK, RESULT, ERROR, or INFO.
        timestamp (str): ISO formatted creation timestamp.
        message_id (str): Unique identifier for tracking and tracing conversations.
        metadata (dict): Optional extra contextual data (e.g. task_id, step_number).
    """

    def __init__(
        self,
        sender: str,
        receiver: str,
        content: Any,
        message_type: str = MessageType.INFO,
        message_id: Optional[str] = None,
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.message_type = message_type.upper() if isinstance(message_type, str) else MessageType.INFO
        self.message_id = message_id or str(uuid.uuid4())[:8]
        self.timestamp = timestamp or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to a dictionary suitable for JSON serialization."""
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
            "message_type": self.message_type,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Message:
        """Create a Message instance from a dictionary."""
        return cls(
            sender=data.get("sender", "Unknown"),
            receiver=data.get("receiver", "*"),
            content=data.get("content", ""),
            message_type=data.get("message_type", MessageType.INFO),
            message_id=data.get("message_id"),
            timestamp=data.get("timestamp"),
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        preview = str(self.content)
        if len(preview) > 50:
            preview = preview[:47] + "..."
        return f"<Message [{self.message_type}] {self.sender} -> {self.receiver}: '{preview}'>"


class Tool:
    """
    Encapsulated capability that an agent can invoke to interact with the world,
    perform calculations, read files, or query knowledge bases.

    Attributes:
        name (str): Identifier for the tool (e.g., 'calculate_compound_interest').
        description (str): Human-readable explanation of what the tool does.
        func (Callable): The Python function executed when the tool runs.
        parameters_doc (str): Description of expected arguments.
    """

    def __init__(
        self,
        name: str,
        description: str,
        func: Callable[..., Any],
        parameters_doc: str = "",
    ):
        self.name = name
        self.description = description
        self.func = func
        self.parameters_doc = parameters_doc

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Safely execute the tool's underlying function with provided arguments.

        Returns:
            dict: Standardized result dict with:
                - 'tool': tool name
                - 'success': bool
                - 'result': output data if successful
                - 'error': error message if failed
        """
        try:
            print(f"  [Tool Execution] Running '{self.name}' with args: {kwargs}")
            output = self.func(**kwargs)
            return {
                "tool": self.name,
                "success": True,
                "result": output,
                "error": None,
            }
        except Exception as exc:
            err_msg = f"Tool '{self.name}' failed: {str(exc)}"
            print(f"  [Tool Error] {err_msg}")
            return {
                "tool": self.name,
                "success": False,
                "result": None,
                "error": err_msg,
            }

    def to_dict(self) -> Dict[str, Any]:
        """Convert tool metadata to dictionary format."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters_doc,
        }

    def __repr__(self) -> str:
        return f"<Tool '{self.name}': {self.description}>"


class BaseAgent:
    """
    Abstract Base Class for all autonomous agents in the system.

    Attributes:
        name (str): Unique name of the agent (e.g. 'ResearcherAgent').
        role (str): The primary duty or domain expertise of the agent.
        capabilities (List[str]): High-level skills this agent possesses.
        tools (Dict[str, Tool]): Registered tools accessible to this agent.
        status (str): Current execution state ('IDLE', 'BUSY', 'ERROR').
        message_bus (Optional[MessageBus]): Central bus for sending/receiving messages.
        inbox (List[Message]): Received messages addressed to this agent.
    """

    def __init__(self, name: str, role: str, capabilities: Optional[List[str]] = None):
        self.name = name
        self.role = role
        self.capabilities = capabilities or []
        self.tools: Dict[str, Tool] = {}
        self.status = "IDLE"
        self.message_bus: Optional[MessageBus] = None
        self.inbox: List[Message] = []
        self.last_active: str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def register_tool(self, tool: Tool) -> None:
        """Register a tool this agent can invoke during task processing."""
        self.tools[tool.name] = tool

    def set_message_bus(self, message_bus: MessageBus) -> None:
        """Connect this agent to a shared MessageBus instance."""
        self.message_bus = message_bus

    def send_message(
        self,
        receiver: str,
        content: Any,
        message_type: str = MessageType.INFO,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:
        """
        Send a message to another agent or broadcast across the MessageBus.
        """
        msg = Message(
            sender=self.name,
            receiver=receiver,
            content=content,
            message_type=message_type,
            metadata=metadata or {},
        )
        if self.message_bus:
            self.message_bus.send_message(msg)
        else:
            print(f"Warning: Agent '{self.name}' has no MessageBus connected. Dropping message to '{receiver}'.")
        return msg

    def receive_message(self, message: Message) -> None:
        """
        Invoked by the MessageBus when a message addressed to this agent arrives.
        Default behavior stores the message in the inbox and updates status timestamp.
        """
        self.inbox.append(message)
        self.last_active = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"  [{self.name}] Received [{message.message_type}] from [{message.sender}]")

    def process_task(self, task: Any) -> Dict[str, Any]:
        """
        Process a delegated task. Must be overridden by specialist agents.

        Args:
            task: Task description string or structured task dict.

        Returns:
            dict: Task outcome with status, results, and diagnostics.
        """
        raise NotImplementedError("Specialized agents must implement process_task()")

    def get_status(self) -> Dict[str, Any]:
        """
        Return the current state and capabilities of this agent.

        Returns:
            dict: Agent status summary.
        """
        return {
            "name": self.name,
            "role": self.role,
            "capabilities": self.capabilities,
            "status": self.status,
            "tools": [t.to_dict() for t in self.tools.values()],
            "inbox_count": len(self.inbox),
            "last_active": self.last_active,
        }

    def __repr__(self) -> str:
        return f"<Agent '{self.name}' ({self.role}) [{self.status}]>"


class MessageBus:
    """
    Central Message Bus facilitating decoupled communication between agents.

    Supports:
      - Point-to-point agent messaging (e.g. Orchestrator -> Calculator)
      - Broadcasting (receiver='*' or receiver='ALL')
      - Message history logging with filtering
      - Thread-safe operations for web server concurrency
    """

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.message_history: List[Message] = []
        self._lock = threading.RLock()

    def register_agent(self, agent: BaseAgent) -> None:
        """
        Register an agent on the message bus and assign this bus to the agent.
        """
        with self._lock:
            self.agents[agent.name] = agent
            agent.set_message_bus(self)
            print(f"[MessageBus] Registered agent '{agent.name}' ({agent.role})")

    def send_message(self, message: Message) -> Message:
        """
        Route a message to its intended recipient(s) and append to history log.

        Args:
            message: Message instance to send.

        Returns:
            Message: The sent message.
        """
        with self._lock:
            # 1. Log to central history
            self.message_history.append(message)

            # 2. Print readable trace to terminal
            arrow = "-->"
            print(f"[Bus LOG] {message.timestamp} | [{message.message_type:<6}] {message.sender} {arrow} {message.receiver}")

            # 3. Deliver to recipient
            if message.receiver in ("*", "ALL"):
                # Broadcast to every agent except the sender
                for name, agent in self.agents.items():
                    if name != message.sender:
                        agent.receive_message(message)
            elif message.receiver in self.agents:
                self.agents[message.receiver].receive_message(message)
            else:
                print(f"[MessageBus Warning] Target agent '{message.receiver}' is not registered on bus.")

            return message

    def get_messages(
        self,
        agent_name: Optional[str] = None,
        message_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve filtered messages from history in chronological order.

        Args:
            agent_name: Optional filter for sender OR receiver matching this name.
            message_type: Optional filter for message type (e.g. 'TASK', 'RESULT').
            limit: Maximum count of recent messages to return.

        Returns:
            List[dict]: Serialized message dictionaries.
        """
        with self._lock:
            filtered = self.message_history

            if agent_name:
                filtered = [
                    m for m in filtered
                    if m.sender == agent_name or m.receiver in (agent_name, "*", "ALL")
                ]

            if message_type:
                target_type = message_type.upper()
                filtered = [m for m in filtered if m.message_type == target_type]

            # Return the most recent 'limit' messages
            results = filtered[-limit:]
            return [m.to_dict() for m in results]

    def get_all_messages(self) -> List[Dict[str, Any]]:
        """Return the entire chronological message history as dictionaries."""
        with self._lock:
            return [m.to_dict() for m in self.message_history]

    def clear_history(self) -> None:
        """Clear all stored messages in the message history log."""
        with self._lock:
            self.message_history.clear()
            for agent in self.agents.values():
                agent.inbox.clear()
            print("[MessageBus] Cleared all message history and agent inboxes.")

    def get_agent_names(self) -> List[str]:
        """Return a list of registered agent names."""
        with self._lock:
            return list(self.agents.keys())
