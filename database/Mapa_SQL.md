# Organización de los scripts SQL

| Archivo | Uso |
|---|---|
| 01_schema.sql | Crear las nueve tablas y sus restricciones en una instalación nueva |
| 02_demo.sql | Cargar los ejemplos académicos identificados como ficticios |
| 03_consultas.sql | Consultar catálogo, condiciones y relaciones mediante JOIN |
| 04_normalizar_catalogos.sql | Migrar categorías y distritos de la versión anterior; el inicio guarda respaldo privado |
| 05_modelo_workbench.sql | Importar la estructura del modelo físico en Workbench |
| 06_verificar_integridad.sql | Revisar relaciones y recuentos sin modificar datos |
| CulturaAccesibleLima.sql | Instalación completa alternativa con la instantánea oficial y los ejemplos |
| catalogo-oficial.json | Instantánea recuperada el 17/10/2026 para el importador |

Usar la instalación completa o el flujo de esquema más importación, según el caso; no ejecutar todos los archivos por número como si fueran una única migración. El script 05 es para modelado. Los datos privados de reportes y contraseñas no forman parte de la exportación distribuida. Se mantienen los nombres porque el inicio y las pruebas los utilizan.
