# Separación de Java y SQL mediante procedimientos almacenados

Actualización del 24/10/2026. Las consultas del catálogo y la inserción de reportes viven en archivos SQL versionados por módulo. Java identifica la rutina y envía parámetros tipados; no contiene consultas ni cadenas CALL.

El código Java está en `backend-java`. Los paquetes `controlador`, `modelo` y `vista` organizan la API; `infraestructura/jdbc` concentra el adaptador que invoca los procedimientos. Renombrar estos paquetes conserva las cinco rutinas, sus firmas y los datos existentes.

```text
Vista HTML y JavaScript
  → Controlador REST Java
  → CatalogService y CatalogStore
  → CatalogRepository: parámetros y resultados de CatalogStore
  → StoredProcedureExecutor y CatalogProcedure: SimpleJdbcCall
  → MySQL: database/procedures/catalog, reports y system
  → Tablas del catálogo y reportes
```

| Procedimiento | Responsabilidad |
|---|---|
| cal_list_functions | Recuperar eventos, funciones, categorías, recintos e imágenes mediante JOIN |
| cal_function_conditions | Consultar evidencia de una función y su recinto en orden de precedencia |
| cal_support_types | Listar los siete tipos de apoyo |
| cal_health | Comprobar la conexión con el servidor |
| cal_create_report | Validar función, condición y comentario; insertar el reporte y devolver su ID |

Cada rutina tiene su propio archivo en `database/procedures/catalog/`, `reports/` o `system/`. `manifest.json` define su nombre, archivo, entradas y orden de instalación. `CatalogProcedure` declara el contrato Java de los parámetros; `StoredProcedureExecutor` configura `SimpleJdbcCall` sin consultar metadatos de columnas del procedimiento. `CatalogRepository` convierte la salida al contrato del servicio. Las sentencias de consulta, validación de persistencia e inserción permanecen en MySQL.

Las reglas de confianza y los filtros del producto siguen en `CatalogService`; los modelos de IA continúan en Python. La separación evita mezclar lenguajes sin trasladar todas las reglas de la aplicación a la base. Referencia de la API utilizada: [documentación oficial de Spring](https://docs.spring.io/spring-framework/reference/6.2/data-access/jdbc/simple.html#jdbc-simple-jdbc-call).

## Instalación y actualización

`Abrir-demo.cmd` instala las rutinas después del esquema, los datos y las migraciones. El usuario de administración realiza esta instalación y concede a `cal_app` únicamente EXECUTE sobre las cinco rutinas, además de los permisos de tablas ya existentes. Se usa `SQL SECURITY INVOKER`: la llamada no hereda privilegios del administrador que creó la rutina. No se han reducido los permisos de tabla existentes porque siguen siendo necesarios para INVOKER y la configuración actual.

Para actualizar solo las rutinas, desde la raíz del proyecto y con las dependencias Python disponibles: `python scripts/install_procedures.py --backup`. Usa la configuración privada de `.local/runtime.json`. Comprueba el hash de los datos antes y después, guarda un respaldo local y no publica credenciales.

En Workbench: seleccionar `culturaaccesible`, ejecutar los cinco archivos indicados en `database/procedures/manifest.json` y luego `database/permissions/cal_app_execute.sql` como administrador. Los archivos contienen DELIMITER para conservar cada bloque BEGIN/END. `database/exports/CulturaAccesibleLima.sql` permite la instalación alternativa de esquema y datos; después también se instalan las rutinas, o se usa el inicio automático.

El instalador carga y valida el manifiesto completo antes de ejecutar DDL. Un nombre repetido, un archivo ausente o una ruta ajena a la carpeta de rutinas se rechaza antes de reemplazar el primer procedimiento.

Reinstalar reemplaza únicamente las rutinas del proyecto mediante DROP PROCEDURE y CREATE PROCEDURE; no elimina tablas ni filas. MySQL confirma DDL de forma independiente: aplicar con la demo detenida y reiniciarla después evita llamadas durante el reemplazo. Las firmas y los nombres son parte del contrato con Java.

## Pruebas

`scripts/procedure_tests.py` crea una base temporal propia, instala esquema, ejemplos y rutinas y comprueba diez casos. Verifica contratos de salida, rechazos sin escritura, ID y estado del reporte, reinstalación sin cambios de datos y ejecución con la cuenta real de la aplicación. El reporte válido de la prueba se revierte y el esquema temporal se elimina al terminar. La integración HTTP comprueba además Java → procedimiento → MySQL.

Los errores SQLSTATE 45000 se traducen a entrada inválida en Java. Los fallos de conexión conservan la respuesta de servicio no disponible; no se informa un reporte guardado si la persistencia falla.

`python scripts/verify_structure.py` verifica sin conexión que el manifiesto coincide con los archivos y contratos Java, que los imports JDBC solo aparecen en infraestructura y que Java no contiene sentencias SQL. Se ejecuta al comienzo de `scripts/Probar.ps1`. Seis pruebas del adaptador comprueban identificadores numéricos de MySQL, condición opcional nula, errores de entrada, caídas de la base y respuestas sin un identificador único.
