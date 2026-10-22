"""Instala las rutinas versionadas en el esquema seleccionado por el llamador.

DELIMITER es una instrucción del cliente Workbench, no del servidor MySQL.
Este lector acepta los delimitadores de nuestros archivos sin dividir sus BEGIN/END.
"""
from pathlib import Path
import argparse
import json

ROOT=Path(__file__).resolve().parents[1]
PROCEDURES=('cal_list_functions','cal_function_conditions','cal_support_types','cal_health','cal_create_report')

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
    with connection.cursor() as cursor:
        for name in PROCEDURES:
            for statement in statements((ROOT/'database/procedures'/f'{name}.sql').read_text(encoding='utf-8')):
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
    print('Cinco procedimientos instalados. Datos conservados; credenciales no publicadas.')
