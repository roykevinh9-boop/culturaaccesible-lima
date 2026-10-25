"""Comprueba los paquetes MVC Java y su separación de SQL sin conexión."""
from pathlib import Path
import json,re
from install_procedures import procedure_scripts

ROOT=Path(__file__).resolve().parents[1]

def verify():
    errors=[]
    java_root=ROOT/'backend-java/src/main/java'
    package_root=java_root/'pe/culturaaccesible'
    for area in ('modelo','vista','controlador'):
        if not any((package_root/area).rglob('*.java')):
            errors.append('Falta una implementación del paquete MVC Java: '+area)
    for path in java_root.rglob('*.java'):
        text=path.read_text(encoding='utf-8')
        expected='.'.join(path.parent.relative_to(java_root).parts)
        if not re.search(r'^package\s+'+re.escape(expected)+r'\s*;',text,re.M):
            errors.append(f'{path.relative_to(ROOT)} no coincide con su paquete Java.')
        if path.is_relative_to(package_root/'modelo') and re.search(
            r'import\s+pe\.culturaaccesible\.(vista|controlador|infraestructura)\.',text):
            errors.append(f'{path.relative_to(ROOT)} depende de una capa externa al modelo.')
        for literal in re.findall(r'"(?:\\.|[^"\\])*"',text,re.S):
            if re.search(r'\b(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|JOIN|CALL)\b',literal,re.I):
                errors.append(f'{path.relative_to(ROOT)} contiene una sentencia SQL en una cadena Java.')
        if re.search(r'import\s+(org\.springframework\.jdbc\.|javax\.sql\.|java\.sql\.)',text):
            if not path.is_relative_to(java_root/'pe/culturaaccesible/infraestructura/jdbc'):
                errors.append(f'{path.relative_to(ROOT)} accede a JDBC fuera de infraestructura.')
    entries=json.loads((ROOT/'database/procedures/manifest.json').read_text(encoding='utf-8'))
    declared={entry['name'] for entry in entries}
    actual={p.resolve() for p in (ROOT/'database/procedures').rglob('*.sql')}
    referenced={(ROOT/'database/procedures'/entry['file']).resolve() for entry in entries}
    if actual!=referenced:errors.append('El manifiesto no coincide con los archivos de procedimientos.')
    contracts=(java_root/'pe/culturaaccesible/infraestructura/jdbc/CatalogProcedure.java').read_text(encoding='utf-8')
    if set(re.findall(r'"(cal_[a-z_]+)"',contracts))!=declared:
        errors.append('Los contratos Java no coinciden con las rutinas del manifiesto.')
    procedure_scripts()
    sql_outside=[p.relative_to(ROOT).as_posix() for area in ('backend-java','frontend','python-service','scripts') for p in (ROOT/area).rglob('*.sql')]
    if sql_outside:errors.append('Hay archivos SQL fuera de database: '+', '.join(sql_outside))
    if errors:raise ValueError('\n'.join(errors))
    return {'java_module':'backend-java','java_mvc_packages':['modelo','vista','controlador'],
            'java_sql_separated':True,'procedures':len(entries),'manifest_complete':True,
            'jdbc_only_in_infrastructure':True}

if __name__=='__main__':print(json.dumps(verify(),ensure_ascii=False))
