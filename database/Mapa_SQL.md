# Base de datos y procedimientos MySQL

Las tablas, consultas y rutinas se mantienen en `database/`. Java invoca procedimientos por nombre con parámetros tipados mediante `SimpleJdbcCall`; no contiene sentencias SQL ni cadenas `CALL`.

```text
database/
├── schema/01_schema.sql
├── seeds/
│   ├── 02_demo.sql
│   └── catalogo-oficial.json
├── migrations/04_normalizar_catalogos.sql
├── procedures/
│   ├── manifest.json
│   ├── catalog/
│   │   ├── cal_list_functions.sql
│   │   ├── cal_function_conditions.sql
│   │   └── cal_support_types.sql
│   ├── reports/cal_create_report.sql
│   └── system/cal_health.sql
├── permissions/cal_app_execute.sql
├── queries/03_consultas.sql
├── validation/06_verificar_integridad.sql
├── workbench/05_modelo_workbench.sql
├── exports/CulturaAccesibleLima.sql
└── testing/legacy/
    ├── legacy_schema.sql
    └── legacy_demo.sql
```

| Archivo | Uso |
|---|---|
| schema/01_schema.sql | Crear las nueve tablas y sus restricciones en una instalación nueva |
| seeds/02_demo.sql | Cargar los ejemplos académicos identificados como ficticios |
| queries/03_consultas.sql | Consultas manuales de revisión; no se copian al código Java |
| migrations/04_normalizar_catalogos.sql | Migrar categorías y distritos; el inicio guarda respaldo privado |
| workbench/05_modelo_workbench.sql | Importar la estructura del modelo físico en Workbench |
| validation/06_verificar_integridad.sql | Revisar relaciones y recuentos sin modificar datos |
| exports/CulturaAccesibleLima.sql | Instalación completa alternativa con la instantánea oficial y los ejemplos |
| seeds/catalogo-oficial.json | Instantánea recuperada el 17/10/2026 para el importador |
| procedures/manifest.json | Orden de instalación, ubicación y parámetros de las cinco rutinas |
| procedures/catalog/*.sql | Funciones, condiciones y tipos de apoyo |
| procedures/reports/cal_create_report.sql | Validación y escritura de reportes; devuelve el identificador |
| procedures/system/cal_health.sql | Comprobación de la conexión |
| permissions/cal_app_execute.sql | Permisos EXECUTE de la cuenta existente sobre esas cinco rutinas |

## Orden de instalación

`Abrir-demo.cmd` prepara esquema, migración, datos y procedimientos. El inicio y las pruebas usan las nuevas rutas. Para una instalación manual puede usarse `exports/CulturaAccesibleLima.sql` y luego las cinco rutinas en el orden de `procedures/manifest.json`, seguidas de sus permisos. Los archivos de modelado, consultas y validación son herramientas de revisión, no migraciones adicionales.

Para actualizar solo las rutinas con la demo detenida: `python scripts/install_procedures.py --backup`. El instalador valida todos los archivos antes de reemplazar la primera rutina y comprueba que las tablas conserven sus datos. Las contraseñas y los reportes privados permanecen en `.local`, fuera del repositorio.
