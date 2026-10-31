"""Original graph fixtures include disconnected jobs, a cycle and the empty graph."""
FIXTURES = {
    'website': [
        {'job_id':'design','requires':[]},
        {'job_id':'database','requires':[]},
        {'job_id':'backend','requires':['database']},
        {'job_id':'frontend','requires':['design']},
        {'job_id':'integration','requires':['backend','frontend']},
        {'job_id':'security','requires':['backend']},
        {'job_id':'deploy','requires':['integration','security']},
        {'job_id':'docs','requires':[]},
    ],
    'parallel': [
        {'job_id':'alpha','requires':[]},
        {'job_id':'beta','requires':[]},
        {'job_id':'gamma','requires':['alpha']},
        {'job_id':'delta','requires':['alpha']},
        {'job_id':'epsilon','requires':['beta','gamma']},
    ],
    'cyclic': [
        {'job_id':'prepare','requires':[]},
        {'job_id':'compile','requires':['test']},
        {'job_id':'test','requires':['compile']},
        {'job_id':'ship','requires':['prepare','test']},
    ],
    'empty':[],
}
RULES = (
    'Output {status: ordered, order:[...]} if a topological sort exists. Include all job IDs once, '
    'put every prerequisite before its dependent, and accept any such ordering. '
    'If the graph contains a directed dependency cycle, output status:cycle and order:[]. '
    'A graph with no jobs is ordered with an empty order. No invented jobs.'
)
