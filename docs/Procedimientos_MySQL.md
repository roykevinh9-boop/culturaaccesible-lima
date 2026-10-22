# Separación de Java y SQL mediante procedimientos almacenados

Actualización del 22/10/2026. Las consultas de producción del catálogo y la inserción de reportes se trasladaron de Java a archivos SQL versionados. Los procedimientos se instalan en MySQL; Java envía parámetros y recibe resultados.

```text
Vista HTML y JavaScript
  → Controlador REST Java
  → CatalogService y CatalogStore
  → CatalogRepository: llamadas CALL con parámetros
  → MySQL: procedimientos en database/procedures/
  → Tablas del catálogo y reportes
```

| Procedimiento | Responsabilidad |
|---|---|
| cal_list_functions | Recuperar eventos, funciones, categorías, recintos e imágenes mediante JOIN |
| cal_function_conditions | Consultar evidencia de una función y su recinto en orden de precedencia |
| cal_support_types | Listar los siete tipos de apoyo |
| cal_health | Comprobar la conexión con el servidor |
| cal_create_report | Validar función, condición y comentario; insertar el reporte y devolver su ID |

Cada procedimiento tiene su propio archivo en `database/procedures/`. Java conserva únicamente las instrucciones `CALL` necesarias para invocarlos; no contiene SELECT, INSERT, UPDATE ni DELETE. Las reglas de confianza y filtros siguen en el servicio Java. Los modelos de IA siguen en Python. MVC organiza la interfaz y no exige copiar SQL dentro de sus controladores.

## Instalación y actualización

`Abrir-demo.cmd` instala las rutinas después del esquema, los datos y las migraciones. El usuario de administración realiza esta instalación y concede a `cal_app` únicamente EXECUTE sobre las cinco rutinas, además de los permisos de tablas ya existentes. Se usa `SQL SECURITY INVOKER`: la llamada no hereda privilegios del administrador que creó la rutina. No se han reducido los permisos de tabla existentes porque siguen siendo necesarios para INVOKER y la configuración actual.

Para actualizar solo las rutinas, desde la raíz del proyecto y con las dependencias Python disponibles: `python scripts/install_procedures.py --backup`. Usa la configuración privada de `.local/runtime.json`. Comprueba el hash de los datos antes y después, guarda un respaldo local y no publica credenciales.

En Workbench: seleccionar el esquema `culturaaccesible`, ejecutar los cinco archivos de `database/procedures/` y luego `database/permissions/cal_app_execute.sql` como administrador. Los archivos contienen DELIMITER para conservar cada bloque BEGIN/END. `CulturaAccesibleLima.sql` sigue siendo la instalación de esquema y datos: después se deben instalar también estos procedimientos, o ejecutar el inicio automático.

Reinstalar reemplaza únicamente las rutinas del proyecto mediante DROP PROCEDURE y CREATE PROCEDURE; no elimina tablas ni filas. MySQL confirma DDL de forma independiente: aplicar con la demo detenida y reiniciarla después evita llamadas durante el reemplazo. Las firmas y los nombres son parte del contrato con Java.

## Pruebas

`scripts/procedure_tests.py` crea una base temporal propia, instala esquema, ejemplos y rutinas y comprueba diez casos. Verifica contratos de salida, rechazos sin escritura, ID y estado del reporte, reinstalación sin cambios de datos y ejecución con la cuenta real de la aplicación. El reporte válido de la prueba se revierte y el esquema temporal se elimina al terminar. La integración HTTP comprueba además Java → procedimiento → MySQL.

Los errores SQLSTATE 45000 se traducen a entrada inválida en Java. Los fallos de conexión conservan la respuesta de servicio no disponible; no se informa un reporte guardado si la persistencia falla.
