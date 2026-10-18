"""Inicia los tres componentes con procesos locales y conserva el estado para detenerlos."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
LOCAL=ROOT/".local"

def reachable(url):
    try:
        with urllib.request.urlopen(url,timeout=2) as response:return response.status==200
    except (urllib.error.URLError,TimeoutError,OSError):return False

def wait_ready(url,process,seconds=30):
    for _ in range(seconds*2):
        if process.poll() is not None:raise RuntimeError("Un componente se cerró al iniciar. Revisa los archivos .local/*.log.")
        if reachable(url):return
        time.sleep(.5)
    raise RuntimeError("No se pudo verificar el inicio. Revisa .local/*.log.")

def main(args):
    LOCAL.mkdir(exist_ok=True)
    if reachable('http://127.0.0.1:8080/api/health'):
        print('La aplicación ya está disponible en http://127.0.0.1:8080')
        return
    from setup_database import setup
    setup(args.mysql_bin,args.db_port)
    config=json.loads((LOCAL/'runtime.json').read_text(encoding='utf-8'))
    flags=getattr(subprocess,'CREATE_NO_WINDOW',0)
    children=[]
    state={}
    if (LOCAL/'mysql.pid').exists():state['mysql']=int((LOCAL/'mysql.pid').read_text())
    env=os.environ.copy()
    dep=str(LOCAL/'python')
    env['PYTHONPATH']=dep+os.pathsep+env.get('PYTHONPATH','')
    try:
        if not reachable('http://127.0.0.1:8001/health'):
            log=(LOCAL/'python.log').open('ab')
            python=subprocess.Popen([sys.executable,'-m','uvicorn','main:app','--host','127.0.0.1','--port','8001'],cwd=ROOT/'python-service',env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=flags)
            children.append(python);state['python']=python.pid
            wait_ready('http://127.0.0.1:8001/health',python)
        env.update(CAL_DB_URL=f"jdbc:mysql://127.0.0.1:{args.db_port}/culturaaccesible?useUnicode=true&characterEncoding=UTF-8&serverTimezone=America/Lima",CAL_DB_USER=config['db_user'],CAL_DB_PASSWORD=config['db_password'],CAL_PYTHON_URL='http://127.0.0.1:8001')
        jar=ROOT/'app/culturaaccesible.jar'
        if not jar.exists():jar=ROOT/'backend/target/culturaaccesible-1.0.0.jar'
        if not jar.exists():raise RuntimeError('Falta el ejecutable Java. Compila el proyecto con scripts/Compilar.ps1.')
        log=(LOCAL/'java.log').open('ab')
        java=subprocess.Popen([args.java,'-jar',str(jar)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=flags)
        children.append(java);state['java']=java.pid
        (LOCAL/'processes.json').write_text(json.dumps(state),encoding='utf-8')
        wait_ready('http://127.0.0.1:8080/api/health',java)
        print('\nCulturaAccesible Lima está lista: http://127.0.0.1:8080')
        print('Mantén esta ventana abierta. Presiona Ctrl+C para detener la aplicación.')
        if not args.no_browser:
            import webbrowser
            webbrowser.open('http://127.0.0.1:8080')
        while java.poll() is None:time.sleep(1)
    except KeyboardInterrupt:
        print('\nDeteniendo los componentes de esta demostración...')
    finally:
        for child in reversed(children):
            if child.poll() is None:
                child.terminate()
                try:child.wait(timeout=8)
                except subprocess.TimeoutExpired:child.kill()
        # Cierre normal de MySQL; solo el servidor aislado configurado por este proyecto.
        try:
            import pymysql
            db=pymysql.connect(host='127.0.0.1',port=args.db_port,user='root',password=config['root_password'],connect_timeout=2)
            with db.cursor() as cursor:cursor.execute('SHUTDOWN')
        except Exception:pass
        (LOCAL/'processes.json').unlink(missing_ok=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--java',required=True)
    parser.add_argument('--mysql-bin',required=True)
    parser.add_argument('--db-port',type=int,default=3307)
    parser.add_argument('--no-browser',action='store_true')
    try:main(parser.parse_args())
    except Exception as exc:
        print(f'No se completó el inicio: {exc}',file=sys.stderr)
        sys.exit(1)
