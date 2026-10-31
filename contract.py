"""Typed task and tool schemas for job dependency ordering."""
from dataclasses import dataclass
from enum import Enum
from typing import Annotated
from slimconfig import Output

class Tool(Enum):
    PIN = "pin_dependency_graph"
    READ = "read_dependencies"
    SAVE = "save_job_order"

class Task(Enum):
    MAIN = "order-jobs"

@dataclass
class PlanInput(Output):
    plan: Annotated[str, "Graph name: website, parallel, cyclic or empty"]

@dataclass
class Job(Output):
    job_id: str
    requires: list[str]

@dataclass
class GraphOutput(Output):
    plan: str
    jobs: list[Job]
    rules: str

@dataclass
class ReferenceOutput(Output):
    plan: str
    jobs: list[Job]

@dataclass
class SaveInput(Output):
    plan: str
    status: Annotated[str, "ordered for acyclic graphs, cycle for cyclic graphs"]
    order: Annotated[list[str], "Each job exactly once in any valid topological order; [] if status is cycle"]

@dataclass
class SaveOutput(Output):
    plan: str
    path: str
    digest: str
    count: int

TOOLS = {Tool.PIN: (PlanInput, ReferenceOutput), Tool.READ: (PlanInput, GraphOutput), Tool.SAVE: (SaveInput, SaveOutput)}
TASKS = {Task.MAIN: (PlanInput, SaveOutput)}
