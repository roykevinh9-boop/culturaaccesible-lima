"""Pruebas HTTP contra Java, Python y MySQL reales. Iniciar la demo antes de ejecutarlas."""
from datetime import datetime
from pathlib import Path
import json
import os
import unittest
import urllib.request
import urllib.error

ROOT=Path(__file__).resolve().parents[1]
BASE=os.environ.get('CAL_TEST_URL','http://127.0.0.1:8080')

def request(path,payload=None,source='demo'):
    if path.split('?')[0] in ['/api/functions','/api/metadata']:
        path+=('&' if '?' in path else '?')+'source='+source
    req=urllib.request.Request(BASE+path,data=None if payload is None else json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=12) as response:return response.status,json.load(response)
    except urllib.error.HTTPError as exc:return exc.code,json.load(exc)

class IntegrationTests(unittest.TestCase):
    def test_01_health_real_mysql(self):
        status,data=request('/api/health');self.assertEqual(status,200);self.assertEqual(data['database'],'mysql')
    def test_02_catalog_demo(self):
        status,data=request('/api/functions');self.assertEqual(status,200);self.assertEqual(data['total'],8);self.assertTrue(all(f['demo'] for f in data['items']))
    def test_03_combined_filters(self):
        status,data=request('/api/functions?district=Miraflores&category=Teatro&price=paid');self.assertEqual(status,200);self.assertEqual({f['id'] for f in data['items']},{1,6})
    def test_04_unknown_price_not_free(self):
        _,free=request('/api/functions?price=free');_,unknown=request('/api/functions?price=unknown');self.assertEqual({f['id'] for f in free['items']},{2,5});self.assertEqual({f['id'] for f in unknown['items']},{4,8})
    def test_05_lsp_expired_is_excluded(self):
        _,data=request('/api/functions?needs=lsp');self.assertEqual([f['id'] for f in data['items']],[1])
    def test_06_multiple_supports(self):
        _,data=request('/api/functions?needs=audiodescripcion&needs=tactil');self.assertEqual([f['id'] for f in data['items']],[2])
    def test_07_expired_condition(self):
        _,data=request('/api/functions/6');condition=next(c for c in data['conditions'] if c['code']=='lsp');self.assertEqual(condition['state'],'NO_CONFIRMADO');self.assertIn('vencida',condition['verification_note'])
    def test_08_missing_evidence(self):
        _,data=request('/api/functions/4');condition=next(c for c in data['conditions'] if c['code']=='lsp');self.assertEqual(condition['state'],'NO_CONFIRMADO')
    def test_09_unknown_function(self):self.assertEqual(request('/api/functions/999999')[0],404)
    def test_10_invalid_support(self):self.assertEqual(request('/api/functions?needs=volar')[0],400)
    def test_11_invalid_date(self):self.assertEqual(request('/api/functions?date=ayer')[0],400)
    def test_12_no_results(self):
        status,data=request('/api/functions?q=zzzinexistente');self.assertEqual(status,200);self.assertEqual(data['total'],0)
    def test_13_normalized_search(self):
        _,data=request('/api/functions?q=musica');self.assertEqual({f['id'] for f in data['items']},{3,7})
    def test_14_sql_text_is_only_text(self):
        _,data=request('/api/functions?q=%27%20OR%201%3D1');self.assertEqual(data['total'],0)
    def test_15_python_roundtrip_preserves_conditions(self):
        _,before=request('/api/functions/4');status,pred=request('/api/estimates',{'category':'Danza','district':'Miraflores','month':10});_,after=request('/api/functions/4');self.assertEqual(status,200);self.assertTrue(pred['synthetic']);self.assertGreaterEqual(pred['estimated_price'],0);self.assertEqual(before,after)
    def test_16_invalid_estimate_month(self):self.assertEqual(request('/api/estimates',{'category':'Teatro','district':'Miraflores','month':13})[0],400)
    def test_17_decimal_month_rejected(self):self.assertEqual(request('/api/estimates',{'category':'Teatro','district':'Miraflores','month':6.5})[0],400)
    def test_18_boolean_month_rejected(self):self.assertEqual(request('/api/estimates',{'category':'Teatro','district':'Miraflores','month':True})[0],400)
    def test_19_unsupported_district(self):self.assertEqual(request('/api/estimates',{'category':'Teatro','district':'Barranco','month':6})[0],422)
    def test_20_invalid_report(self):self.assertEqual(request('/api/reports',{'function_id':1,'comment':'   '})[0],400)
    def test_21_report_saved_in_mysql(self):
        import pymysql
        status,data=request('/api/reports',{'function_id':1,'comment':'Prueba de integración: verificar evidencia ficticia.'});self.assertEqual(status,201);self.assertEqual(data['state'],'PENDIENTE')
        config=json.loads((ROOT/'.local/runtime.json').read_text())
        with pymysql.connect(host='127.0.0.1',port=config['db_port'],user=config['db_user'],password=config['db_password'],database=config['db_name'],charset='utf8mb4') as db:
            with db.cursor() as cursor:
                cursor.execute('SELECT funcion_id,estado,comentario FROM reportes WHERE id=%s',(data['id'],));row=cursor.fetchone();self.assertEqual(row[0],1);self.assertEqual(row[1],'PENDIENTE');self.assertIn('integración',row[2])
    def test_22_wrong_condition_is_rejected(self):
        _,function=request('/api/functions/2');cid=next(c['id'] for c in function['conditions'] if c['code']=='tactil');self.assertEqual(request('/api/reports',{'function_id':1,'condition_id':cid,'comment':'Prueba de condición ajena a esta función.'})[0],400)
    def test_23_metadata(self):
        status,data=request('/api/metadata');self.assertEqual(status,200);self.assertEqual(len(data['supports']),7);self.assertEqual(len(data['districts']),4)
    def test_25_official_default_catalog(self):
        status,data=request('/api/functions',source='official');self.assertEqual(status,200);self.assertEqual(data['total'],49);self.assertTrue(all(not f['demo'] and f['image_url'].startswith('https://') and f['official_url'].startswith('https://') for f in data['items']))
    def test_26_nullable_hours_are_preserved(self):
        _,data=request('/api/functions',source='official');self.assertTrue(any(f['time'] is None for f in data['items']));self.assertFalse(any(f['time']=='00:00:00' for f in data['items']))
    def test_27_invalid_source(self):self.assertEqual(request('/api/functions',source='inventado')[0],400)
    def test_28_official_metadata(self):
        _,data=request('/api/metadata',source='official');self.assertFalse(data['demo']);self.assertIn('San Borja',data['districts'])
    def test_29_all_catalogs_are_explicit(self):
        _,data=request('/api/functions',source='all');self.assertEqual(data['total'],57);self.assertEqual(sum(f['demo'] for f in data['items']),8)
    def test_30_catalog_import_is_idempotent(self):
        import pymysql,sys
        sys.path.insert(0,str(ROOT/'scripts'))
        from catalog_import import import_catalog
        config=json.loads((ROOT/'.local/runtime.json').read_text())
        with pymysql.connect(host='127.0.0.1',port=config['db_port'],user='root',password=config['root_password'],database=config['db_name'],autocommit=True) as db:
            with db.cursor() as cursor:cursor.execute('SELECT COUNT(*) FROM funciones');before=cursor.fetchone()[0]
            import_catalog(db,force=True)
            with db.cursor() as cursor:cursor.execute('SELECT COUNT(*) FROM funciones');self.assertEqual(cursor.fetchone()[0],before)
    def test_31_chat_greeting(self):
        status,data=request('/api/chat',{'message':'hola','context':{},'source':'official'});self.assertEqual(status,200);self.assertIn('¡Hola!',data['reply']);self.assertEqual(data['engine'],'AccesI-local-tfidf-logistic-v1');self.assertFalse(data['items'])
    def test_32_chat_remembers_month_and_sorts_price(self):
        _,first=request('/api/chat',{'message':'eventos en noviembre'})
        status,data=request('/api/chat',{'message':'y los más baratos','context':first['context']})
        self.assertEqual(status,200);self.assertTrue(data['items']);self.assertTrue(all(f['date'].startswith('2026-11') for f in data['items']));prices=[f['official_price'] for f in data['items']];self.assertEqual(prices,sorted(prices));self.assertIn('sin precio publicado',data['reply'])
    def test_33_chat_exact_day(self):
        _,data=request('/api/chat',{'message':'los más caros el 18 de octubre'});self.assertTrue(data['items']);self.assertTrue(all(f['date']=='2026-10-18' for f in data['items']))
    def test_34_chat_budget_does_not_use_predictions(self):
        _,data=request('/api/chat',{'message':'hasta 20 soles en octubre'});self.assertTrue(data['items']);self.assertTrue(all(f['official_price'] is not None and f['official_price']<=20 for f in data['items']));self.assertIn('tarifa de partida',data['reply'])
    def test_35_chat_invalid_context(self):self.assertEqual(request('/api/chat',{'message':'hola','context':{'month':13}})[0],400)
    def test_36_chat_keeps_demo_separate(self):
        _,data=request('/api/chat',{'message':'todos los eventos','source':'demo'});self.assertTrue(data['items']);self.assertTrue(all(f['demo'] for f in data['items']));self.assertEqual(data['total'],8)
    def test_37_chat_results_are_mysql_records(self):
        _,data=request('/api/chat',{'message':'eventos en noviembre'});_,catalog=request('/api/functions',source='official');lookup={f['id']:f for f in catalog['items']}
        for item in data['items']:
            self.assertIn(item['id'],lookup);self.assertEqual(item['title'],lookup[item['id']]['title']);self.assertEqual(item['conditions'],lookup[item['id']]['conditions'])
    def test_38_chat_rejects_long_message(self):self.assertEqual(request('/api/chat',{'message':'x'*601})[0],400)
    def test_39_chat_invalid_source(self):self.assertEqual(request('/api/chat',{'message':'hola','source':'all'})[0],400)
    def test_24_negative_price_mysql_constraint(self):
        import pymysql
        config=json.loads((ROOT/'.local/runtime.json').read_text())
        with pymysql.connect(host='127.0.0.1',port=config['db_port'],user=config['db_user'],password=config['db_password'],database=config['db_name'],autocommit=False) as db:
            try:
                with db.cursor() as cursor:
                    with self.assertRaises(pymysql.MySQLError):cursor.execute('INSERT INTO funciones(evento_id,recinto_id,fecha,hora,precio_oficial) VALUES(1,1,CURRENT_DATE,"19:00:00",-1)')
            finally:db.rollback()

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(IntegrationTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    report={'executed_at':datetime.now().astimezone().isoformat(),'base_url':BASE,'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'passed':result.wasSuccessful(),'scope':'HTTP Java + Python + MySQL reales en demostración local','details': [{'test':str(test),'trace':trace} for test,trace in result.failures+result.errors]}
    target=ROOT/'docs/evidencias/integration-tests.json';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    raise SystemExit(0 if result.wasSuccessful() else 1)
