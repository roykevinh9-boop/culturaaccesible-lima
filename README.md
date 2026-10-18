# CulturaAccesible Lima · Semana 10

PMV1 académico con **Java + Python + MySQL**, interfaz web organizada en **MVP (Modelo-Vista-Presentador)** y pruebas reales de integración.

Lee primero **LEEME_PRIMERO.md**: contiene una explicación simple del proyecto, MySQL y AccesI.

## Inicio rápido en Windows

1. Extrae el ZIP completo a una carpeta de trabajo.
2. Verifica que tienes **Java 17 o posterior, Python 3.11/3.12 y MySQL Server 8.0.16 o posterior**.
3. Haz doble clic en **Abrir-demo.cmd**.
4. Espera a que aparezca `CulturaAccesible Lima está lista` y abre **http://127.0.0.1:8080**.
5. Mantén abierta la ventana de inicio. Usa **Ctrl+C** en esa ventana para detener la demostración.

La primera ejecución descarga dependencias oficiales de Python. Java ya está compilado en `app/culturaaccesible.jar`. El programa detecta el Java instalado y el MySQL Server 8.0 habitual. Si utilizas otras rutas, ajusta `Iniciar.ps1`. No requiere modificar el servicio MySQL existente.

El inicio crea una instancia **aislada** de MySQL en el puerto **3307** con datos propios dentro de `.local/mysql-data`, base `culturaaccesible`, un usuario de aplicación y contraseñas aleatorias locales. No usa la contraseña de tu instalación principal. Si el puerto está ocupado por otro servidor, se detiene sin modificarlo.

La cartelera principal incorpora **49 funciones recuperadas de la web del equipo el 17/10/2026**, con fotos remotas, créditos y enlaces a fuentes oficiales. Es una instantánea; no se actualiza automáticamente y no acredita una nueva verificación independiente de cada actividad. Los horarios que no se pudieron confirmar quedan pendientes. Los ocho ejemplos ficticios de la semilla se consultan en un modo separado. No se venden ni reservan entradas.

## Qué funciona

- Buscar por título, disciplina o recinto, con normalización de tildes.
- Combinar fecha, distrito, categoría, precio y apoyos indispensables.
- Distinguir ingreso gratuito de precio no informado.
- Abrir una ficha por función, con estados textuales, alcance, fuente y revisión.
- Convertir evidencia ausente o vencida en **No confirmado**.
- Evitar trasladar automáticamente LSP, subtítulos, audiodescripción y apoyos táctiles del recinto a una función.
- Compartir enlaces directos a fichas conservando el identificador de función.
- Registrar reportes de prueba en MySQL con estado **PENDIENTE**.
- Consultar Python desde Java para obtener precio orientativo y clase hasta/mayor de S/ 40.
- Explicar el uso de datos sintéticos y avisar si los modelos discrepan.
- Conversar con **AccesI**, IA local de intenciones con TF-IDF y regresión logística, más reglas de fechas y precios. Responde a saludos, conserva filtros y consulta eventos obtenidos de MySQL; sin proveedor generativo externo.
- Mostrar fotos con texto alternativo y crédito; abrir la fuente oficial de cada función.
- Cambiar tamaño de texto, contraste, subrayado y movimiento; ajustes guardados en este navegador.
- Operar diálogos nativos y cerrar con Escape; diseño adaptado a pantalla pequeña.

## Alcance y límites

El alcance implementado es **descubrir y comprobar**, más la orientación de precios y el reporte de inconsistencias como extensiones académicas. Las 18 historias se encuentran en `docs/historias.json` y en el informe. No se declara que las 18 estén implementadas.

Las cuentas, panel del organizador, solicitudes reales de apoyo, seguimiento de respuestas, preferencias de perfil, comparador, revisión con permisos y notificaciones quedan en el backlog. Tampoco se ha realizado una auditoría WCAG completa ni pruebas con usuarios o lectores de pantalla reales.

La arquitectura **MVP se aplica a la interfaz**: `view.js` presenta, `presenter.js` coordina y `model.js` accede a datos. El servidor Java usa un adaptador HTTP, servicios de negocio y repositorio JDBC. El uso de Spring no convierte por sí solo la interfaz en MVP.

La guía original menciona MVC o hexagonal. Esta entrega usa MVP siguiendo la elección comunicada por el equipo; debe explicarse esa decisión al docente.

## Organización

```text
CulturaAccesibleLima/
  Abrir-demo.cmd             Inicio de la demostración
  Iniciar.ps1                Detección y preparación del entorno
  app/culturaaccesible.jar   Ejecutable Java con la web incluida
  backend/                  Código Java, Maven y pruebas de negocio
  frontend/                 HTML, CSS y módulos MVP en JavaScript
  python-service/           FastAPI, modelos, datos sintéticos y pruebas
  database/                 Esquema y semilla MySQL
  scripts/                  Inicio, compilación y pruebas de integración
  docs/                     Informe, historias, matrices, diagramas y evidencias
  .local/                   Datos de ejecución privados, excluidos del ZIP y Git
```

## Abrir en Visual Studio Code o IntelliJ

En VS Code abre `CulturaAccesibleLima.code-workspace` y usa Terminal → Ejecutar tarea para iniciar, compilar o probar. También puedes abrir la carpeta completa y utiliza las recomendaciones de `.vscode/extensions.json`. En IntelliJ abre `backend/pom.xml` como proyecto Maven. La parte Python también puede editarse en VS Code. La interfaz se modifica en `frontend/`; luego se recompila Java para actualizar el ejecutable.

Para reconstruir ejecuta `scripts/Compilar.ps1` **con la aplicación detenida**, porque Windows bloquea el archivo JAR en ejecución. El script busca Maven en PATH o en IntelliJ y ejecuta las pruebas antes de copiar el JAR a `app/`.

Para Python, el archivo `requirements-lock.txt` conserva las versiones verificadas. Para un entorno independiente también puedes crear un entorno virtual e instalarlo con `python -m pip install -r python-service/requirements-lock.txt`.

## Pruebas

Con la demo iniciada ejecuta `scripts/Probar.ps1`. Las reglas Java se comprueban al compilar y también pueden ejecutarse desde IntelliJ. Las evidencias de esta sesión están en `docs/evidencias`.

- 20 pruebas de reglas en Java.
- 43 pruebas del servicio Python.
- 39 pruebas de integración HTTP/Java/Python/MySQL.
- 9 pruebas de migración, integridad e instalación de MySQL en bases efímeras propias.
- 4 pruebas de fallos controlados: ausencia de Python y MySQL, conservando la demo principal.
- Revisión manual del navegador: filtros, fichas, reportes, estimación, navegación de diálogos y tamaño móvil.

El conjunto de pruebas de integración registra un reporte con texto explícito de prueba. No borra ni modifica información de bases externas. Las cantidades y resultados finales deben contrastarse con los archivos XML/JSON incluidos.

Las pruebas de fallos abren instancias auxiliares en 18080 y 18081, y se cierran al terminar. Se pueden omitir con `scripts/Probar.ps1 -SinFallos`.

## API

| Operación | Ruta |
|---|---|
| Salud de Java y MySQL | `GET /api/health` |
| Distritos, categorías y apoyos | `GET /api/metadata?source=official` |
| Búsqueda y filtros | `GET /api/functions?source=official&q=&district=&category=&date=all&price=all&needs=lsp` |
| Ficha por función | `GET /api/functions/{id}` |
| Registrar reporte | `POST /api/reports` con `function_id`, `comment` y `condition_id` opcional |
| Estimación a través de Java | `POST /api/estimates` con `category`, `district` y `month` |
| Conversación con AccesI | `POST /api/chat` con `message`, `context` opcional y `source` official/demo |
| Servicio Python | `GET http://127.0.0.1:8001/health` y `/docs` |

El modelo Python utiliza **40 registros sintéticos nuevos**, semilla 42, cinco categorías, dos distritos y meses 1, 4, 7 y 10 como datos de entrenamiento disponibles. Acepta consultas en meses 1 a 12 como interpolación/extrapolación de demostración, sin acreditar estacionalidad. Usa regresión lineal y árbol de clasificación independientes. No reproduce las métricas del PDF previo; sus métricas se recalculan y se presentan como resultados de esta implementación.

## MySQL Workbench

La aplicación guarda la configuración de la instancia de demostración en `.local/runtime.json`. Consulta ese archivo **solo en tu equipo** para crear una conexión local a 127.0.0.1:3307 con el usuario `cal_app`. No publiques ese archivo ni sus contraseñas. El usuario de aplicación tiene permisos de datos sobre una sola base y no permisos globales de administración.

Para un servidor MySQL propio, crea una base vacía y aplica `database/01_schema.sql` y `database/02_demo.sql`. Configura las variables de `.env.example` en el entorno del proceso Java; Java no carga automáticamente archivos `.env`. Esta modalidad es manual y no usa `Iniciar.ps1`.

## GitHub y Trello

Se entrega el código listo para un repositorio. El historial Git local, cuando se incluye en la carpeta de trabajo, registra la implementación asistida. **No se ha publicado un repositorio en GitHub ni creado un tablero en Trello.**

El archivo `repositorio.bundle` conserva el repositorio Git y su commit real de implementación. Para recuperar el historial en otra carpeta se puede usar `git clone repositorio.bundle CulturaAccesibleRepo`. El ejecutable compilado y los archivos de entrega se conservan en el ZIP, fuera del historial de código.

Para GitHub: crea un repositorio vacío en tu cuenta, añade su URL como remoto y sube `main`. Usa ramas `feature/...` y pull requests para cambios siguientes. No subas `.local`, `.env`, contraseñas, datos de MySQL ni carpetas generadas.

Para Trello: crea las listas **Por hacer**, **En desarrollo**, **En pruebas** y **Terminado**. `docs/backlog-trello.csv` facilita copiar las tarjetas con historia, criterios, prioridad y estado. No se presupone una importación CSV nativa de Trello.

## Entrega académica

Lee `docs/Informe_Semana10.pdf`, su versión editable en Markdown, la matriz de herramientas y los diagramas PlantUML/SVG. La asignación nominal de roles es una propuesta para que el equipo la revise. Las evidencias corresponden a verificaciones técnicas locales; no acreditan validación de accesibilidad de recintos reales.

La instalación se verificó también desde una copia limpia extraída del ZIP en una ruta con espacios: descargó dependencias, inicializó otra carpeta MySQL y conectó Java con Python. El resultado está en `docs/evidencias/instalacion-limpia.json`.

## Cartelera y conexión local actualizadas

`source=official` es el catálogo predeterminado; `source=demo` devuelve los ocho ejemplos ficticios y `source=all` sirve para inspección explícita. `database/catalogo-oficial.json` conserva la procedencia de las 49 funciones. No se atribuyen los apoyos del recinto a una función cuando requieren confirmación por sesión. Los precios «Desde» conservan ese calificativo; NULL no se convierte en cero. Hora NULL se muestra como pendiente.

`scripts/catalog_import.py` aplica las nuevas columnas y carga la instantánea sin duplicar funciones. El inicio lo ejecuta cuando cambia el archivo; no descarga una nueva cartelera. `--force` vuelve a aplicar la instantánea. El hash local evita sobrescribir cambios manuales en cada arranque. La base mantiene los reportes existentes.

La conexión MySQL verificada está en **127.0.0.1:3307**, base **culturaaccesible**, usuario **cal_app**. Es una instancia real con el MySQL instalado en esta PC. Workbench tiene guardada la conexión CulturaAccesible Lima. Verificación del 18/10/2026: puerto 3307, usuario cal_app, base culturaaccesible y 57 funciones (49 de cartelera y ocho ejemplos). Las claves están únicamente en `.local/runtime.json`, excluidas de la entrega.

## AccesI: versión 1.2

Se comprobó en el primer enlace del equipo que AccesI contesta a «hola» y consulta por mes y tarifa. En esa prueba «los más caros el 18 de octubre» devolvió fechas de otros días de octubre. La versión local aplica el día exacto, también interpreta hoy, mañana, fin de semana, este mes, próximo mes y días de la semana. «Baratos» y «caros» ordenan tarifas publicadas; un precio no informado se excluye de la comparación.

La IA local está en `python-service/assistant.py`: clasificador TF-IDF de caracteres + regresión logística entrenado sobre ejemplos académicos de seis intenciones. No se declara una precisión medida en conversaciones reales ni equivalencia con un modelo generativo. Las respuestas se construyen con reglas sobre los datos que Java obtiene desde MySQL, sin inventar apoyos, horarios o tarifas.

El cliente conserva solamente los filtros de conversación en memoria de la pestaña. Nueva conversación, cambio de catálogo o recarga los limpia. No hay almacenamiento del texto conversado ni servicio externo de IA. Una caída de Python produce un aviso; el catálogo sigue disponible. El modelo de predicción de precios sintéticos es independiente y no se usa para clasificar las tarifas oficiales.

Pruebas de la versión: **20 Java + 43 Python + 39 integración + 4 fallos + 9 migración = 115 aprobadas**. Las pruebas de migración comprueban tanto la versión anterior como una instalación nueva con esquema, semilla e importador, además del SQL completo.


La conexión visual de Workbench se completó el 18/10/2026; el informe actualizado el 18/10/2026 incorpora la conexión verificada y su evidencia visual. Las evidencias mysql-workbench-conexion.jpg y mysql-workbench-datos.jpg documentan el estado actualizado.


## Base normalizada: versión 1.3

La base tiene **9 tablas**. `categorias` guarda nombres únicos y `eventos.categoria_id` la referencia; `distritos` hace lo mismo con `recintos.distrito_id`. Las otras siete tablas mantienen sus datos y relaciones. Java realiza JOIN y devuelve los mismos nombres a la web y a Python.

- **Ver como el diagrama del equipo:** abre `docs/CulturaAccesibleLima.mwb` en Workbench. Incluye nueve tablas y diez relaciones. `docs/base-datos-workbench.png` permite verlo sin Workbench; PlantUML/SVG documentan una vista resumida.
- **Base actual:** ya está migrada. El inicio detecta las columnas antiguas y aplica `04_normalizar_catalogos.sql` después de guardar un volcado privado en `.local/backups/`. La migración puede repetirse sin duplicar datos. MySQL confirma los cambios de estructura por sentencia; no debe interrumpirse.
- **Otra PC / base nueva y vacía:** abre y ejecuta `database/CulturaAccesibleLima.sql`. Incluye las nueve tablas, las fotos y fuentes, 49 funciones recuperadas y ocho ejemplos. No incluye credenciales ni reportes privados. Para conectar la aplicación en esta modalidad, configura las variables de entorno indicadas arriba.
- **Solo modelado:** `database/05_modelo_workbench.sql` contiene la estructura para importar mediante File → Import → Reverse Engineer MySQL Create Script. El SQL es la referencia para los CHECK.
- **Conservación:** `docs/evidencias/normalizacion.json` registra hashes iguales antes/después y el recuento de cada tabla. Se conservaron los cinco reportes existentes; la prueba de integración posterior registra otro reporte de prueba.

La captura mysql-workbench-datos.jpg documenta la conexión anterior con siete tablas. El modelo .mwb y los diagramas actuales muestran la estructura mejorada.
