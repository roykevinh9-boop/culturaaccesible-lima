"""Normaliza categorías y distritos; respalda y verifica los datos existentes."""
from datetime import datetime
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE_TABLES = ('recintos', 'eventos', 'funciones', 'tipos_apoyo', 'evidencias', 'condiciones', 'reportes')


def snapshot(connection):
    """Representación comparable antes y después de sustituir texto por claves."""
    result = {}
    with connection.cursor() as cursor:
        for table in BASE_TABLES:
            cursor.execute(f'SELECT * FROM {table} ORDER BY id')
            columns = [c[0] for c in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
            if table in ('eventos', 'recintos'):
                key, field, catalog = ('categoria_id', 'categoria', 'categorias') if table == 'eventos' else ('distrito_id', 'distrito', 'distritos')
                if key in columns:
                    cursor.execute(f'SELECT id,nombre FROM {catalog}')
                    names = dict(cursor.fetchall())
                    for row in rows:
                        row[field] = names[row.pop(key)]
            result[table] = rows
    return result


def digest(data):
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True, default=str).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def backup(connection, mysql_bin, config):
    folder = ROOT / '.local/backups'
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / ('antes-normalizacion-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.sql')
    # El archivo transitorio con credenciales se elimina incluso si el volcado falla.
    credentials = folder / (target.stem + '.cnf')
    credentials.write_text('[client]\nhost=127.0.0.1\nport=' + str(config['db_port']) + '\nuser=root\npassword=' + config['root_password'] + '\n', encoding='utf-8')
    try:
        subprocess.run([str(Path(mysql_bin) / 'mysqldump.exe'), '--defaults-extra-file=' + str(credentials),
                        '--single-transaction', '--no-tablespaces', '--set-gtid-purged=OFF',
                        '--result-file=' + str(target), config['db_name']], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        if target.stat().st_size < 100:
            raise RuntimeError('El respaldo SQL está incompleto; no se modificó el esquema.')
    finally:
        credentials.unlink(missing_ok=True)
    return target


def normalize(connection, mysql_bin, config):
    with connection.cursor() as cursor:
        cursor.execute("SHOW COLUMNS FROM eventos LIKE 'categoria'")
        legacy_category = cursor.fetchone() is not None
        cursor.execute("SHOW COLUMNS FROM recintos LIKE 'distrito'")
        legacy_district = cursor.fetchone() is not None
    if not (legacy_category or legacy_district):
        return False
    before = snapshot(connection)
    saved = backup(connection, mysql_bin, config)
    from setup_database import execute_sql
    execute_sql(connection, ROOT / 'database/migrations/04_normalizar_catalogos.sql')
    after = snapshot(connection)
    if digest(before) != digest(after):
        raise RuntimeError('La verificación detectó diferencias. Se conserva el respaldo local: ' + str(saved))
    evidence = {
        'executed_at': datetime.now().astimezone().isoformat(),
        'migration': '1.3.0: categorias y distritos normalizados',
        'data_preserved': True, 'sha256_before': digest(before), 'sha256_after': digest(after),
        'rows_preserved': {table: len(rows) for table, rows in before.items()},
        'backup': '.local/backups/' + saved.name,
        'note': 'Respaldo privado excluido de Git y del ZIP; las contraseñas no forman parte de la evidencia.'
    }
    (ROOT / 'docs/evidencias/normalizacion.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Normalización completada: datos conservados y respaldo SQL local disponible.')
    return True
