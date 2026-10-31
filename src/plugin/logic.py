"""Read job graphs, pin their exact edges, and write actual candidate reports."""
from pathlib import Path
from contract import PlanInput, Job, GraphOutput, ReferenceOutput, SaveInput, SaveOutput
from plugin.datasets import FIXTURES, RULES
from plugin.storage import store

def graph(plan):
    if plan not in FIXTURES:
        raise ValueError('unknown plan; choose website, parallel, cyclic, empty')
    return [Job(row['job_id'], list(row['requires'])) for row in FIXTURES[plan]]

def read_dataset(given: PlanInput, workspace: Path) -> GraphOutput:
    return GraphOutput(given.plan, graph(given.plan), RULES)

def pin_reference(given: PlanInput, workspace: Path) -> ReferenceOutput:
    return ReferenceOutput(given.plan, graph(given.plan))

def save_candidate(given: SaveInput, workspace: Path) -> SaveOutput:
    graph(given.plan)
    if given.status not in ('ordered','cycle') or len(given.order) > 500:
        raise ValueError('status or number of jobs is invalid')
    path,digest=store(workspace, {'plan': given.plan,'status':given.status,'order':given.order})
    return SaveOutput(given.plan, path, digest, len(given.order))
