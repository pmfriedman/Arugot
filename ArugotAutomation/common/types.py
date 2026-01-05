from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass
class Trigger:
    type: Literal["manual", "interval", "once", "scheduled"]
    params: dict


@dataclass
class RunContext:
    workflow: str
    trigger: Trigger
    run_id: str
    started_at: datetime
    args: dict
    dry_run: bool = False
