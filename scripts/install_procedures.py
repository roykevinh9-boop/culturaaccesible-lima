"""Instala las rutinas versionadas en el esquema seleccionado por el llamador.

DELIMITER es una instrucción del cliente Workbench, no del servidor MySQL.
Este lector acepta los delimitadores de nuestros archivos sin dividir sus BEGIN/END.
"""
from pathlib import Path
import argparse
import json
import re

ROOT=Path(__file__).resolve().parents[1]
PROCEDURE_ROOT=ROOT/'database/procedures'

def procedure_scripts():
    """Comprueba todo el manifiesto antes de reemplazar la primera rutina."""
    entries=json.loads((PROCEDURE_ROOT/'manifest.json').read_text(encoding='utf-8'))
    if not isinstance(entries,list) or not entries:
        raise ValueError('El manifiesto de procedimientos está vacío o no es una lista.')
    names=set();scripts=[]
    for entry in entries:
        name=entry['name'];path=(PROCEDURE_ROOT/entry['file']).resolve()
        if not re.fullmatch(r'cal_[a-z_]+',name) or name in names:
            raise ValueError('Nombre de rutina no válido o repetido.')
        if not path.is_relative_to(PROCEDURE_ROOT.resolve()) or path.suffix!='.sql':
            raise ValueError('El procedimiento debe estar dentro de database/procedures.')
        text=path.read_text(encoding='utf-8')
        if not re.search(r'\bCREATE\s+PROCEDURE\s+'+re.escape(name)+r'\s*\(',text,re.I):
            raise ValueError('La rutina no coincide con el nombre del manifiesto: '+name)
        scripts.append((name,list(statements(text))))
        names.add(name)
    return scripts

def statements(script):
    delimiter=';'
    pending=[]
    for line in script.splitlines():
        stripped=line.strip()
        if not stripped or stripped.startswith('--'):
            continue
        if stripped.upper().startswith('DELIMITER '):
            if pending: raise ValueError('Sentencia incompleta antes de DELIMITER.')
            delimiter=stripped.split(None,1)[1]
            continue
        pending.append(line)
        if stripped.endswith(delimiter):
            yield '\n'.join(pending).rstrip()[:-len(delimiter)].strip()
            pending=[]
    if pending: raise ValueError('Falta el delimitador final del procedimiento.')

def install(connection):
    scripts=procedure_scripts()
    with connection.cursor() as cursor:
        for name,script in scripts:
            for statement in script:
                cursor.execute(statement)
                while cursor.nextset(): pass

def grant_execute(connection):
    # Permisos versionados junto al SQL; no se construyen consultas desde entradas del usuario.
    with connection.cursor() as cursor:
        script=(ROOT/'database/permissions/cal_app_execute.sql').read_text(encoding='utf-8')
        for statement in statements(script):cursor.execute(statement)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--backup',action='store_true');args=parser.parse_args()
    import pymysql
    config=json.loads((ROOT/'.local/runtime.json').read_text(encoding='utf-8'))
    with pymysql.connect(host='127.0.0.1',port=config['db_port'],user='root',password=config['root_password'],database=config['db_name'],charset='utf8mb4',autocommit=True) as db:
        from normalize_database import backup,snapshot,digest
        before=digest(snapshot(db))
        if args.backup: backup(db,r'C:/Program Files/MySQL/MySQL Server 8.0/bin',config)
        install(db);grant_execute(db)
        assert before==digest(snapshot(db)), 'Cambió el contenido de las tablas.'
    print('Procedimientos instalados. Datos conservados; credenciales no publicadas.')
