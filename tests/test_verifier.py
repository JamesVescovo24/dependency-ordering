import hashlib
import pytest
from contract import PlanInput,SaveInput,SaveOutput
from plugin.logic import pin_reference,read_dataset,save_candidate
from plugin.storage import REPORT_PATH
from verifier import verify_input,verify_output,verify_task

@pytest.mark.parametrize('plan,order,status',[
    ('website',['docs','database','design','frontend','backend','security','integration','deploy'],'ordered'),
    ('website',['design','database','backend','frontend','integration','security','docs','deploy'],'ordered'),
    ('parallel',['beta','alpha','delta','gamma','epsilon'],'ordered'),
    ('cyclic',[],'cycle'),
    ('empty',[],'ordered'),
])
def test_valid_order(tmp_path,plan,order,status):
    given=PlanInput(plan);reference=pin_reference(given,tmp_path)
    assert verify_output('pin_dependency_graph',given,reference,str(tmp_path))['valid']
    assert verify_output('read_dependencies',given,read_dataset(given,tmp_path),str(tmp_path))['valid']
    payload=SaveInput(plan,status,order)
    output=save_candidate(payload,tmp_path)
    assert verify_output('save_job_order',payload,output,str(tmp_path))['valid']
    assert verify_task('order-jobs',given,output,reference,str(tmp_path))['valid']

@pytest.mark.parametrize('plan,order,status',[
    ('website',['deploy','integration','security','backend','frontend','design','database','docs'],'ordered'),
    ('website',['design','database','backend','frontend','integration','security','docs'],'ordered'),
    ('website',['design','database','backend','frontend','integration','security','docs','deploy','deploy'],'ordered'),
    ('website',['design','database','backend','frontend','integration','security','docs','extra'],'ordered'),
    ('website',[],'cycle'),
    ('cyclic',['prepare','compile','test','ship'],'ordered'),
    ('cyclic',['prepare'],'cycle'),
    ('empty',['invented'],'ordered'),
])
def test_invalid_order(tmp_path,plan,order,status):
    given=PlanInput(plan)
    output=save_candidate(SaveInput(plan,status,order),tmp_path)
    assert not verify_task('order-jobs',given,output,pin_reference(given,tmp_path),str(tmp_path))['valid']

def test_tamper_invalid_batch_and_missing(tmp_path):
    assert not verify_input('read_dependencies',PlanInput('none'))['valid']
    given=PlanInput('empty');output=save_candidate(SaveInput('empty','ordered',[]),tmp_path)
    (tmp_path/REPORT_PATH).write_text('bad')
    assert not verify_task('order-jobs',given,output,pin_reference(given,tmp_path),str(tmp_path))['valid']
    (tmp_path/REPORT_PATH).unlink()
    assert not verify_task('order-jobs',given,output,pin_reference(given,tmp_path),str(tmp_path))['valid']
