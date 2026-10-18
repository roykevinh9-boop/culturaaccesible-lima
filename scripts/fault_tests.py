"""Comprueba fallos controlados en instancias Java auxiliares, sin detener la demo."""
from pathlib import Path
import json, os, socket, subprocess, sys, time, unittest, shutil
import urllib.request, urllib.error
from datetime import datetime

ROOT=Path(__file__).resolve().parents[1]
LOCAL=ROOT/'.local'
CONFIG=json.loads((LOCAL/'runtime.json').read_text(encoding='utf-8'))
jdks=sorted(Path(os.environ.get('ProgramFiles','C:/Program Files')).glob('Java/jdk*/bin/java.exe'),key=lambda p:p.stat().st_mtime,reverse=True)
JAVA=os.environ.get('CAL_JAVA_EXE') or (str(jdks[0]) if jdks else shutil.which('java'))
PROCESSES=[]

def call(port,path,payload=None):
    request=urllib.request.Request(f'http://127.0.0.1:{port}{path}',data=None if payload is None else json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(request,timeout=12) as response:return response.status,json.loads(response.read())
    except urllib.error.HTTPError as exc:return exc.code,json.loads(exc.read())

def launch(port,db_port,python_port):
    if not JAVA:raise RuntimeError('No se encontró Java para ejecutar las pruebas auxiliares.')
    for checked in [port,18098,18099]:
        with socket.socket() as sock:
            if sock.connect_ex(('127.0.0.1',checked))==0:raise RuntimeError(f'El puerto auxiliar {checked} está ocupado. No se modificó ese proceso.')
    env=os.environ.copy()
    env.update(CAL_HTTP_PORT=str(port),CAL_DB_URL=f'jdbc:mysql://127.0.0.1:{db_port}/culturaaccesible?connectTimeout=1000&socketTimeout=1000&serverTimezone=America/Lima',CAL_DB_USER=CONFIG['db_user'],CAL_DB_PASSWORD=CONFIG['db_password'],CAL_PYTHON_URL=f'http://127.0.0.1:{python_port}')
    log=(LOCAL/f'fault-{port}.log').open('ab')
    process=subprocess.Popen([JAVA,'-jar',str(ROOT/'app/culturaaccesible.jar')],env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    PROCESSES.append(process)
    for _ in range(80):
        if process.poll() is not None:raise RuntimeError('No pudo iniciar la instancia auxiliar.')
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{port}/',timeout=1) as response:
                if response.status==200:return
        except (urllib.error.URLError,OSError):pass
        time.sleep(.25)
    raise RuntimeError('No respondió la instancia auxiliar.')

class FaultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        launch(18080,CONFIG['db_port'],18099)
        launch(18081,18098,18099)
    def test_python_unavailable_preserves_catalog(self):
        status,data=call(18080,'/api/estimates',{'category':'Teatro','district':'Miraflores','month':6})
        self.assertEqual(status,503);self.assertIn('catálogo',data['message'])
        status,data=call(18080,'/api/functions');self.assertEqual(status,200);self.assertEqual(data['total'],8)
    def test_database_unavailable_never_confirms_report(self):
        status,data=call(18081,'/api/reports',{'function_id':1,'comment':'Prueba de fallo: no debe confirmarse ningún guardado.'})
        self.assertEqual(status,503);self.assertNotIn('id',data);self.assertIn('no está confirmada',data['message'])
    def test_primary_demo_remains_available(self):
        status,data=call(8080,'/api/health');self.assertEqual(status,200);self.assertEqual(data['status'],'ok')

if __name__=='__main__':
    try:
        result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(FaultTests))
        report={'executed_at':datetime.now().astimezone().isoformat(),'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'passed':result.wasSuccessful(),'scope':'Caída de Python y MySQL simuladas en instancias auxiliares; demo principal conservada.'}
        (ROOT/'docs/evidencias/fault-tests.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    finally:
        for process in reversed(PROCESSES):
            if process.poll() is None:
                process.terminate()
                try:process.wait(timeout=8)
                except subprocess.TimeoutExpired:process.kill()
    raise SystemExit(0 if result.wasSuccessful() else 1)
