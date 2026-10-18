from datetime import date
from fastapi.testclient import TestClient
from main import app
from assistant import reply
import pytest

TODAY=date(2026,10,17)

def event(id,day,price,title='Teatro de prueba',conditions=None):
    return dict(id=id,title=title,date=day,time=None,official_price=price,price_from=True,category='Teatro',district='San Borja',venue='Gran Teatro Nacional',address='Consultar fuente oficial',conditions=conditions or [],official_url='https://example.org/evento',demo=False)

ITEMS=[event(1,'2026-10-17',15),event(2,'2026-10-18',30),event(3,'2026-11-14',0),event(4,'2026-11-15',50),event(5,'2026-11-20',None),event(6,'2026-12-01',10)]

def ask(text,state=None):return reply(text,state or {},ITEMS,TODAY)

def test_simple_hello_is_a_conversation():
    result=ask('hola');assert '¡Hola!' in result['reply'];assert not result['items'];assert 'AccesI' in result['reply']

@pytest.mark.parametrize('message',['buenas tardes','buenos días','hola!!!'])
def test_greeting_variants(message):assert '¡Hola!' in ask(message)['reply']

def test_month_and_followup_price_keep_context():
    first=ask('qué hay en noviembre');second=ask('y los más baratos',first['context'])
    assert [f['id'] for f in second['items']]==[3,4];assert second['total']==2;assert '1 funciones sin precio' in second['reply']

def test_expensive_order_is_not_alphabetical():
    result=ask('los más caros en noviembre');assert [f['id'] for f in result['items']]==[4,3]

def test_day_overrides_previous_month():
    first=ask('noviembre');result=ask('los más caros el 18 de octubre',first['context'])
    assert [f['id'] for f in result['items']]==[2];assert result['context']['month']==10

def test_day_without_month_uses_context():
    first=ask('noviembre');assert [f['id'] for f in ask('y el 14',first['context'])['items']]==[3]

def test_unknown_price_never_means_free():
    assert [f['id'] for f in ask('gratis en noviembre')['items']]==[3]

def test_budget_is_not_a_price_prediction():
    result=ask('hasta 20 soles en octubre');assert [f['id'] for f in result['items']]==[1];assert 'tarifa de partida' in result['reply']

def test_unknown_support_is_not_confirmed():
    result=ask('teatro con LSP en noviembre');assert result['total']==0;assert 'requieren evidencia' in result['reply']

def test_today_and_tomorrow_are_exact():
    assert [f['id'] for f in ask('eventos hoy')['items']]==[1]
    assert [f['id'] for f in ask('eventos mañana')['items']]==[2]

def test_this_month_and_next_month():
    assert [f['id'] for f in ask('eventos este mes')['items']]==[1,2]
    assert all(f['date'].startswith('2026-11') for f in ask('eventos el próximo mes')['items'])

def test_weekday_uses_next_date():assert [f['id'] for f in ask('eventos el domingo')['items']]==[2]

def test_invalid_calendar_date_is_explained():
    result=ask('el 31 de febrero');assert not result['items'];assert 'fecha no existe' in result['reply']

def test_numeric_date():assert [f['id'] for f in ask('el 18/10/2026')['items']]==[2]

def test_reset_removes_month():
    first=ask('noviembre');result=ask('otra búsqueda',first['context']);assert not result['context']

def test_greeting_preserves_existing_search_without_returning_old_events():
    first=ask('noviembre');result=ask('hola',first['context']);assert result['context']==first['context'];assert not result['items']

def test_unspecified_query_requests_clarification():assert 'Dime un mes' in ask('xyz123')['reply']

def test_venue_name_is_not_a_category_filter():
    result=ask('eventos en el Gran Teatro Nacional');assert 'category' not in result['context']

def test_help_is_honest_about_local_ai():assert 'no soy un modelo generativo' in ask('qué puedes hacer')['reply']

def test_price_range_validation():assert 'mínimo supera' in ask('desde 80 hasta 20 soles')['reply']

def test_chat_api_validates_context_and_returns_real_model_name():
    with TestClient(app) as client:
        result=client.post('/chat',json=dict(message='hola',context={},items=ITEMS,today=TODAY.isoformat()))
        assert result.status_code==200;assert result.json()['engine']=='AccesI-local-tfidf-logistic-v1'
        bad=client.post('/chat',json=dict(message='hola',context={'month':13},items=ITEMS,today=TODAY.isoformat()))
        assert bad.status_code==422

@pytest.mark.parametrize('context',[{'sql':'DROP TABLE funciones'},{'month':True},{'date_from':'2026-10-17'},{'date_from':'2026-10-18','date_to':'2026-10-17'}])
def test_untrusted_context_rejected(context):
    with TestClient(app) as client:assert client.post('/chat',json=dict(message='hola',context=context,items=ITEMS,today=TODAY.isoformat())).status_code==422
