"""Prueba rutinas en un esquema efímero propio; cuenta real de la app solo para lectura."""
from pathlib import Path
from datetime import datetime
import json, unittest, uuid
import pymysql
from setup_database import execute_sql
from install_procedures import install
from normalize_database import snapshot, digest

ROOT=Path(__file__).resolve().parents[1]
CONFIG=json.loads((ROOT/'.local/runtime.json').read_text(encoding='utf-8'))

class ProcedureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.name='cal_test_procedures_'+uuid.uuid4().hex
        cls.db=pymysql.connect(host='127.0.0.1',port=CONFIG['db_port'],user='root',password=CONFIG['root_password'],charset='utf8mb4',autocommit=True,client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS)
        with cls.db.cursor() as c:c.execute(f'CREATE DATABASE {cls.name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        cls.db.select_db(cls.name)
        execute_sql(cls.db,ROOT/'database/schema/01_schema.sql');execute_sql(cls.db,ROOT/'database/seeds/02_demo.sql')
        install(cls.db)

    @classmethod
    def tearDownClass(cls):
        cls.db.rollback()
        assert cls.name.startswith('cal_test_procedures_') and len(cls.name)==52
        with cls.db.cursor() as c:c.execute(f'DROP DATABASE {cls.name}')
        cls.db.close()

    def call(self,name,args=()):
        with self.db.cursor(pymysql.cursors.DictCursor) as c:
            c.callproc(name,args);rows=c.fetchall()
            while c.nextset():pass
            return rows

    def test_01_catalog_has_eight_examples_and_api_fields(self):
        rows=self.call('cal_list_functions')
        self.assertEqual(len(rows),8)
        self.assertTrue({'id','title','category','district','image_url','event_date','official_price'}<=rows[0].keys())

    def test_02_conditions_belong_to_function_or_venue(self):
        rows=self.call('cal_function_conditions',(1,))
        self.assertTrue(rows)
        self.assertTrue(all(r['scope'] in ('FUNCION','RECINTO') for r in rows))
        self.assertFalse(self.call('cal_function_conditions',(999999,)))

    def test_03_support_types_contract(self):
        rows=self.call('cal_support_types')
        self.assertEqual(len(rows),7)
        self.assertIn('lsp',[row['code'] for row in rows])

    def test_04_health(self):self.assertEqual(self.call('cal_health')[0]['ok'],1)

    def test_11_bulk_conditions_match_the_existing_per_function_contract(self):
        bulk=self.call('cal_catalog_conditions')
        for function in self.call('cal_list_functions'):
            rows=[{k:v for k,v in row.items() if k!='function_id'} for row in bulk if row['function_id']==function['id']]
            self.assertEqual(rows,list(self.call('cal_function_conditions',(function['id'],))))

    def test_05_report_returns_id_and_pending_state(self):
        self.db.begin()
        try:
            identifier=self.call('cal_create_report',(1,None,'   Reporte valido de prueba   '))[0]['id']
            with self.db.cursor() as c:
                c.execute('SELECT comentario,estado FROM reportes WHERE id=%s',(identifier,))
                self.assertEqual(c.fetchone(),('Reporte valido de prueba','PENDIENTE'))
        finally:self.db.rollback()

    def rejected(self,args):
        before=digest(snapshot(self.db))
        with self.assertRaises(pymysql.MySQLError) as raised:self.call('cal_create_report',args)
        self.assertEqual(raised.exception.args[0],1644)
        self.assertEqual(before,digest(snapshot(self.db)))

    def test_06_unknown_condition_never_writes(self):self.rejected((1,999999,'Reporte con condicion incorrecta'))
    def test_07_invalid_comment_never_writes(self):
        for text in (None,'   ','x'*1001):self.rejected((1,None,text))
    def test_08_unknown_function_never_writes(self):self.rejected((999999,None,'Reporte de funcion inexistente'))

    def test_09_reinstall_preserves_data_and_calls(self):
        before=digest(snapshot(self.db));install(self.db)
        self.assertEqual(before,digest(snapshot(self.db)))
        self.assertEqual(len(self.call('cal_list_functions')),8)

    def test_10_application_account_can_execute(self):
        with pymysql.connect(host='127.0.0.1',port=CONFIG['db_port'],user=CONFIG['db_user'],password=CONFIG['db_password'],database=CONFIG['db_name']) as app:
            with app.cursor() as c:
                c.callproc('cal_health');self.assertEqual(c.fetchone()[0],1)
                while c.nextset():pass
                c.callproc('cal_list_functions');self.assertEqual(len(c.fetchall()),57)
                while c.nextset():pass

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ProcedureTests))
    evidence={'executed_at':datetime.now().astimezone().isoformat(),'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'scope':'MySQL real, esquema efímero propio y lectura mediante cal_app.'}
    (ROOT/'docs/evidencias/procedure-tests.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
    raise SystemExit(not result.wasSuccessful())
