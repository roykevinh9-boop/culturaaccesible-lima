import math
import pytest
from fastapi.testclient import TestClient
from main import app
from model import estimate, dataset, trained

client=TestClient(app)

def test_dataset_is_declared_synthetic():
    data=dataset()
    assert len(data)==40
    assert data.isna().sum().sum()==0
    assert len(data.distrito.unique())==2
    assert (data.precio_soles>=0).all()

def test_healthy_and_metrics():
    response=client.get('/health')
    assert response.status_code==200
    result=response.json()
    assert result['synthetic'] is True
    assert result['metrics']['training']==30
    assert result['metrics']['test']==10
    assert 0<=result['metrics']['accuracy']<=1

def test_estimate_has_warning_and_finite_value():
    response=client.post('/estimate',json={'categoria':'Teatro','distrito':'Miraflores','mes':6})
    assert response.status_code==200
    result=response.json()
    assert result['synthetic'] is True
    assert math.isfinite(result['estimated_price']) and result['estimated_price']>=0
    assert 'ficticios' in result['message']
    assert result['predicted_range'] in ['Hasta S/ 40','Mayor de S/ 40']

@pytest.mark.parametrize('field,value',[
    ('categoria',''),('categoria','Cine'),('distrito','Barranco'),('mes',0),('mes',13),
    ('mes',6.5),('mes',True),('mes','6'),('mes',None)
])
def test_reject_invalid_inputs(field,value):
    payload={'categoria':'Teatro','distrito':'Miraflores','mes':6}
    payload[field]=value
    assert client.post('/estimate',json=payload).status_code==422

def test_reject_unknown_field():
    assert client.post('/estimate',json={'categoria':'Teatro','distrito':'Miraflores','mes':6,'diagnostico':'no se solicita'}).status_code==422

def test_deterministic_output():
    assert estimate('Museo','Cercado de Lima',1)==estimate('Museo','Cercado de Lima',1)

def test_unsupported_input_never_predicts():
    with pytest.raises(ValueError):estimate('Cine','Miraflores',6)

def test_month_boolean_is_not_an_integer_input():
    with pytest.raises(ValueError):estimate('Teatro','Miraflores',True)
