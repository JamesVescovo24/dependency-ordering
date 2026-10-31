"""Checks DAG / cycle status from pinned jobs; accepts every valid topological ordering."""
from contract import Tool
from .checks import result, read_receipt
PLANS=('website','parallel','cyclic','empty')

def dependencies(jobs):
    result_map={}
    for job in jobs:
        if not job.job_id or job.job_id in result_map or len(set(job.requires)) != len(job.requires):
            return None
        result_map[job.job_id] = set(job.requires)
    if any(dep not in result_map for deps in result_map.values() for dep in deps):
        return None
    return result_map

def cycle_exists(deps):
    pending = {k: set(v) for k,v in deps.items()}
    while pending:
        ready = [k for k,v in pending.items() if not v]
        if not ready:
            return True
        for key in ready:
            del pending[key]
        for v in pending.values():
            v.difference_update(ready)
    return False

def order_ok(order, deps):
    if len(order) != len(deps) or len(set(order)) != len(order) or set(order) != set(deps):
        return False
    before = set()
    for job in order:
        if not deps[job].issubset(before):
            return False
        before.add(job)
    return True

def verify_input(tool,value):
    ok=value.plan in PLANS
    if tool == Tool.SAVE:
        ok=ok and value.status in ('ordered','cycle') and len(value.order) <= 500
    return result(ok,'plan supported' if ok else 'unknown plan or invalid submission')

def verify_output(tool,input_value,output_value,workspace):
    if tool in (Tool.READ,Tool.PIN):
        return result(output_value.plan == input_value.plan and dependencies(output_value.jobs) is not None,'graph available')
    saved,problem=read_receipt(workspace,output_value)
    expected={'plan':input_value.plan,'status':input_value.status,'order':input_value.order}
    ok=not problem and output_value.plan == input_value.plan and output_value.count == len(input_value.order) and saved == expected
    return result(ok,'order saved' if ok else problem or 'saved candidate differs')

def verify_task(arguments,output,reference,workspace):
    if reference is None or reference.plan != arguments.plan or output.plan != arguments.plan:
        return result(False,'missing or mismatched pinned graph')
    deps=dependencies(reference.jobs)
    if deps is None:
        return result(False,'invalid reference graph')
    saved,problem=read_receipt(workspace,output)
    if problem:
        return result(False,problem)
    if saved.get('plan') != arguments.plan or type(saved.get('order')) is not list or type(saved.get('status')) is not str:
        return result(False,'wrong plan or malformed saved order')
    order=saved['order'];status=saved['status']
    if any(not isinstance(item,str) for item in order) or output.count != len(order):
        return result(False,'bad job type or count')
    cyclic=cycle_exists(deps)
    if cyclic:
        ok=status == 'cycle' and order == []
    else:
        ok=status == 'ordered' and order_ok(order,deps)
    return result(ok,'valid cycle finding' if ok and cyclic else 'valid topological order' if ok else 'cycle status, omission, duplicate, unknown job, or dependency violation',jobs=len(deps),cyclic=cyclic)
