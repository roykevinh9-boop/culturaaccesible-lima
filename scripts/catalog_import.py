"""Importa una instantánea de la cartelera del equipo, con fuentes e imágenes oficiales."""
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parents[1]
FIELDS={
 'eventos':{'fuente_id':'VARCHAR(220) NULL UNIQUE','imagen_url':'VARCHAR(1200) NULL','imagen_alt':'VARCHAR(350) NULL','imagen_credito':'VARCHAR(180) NULL'},
 'funciones':{'fuente_id':'VARCHAR(220) NULL UNIQUE','precio_desde':'INT NOT NULL DEFAULT 0','consultado_en':'DATE NULL'}
}

def migrate(connection):
    with connection.cursor() as cursor:
        for table,fields in FIELDS.items():
            cursor.execute(f'SHOW COLUMNS FROM {table}')
            columns={row[0] for row in cursor.fetchall()}
            for field,definition in fields.items():
                if field not in columns:cursor.execute(f'ALTER TABLE {table} ADD COLUMN {field} {definition}')
        cursor.execute('SHOW COLUMNS FROM funciones LIKE "hora"')
        if cursor.fetchone()[2]=='NO':cursor.execute('ALTER TABLE funciones MODIFY hora TIME NULL')

def import_catalog(connection,force=False):
    path=ROOT/'database/catalogo-oficial.json'
    if not path.exists():return
    content=path.read_bytes();digest=hashlib.sha256(content).hexdigest()
    stamp=ROOT/'.local/catalog-import.sha256'
    if not force and stamp.exists() and stamp.read_text().strip()==digest:return
    data=json.loads(content)
    if len(data['items'])!=len({item['external_id'] for item in data['items']}):raise ValueError('La cartelera contiene identificadores duplicados.')
    migrate(connection)
    connection.begin()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT id,codigo FROM tipos_apoyo')
            supports={code:id for id,code in cursor.fetchall()}
            venues={}
            for index,item in enumerate(data['items']):
                venue_key=(item['venue'],item['district'])
                if venue_key not in venues:
                    cursor.execute('SELECT id FROM recintos WHERE nombre=%s AND distrito=%s',venue_key)
                    found=cursor.fetchone()
                    if found:venue_id=found[0]
                    else:
                        cursor.execute('INSERT INTO recintos(nombre,distrito,direccion) VALUES(%s,%s,%s)',(*venue_key,'Consultar dirección y acceso en la fuente oficial.'))
                        venue_id=cursor.lastrowid
                    venues[venue_key]=venue_id
                venue_id=venues[venue_key]
                cursor.execute('SELECT id FROM eventos WHERE fuente_id=%s',(item['external_id'],));found=cursor.fetchone()
                if found:
                    event_id=found[0]
                    cursor.execute('UPDATE eventos SET nombre=%s,descripcion=%s,categoria=%s,es_demo=0,imagen_url=%s,imagen_alt=%s,imagen_credito=%s WHERE id=%s',(item['title'],item['description'],item['category'],item['image_url'],item['image_alt'],item['image_credit'],event_id))
                else:
                    cursor.execute('INSERT INTO eventos(nombre,descripcion,categoria,es_demo,fuente_id,imagen_url,imagen_alt,imagen_credito) VALUES(%s,%s,%s,0,%s,%s,%s,%s)',(item['title'],item['description'],item['category'],item['external_id'],item['image_url'],item['image_alt'],item['image_credit']))
                    event_id=cursor.lastrowid
                cursor.execute('SELECT id FROM funciones WHERE fuente_id=%s',(item['external_id'],));found=cursor.fetchone()
                if found:
                    function_id=found[0]
                    cursor.execute('UPDATE funciones SET evento_id=%s,recinto_id=%s,fecha=%s,hora=%s,precio_oficial=%s,url_oficial=%s,precio_desde=%s,consultado_en=%s WHERE id=%s',(event_id,venue_id,item['date'],item['time'],item['official_price'],item['official_url'],int(item['price_from']),item['consulted_at'],function_id))
                else:
                    cursor.execute('INSERT INTO funciones(evento_id,recinto_id,fecha,hora,precio_oficial,url_oficial,fuente_id,precio_desde,consultado_en) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)',(event_id,venue_id,item['date'],item['time'],item['official_price'],item['official_url'],item['external_id'],int(item['price_from']),item['consulted_at']))
                    function_id=cursor.lastrowid
                for c in item['conditions']:
                    rid=venue_id if c['scope']=='RECINTO' else None
                    fid=function_id if c['scope']=='FUNCION' else None
                    cursor.execute('SELECT id,evidencia_id FROM condiciones WHERE tipo_apoyo_id=%s AND '+('recinto_id=%s' if rid else 'funcion_id=%s'),(supports[c['code']],rid or fid))
                    condition=cursor.fetchone()
                    evidence_id=condition[1] if condition else None
                    if c['reviewed_at'] and c['source_url']:
                        if evidence_id:
                            cursor.execute('UPDATE evidencias SET fuente=%s,url=%s,fecha_revision=%s,es_demo=0 WHERE id=%s',('Fuente oficial de '+item['image_credit'],c['source_url'],c['reviewed_at'],evidence_id))
                        else:
                            cursor.execute('INSERT INTO evidencias(fuente,url,fecha_revision,es_demo) VALUES(%s,%s,%s,0)',('Fuente oficial de '+item['image_credit'],c['source_url'],c['reviewed_at']))
                            evidence_id=cursor.lastrowid
                    if condition:
                        cursor.execute('UPDATE condiciones SET estado=%s,evidencia_id=%s,observacion=%s WHERE id=%s',(c['state'],evidence_id,c['note'],condition[0]))
                    else:
                        cursor.execute('INSERT INTO condiciones(tipo_apoyo_id,alcance,recinto_id,funcion_id,estado,evidencia_id,observacion) VALUES(%s,%s,%s,%s,%s,%s,%s)',(supports[c['code']],c['scope'],rid,fid,c['state'],evidence_id,c['note']))
        connection.commit()
    except Exception:
        connection.rollback();raise
    stamp.parent.mkdir(exist_ok=True);stamp.write_text(digest,encoding='ascii')
    print(f"Cartelera importada: {len(data['items'])} funciones con imágenes y fuentes. Ejemplos académicos conservados por separado.")

if __name__=='__main__':
    import pymysql,sys
    config=json.loads((ROOT/'.local/runtime.json').read_text(encoding='utf-8'))
    with pymysql.connect(host='127.0.0.1',port=config['db_port'],user='root',password=config['root_password'],database=config['db_name'],charset='utf8mb4',autocommit=True) as connection:
        migrate(connection);import_catalog(connection,force='--force' in sys.argv)
