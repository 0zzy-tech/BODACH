from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Any
import uuid

from pydantic import BaseModel, Field


class FindingSeverity(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"
    info = "info"


class Finding(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    severity: FindingSeverity
    description: str
    evidence: str = ""
    recommendation: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TargetConfig(BaseModel):
    ip: str | None = None
    domain: str | None = None
    ports: str = "1-65535"
    scope: list[str] = []
    notes: str = ""


class Message(BaseModel):
    role: str  # user | assistant | tool | system
    content: str
    tool_calls: list[dict[str, Any]] | None = None
    name: str | None = None          # tool name (for display)
    tool_call_id: str | None = None  # OpenAI-format: required on role=tool messages
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Session(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    messages: list[Message] = []
    findings: list[Finding] = []
    target_config: TargetConfig = Field(default_factory=TargetConfig)


class SessionSummary(BaseModel):
    id: str
    name: str
    created_at: datetime
    last_active: datetime
    message_count: int
    target_ip: str | None
    target_domain: str | None
