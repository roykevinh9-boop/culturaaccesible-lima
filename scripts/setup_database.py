"""Crea un servidor MySQL de demostración aislado, sin tocar el servicio existente."""
import argparse
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
LOCAL=ROOT/".local"

def execute_sql(connection,path):
    text="\n".join(line for line in path.read_text(encoding="utf-8").splitlines() if not line.lstrip().startswith("--"))
    with connection.cursor() as cursor:
        cursor.execute(text)
        while cursor.nextset():
            pass

def setup(mysql_bin,port):
    import pymysql
    LOCAL.mkdir(exist_ok=True)
    config_file=LOCAL/"runtime.json"
    if config_file.exists():
        config=json.loads(config_file.read_text(encoding="utf-8"))
        if int(config["db_port"])!=port:
            raise RuntimeError("El puerto no coincide con la configuración local existente.")
    else:
        config={"db_port":port,"db_name":"culturaaccesible","db_user":"cal_app","db_password":secrets.token_urlsafe(24),"root_password":secrets.token_urlsafe(28)}
    mysql=Path(mysql_bin)/"mysqld.exe"
    if not mysql.is_file(): raise RuntimeError("No se encontró mysqld.exe en la carpeta indicada.")
    datadir=LOCAL/"mysql-data"
    base=[str(mysql),"--no-defaults",f"--basedir={mysql.parent.parent}",f"--datadir={datadir}"]
    if not (datadir/"mysql").exists():
        if datadir.exists() and any(datadir.iterdir()): raise RuntimeError("La carpeta local contiene una inicialización incompleta. Revísala antes de continuar.")
        datadir.mkdir(exist_ok=True)
        subprocess.run(base+["--initialize-insecure","--console"],check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
    def connect():
        return pymysql.connect(host="127.0.0.1",port=port,user="root",password=config["root_password"],charset="utf8mb4",autocommit=True,connect_timeout=2,client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS)
    try:
        connection=connect()
        print("MySQL de demostración ya está disponible.")
    except pymysql.MySQLError:
        with socket.socket() as sock:
            if sock.connect_ex(("127.0.0.1",port))==0:
                raise RuntimeError("El puerto está ocupado por otro proceso; no se modificó ese servidor.")
        init=LOCAL/"mysql-init.sql"
        init.write_text("ALTER USER 'root'@'localhost' IDENTIFIED BY '"+config["root_password"]+"';\n",encoding="utf-8")
        log=(LOCAL/"mysql-console.log").open("ab")
        process=subprocess.Popen(base+["--bind-address=127.0.0.1",f"--port={port}","--mysqlx=0","--skip-log-bin",f"--init-file={init}","--console"],stdout=log,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
        (LOCAL/"mysql.pid").write_text(str(process.pid),encoding="ascii")
        for attempt in range(60):
            if process.poll() is not None: raise RuntimeError("MySQL no pudo iniciar; consulta .local/mysql-console.log.")
            try:
                connection=connect()
                break
            except pymysql.MySQLError: time.sleep(.5)
        else: raise RuntimeError("MySQL no respondió en el tiempo previsto.")
        init.unlink(missing_ok=True)
        config_file.write_text(json.dumps(config),encoding="utf-8")
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS culturaaccesible CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute("USE culturaaccesible")
            cursor.execute("SHOW TABLES LIKE 'funciones'")
            schema_exists=cursor.fetchone() is not None
        execute_sql(connection,ROOT/"database/schema/01_schema.sql")
        from normalize_database import normalize
        normalize(connection,mysql_bin,config)
        connection.begin()
        try:
            execute_sql(connection,ROOT/"database/seeds/02_demo.sql")
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        from catalog_import import migrate, import_catalog
        migrate(connection)
        import_catalog(connection)
        with connection.cursor() as cursor:
            cursor.execute("CREATE USER IF NOT EXISTS 'cal_app'@'127.0.0.1' IDENTIFIED BY %s",(config["db_password"],))
            cursor.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON culturaaccesible.* TO 'cal_app'@'127.0.0.1'")
        from install_procedures import install, grant_execute
        install(connection)
        grant_execute(connection)
    config_file.write_text(json.dumps(config),encoding="utf-8")
    print(f"Base aislada lista en 127.0.0.1:{port}. Cartelera y ejemplos académicos cargados por separado.")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--mysql-bin",default=r"C:\Program Files\MySQL\MySQL Server 8.0\bin")
    parser.add_argument("--port",type=int,default=3307)
    args=parser.parse_args()
    try: setup(args.mysql_bin,args.port)
    except Exception as exc:
        print(f"No se completó la preparación: {exc}",file=sys.stderr)
        sys.exit(1)
