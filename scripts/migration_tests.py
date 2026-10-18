"""Verifica migración y alta nueva en bases efímeras propias, nunca sobre datos ajenos."""
from pathlib import Path
from datetime import datetime
import json
import unittest
import uuid
import pymysql
from normalize_database import snapshot, digest
from setup_database import execute_sql

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / '.local/runtime.json').read_text(encoding='utf-8'))


class MigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = pymysql.connect(host='127.0.0.1', port=CONFIG['db_port'], user='root',
                                password=CONFIG['root_password'], charset='utf8mb4', autocommit=True,
                                client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS)
        cls.names = ['cal_test_migracion_' + uuid.uuid4().hex for _ in range(3)]
        with cls.db.cursor() as cursor:
            for name in cls.names:
                cursor.execute(f'CREATE DATABASE {name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
            cursor.execute(f'USE {cls.names[0]}')
        execute_sql(cls.db, ROOT / 'scripts/fixtures/legacy_schema.sql')
        execute_sql(cls.db, ROOT / 'scripts/fixtures/legacy_demo.sql')
        with cls.db.cursor() as cursor:
            cursor.execute("INSERT INTO eventos(id,nombre,descripcion,categoria,es_demo) VALUES(90,'Prueba','Categoría adicional','Categoría nueva con ñ',1)")
            cursor.execute("INSERT INTO reportes(funcion_id,comentario) VALUES(1,'Reporte existente antes de migrar')")
        cls.before = snapshot(cls.db)
        cls.migrate()
        cls.after = snapshot(cls.db)

    @classmethod
    def migrate(cls):
        sql = (ROOT / 'database/04_normalizar_catalogos.sql').read_text(encoding='utf-8')
        sql = sql.replace('USE culturaaccesible;', f'USE {cls.names[0]};')
        with cls.db.cursor() as cursor:
            cursor.execute(sql)
            while cursor.nextset():
                pass

    @classmethod
    def tearDownClass(cls):
        with cls.db.cursor() as cursor:
            for name in cls.names:
                # Solo nombres aleatorios creados por esta ejecución.
                assert name.startswith('cal_test_migracion_') and len(name) == 51
                cursor.execute(f'DROP DATABASE {name}')
        cls.db.close()

    def setUp(self):
        self.db.select_db(self.names[0])

    def test_01_preserves_every_original_row_and_value(self):
        self.assertEqual(digest(self.before), digest(self.after))
        self.assertEqual(self.after['reportes'][0]['comentario'], 'Reporte existente antes de migrar')

    def test_02_repeated_migration_preserves_ids_and_data(self):
        self.migrate()
        self.assertEqual(digest(self.after), digest(snapshot(self.db)))

    def test_03_no_orphaned_categories_or_districts(self):
        with self.db.cursor() as c:
            for sql in ['SELECT COUNT(*) FROM eventos e LEFT JOIN categorias c ON c.id=e.categoria_id WHERE c.id IS NULL',
                        'SELECT COUNT(*) FROM recintos r LEFT JOIN distritos d ON d.id=r.distrito_id WHERE d.id IS NULL']:
                c.execute(sql)
                self.assertEqual(c.fetchone()[0], 0)

    def test_04_unknown_category_is_preserved(self):
        with self.db.cursor() as c:
            c.execute('SELECT c.nombre FROM eventos e JOIN categorias c ON c.id=e.categoria_id WHERE e.id=90')
            self.assertEqual(c.fetchone()[0], 'Categoría nueva con ñ')

    def test_05_foreign_keys_reject_unknown_references(self):
        self.db.begin()
        try:
            with self.db.cursor() as c:
                with self.assertRaises(pymysql.IntegrityError):
                    c.execute('UPDATE eventos SET categoria_id=999999 WHERE id=1')
                with self.assertRaises(pymysql.IntegrityError):
                    c.execute('UPDATE recintos SET distrito_id=999999 WHERE id=1')
        finally:
            self.db.rollback()

    def test_06_duplicate_catalog_names_are_rejected(self):
        self.db.begin()
        try:
            with self.db.cursor() as c:
                for table in ['categorias','distritos']:
                    with self.assertRaises(pymysql.IntegrityError):
                        c.execute(f'INSERT INTO {table}(nombre) SELECT nombre FROM {table} LIMIT 1')
        finally:
            self.db.rollback()

    def test_07_fresh_schema_seed_and_official_import(self):
        from catalog_import import import_catalog
        self.db.select_db(self.names[1])
        execute_sql(self.db, ROOT / 'database/01_schema.sql')
        execute_sql(self.db, ROOT / 'database/02_demo.sql')
        import_catalog(self.db, force=True)
        with self.db.cursor() as c:
            c.execute('SHOW TABLES')
            self.assertEqual(len(c.fetchall()), 9)
            c.execute('SELECT COUNT(*),SUM(e.es_demo=0),SUM(e.es_demo=1) FROM funciones f JOIN eventos e ON e.id=f.evento_id')
            self.assertEqual(tuple(int(v) for v in c.fetchone()), (57,49,8))
        execute_sql(self.db, ROOT / 'database/02_demo.sql')
        with self.db.cursor() as c:
            c.execute('SELECT COUNT(*) FROM funciones')
            self.assertEqual(c.fetchone()[0],57)

    def test_08_original_accessibility_constraints_still_apply(self):
        self.db.begin()
        try:
            with self.db.cursor() as c:
                with self.assertRaises(pymysql.MySQLError):
                    c.execute("INSERT INTO condiciones(tipo_apoyo_id,alcance,recinto_id,funcion_id) VALUES(1,'RECINTO',1,1)")
                with self.assertRaises(pymysql.MySQLError):
                    c.execute("UPDATE funciones SET precio_oficial=-1 WHERE id=1")
        finally:
            self.db.rollback()

    def test_09_standalone_sql_loads_the_complete_catalog(self):
        sql = (ROOT / 'database/CulturaAccesibleLima.sql').read_text(encoding='utf-8')
        sql = sql.replace('CREATE DATABASE IF NOT EXISTS culturaaccesible', 'CREATE DATABASE IF NOT EXISTS ' + self.names[2])
        sql = sql.replace('USE culturaaccesible;', 'USE ' + self.names[2] + ';')
        with self.db.cursor() as c:
            c.execute(sql)
            while c.nextset():
                pass
            c.execute('SELECT COUNT(*),SUM(e.es_demo=0),SUM(e.es_demo=1) FROM funciones f JOIN eventos e ON e.id=f.evento_id')
            self.assertEqual(tuple(int(v) for v in c.fetchone()), (57,49,8))
            c.execute('SELECT COUNT(*) FROM reportes')
            self.assertEqual(c.fetchone()[0],0)
            c.execute('SELECT COUNT(*) FROM eventos WHERE es_demo=0 AND imagen_url LIKE "https://%"')
            self.assertEqual(c.fetchone()[0],49)


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(MigrationTests))
    report = {'executed_at': datetime.now().astimezone().isoformat(), 'tests': result.testsRun,
              'failures': len(result.failures), 'errors': len(result.errors), 'passed': result.wasSuccessful(),
              'scope': 'Migración 7→9 tablas, conservación, repetición, integridad e instalación nueva en bases efímeras propias.'}
    (ROOT / 'docs/evidencias/migration-tests.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    raise SystemExit(0 if result.wasSuccessful() else 1)
