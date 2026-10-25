# Mapa del proyecto MVC

```text
CulturaAccesibleLima/
├── frontend/                         Interfaz del navegador
│   ├── models/
│   │   ├── catalog-model.js          Datos de la API
│   │   └── support-preferences.js    Selección de apoyos de la pestaña
│   ├── views/
│   │   ├── index.html                Página y diálogos
│   │   ├── catalog-view.js           Tarjetas, fichas y filtros
│   │   └── support-bar-view.js       Barra de apoyos y selección
│   ├── controllers/
│   │   ├── catalog-controller.js     Acciones, rutas y búsqueda
│   │   ├── chat-controller.js        Conversación con AccesI
│   │   └── dialog-controller.js      Recorrido de teclado dentro de los diálogos
│   └── static/
│       ├── css/styles.css            Maquetación adaptable
│       ├── css/theme.css             Colores y barra persistente
│       ├── css/interaction.css       Filtros progresivos, foco y errores por campo
│       └── js/app.js                 Conecta modelo, vista y controlador
├── backend-java/                     Servidor Java 17 y Spring MVC
│   ├── pom.xml                       Dependencias y compilación Maven
│   └── src/
│       ├── main/java/pe/culturaaccesible/
│       │   ├── Application.java      Inicio de Spring Boot
│       │   ├── modelo/
│       │   │   ├── catalogo/         CatalogService: filtros, evidencia y reportes
│       │   │   ├── chat/             ChatService: coordinación de AccesI
│       │   │   ├── precios/          PricingService: orientación de precios
│       │   │   └── puertos/          CatalogStore: contrato de persistencia
│       │   ├── vista/
│       │   │   └── ApiView.java      Representaciones JSON de catálogo, salud y errores
│       │   ├── controlador/
│       │   │   ├── ApiController.java Rutas HTTP y coordinación del modelo y la vista
│       │   │   └── ApiErrors.java    Traducción de errores a respuestas HTTP
│       │   └── infraestructura/jdbc/
│       │       ├── CatalogProcedure.java Contratos de procedimientos MySQL
│       │       ├── StoredProcedureExecutor.java Invocación mediante SimpleJdbcCall
│       │       └── CatalogRepository.java Adaptador de CatalogStore, sin SQL
│       ├── main/resources/           Configuración del servidor Java
│       └── test/java/pe/culturaaccesible/ Pruebas de modelo, vista e infraestructura
├── python-service/
│   ├── main.py                       Inicio de FastAPI
│   ├── api/                          Rutas y validación de entradas
│   ├── application/                  Casos de uso
│   ├── assistant.py                  Clasificación y reglas de AccesI
│   ├── model.py                      Modelos de precios sintéticos
│   ├── data/                         Datos académicos sintéticos
│   └── tests/                        Pruebas Python
├── database/
│   ├── schema/                       Tablas y restricciones
│   ├── seeds/                        Ejemplos e instantánea del catálogo
│   ├── migrations/                   Evolución del esquema existente
│   ├── procedures/
│   │   ├── manifest.json             Contratos y orden de instalación
│   │   ├── catalog/                  Funciones, condiciones y tipos de apoyo
│   │   ├── reports/                  Escritura de reportes
│   │   └── system/                   Estado de la conexión
│   ├── permissions/                  Permisos de ejecución
│   ├── queries/                      Consultas manuales de revisión
│   ├── validation/                   Comprobaciones de integridad
│   ├── workbench/                    Modelado de la base de datos
│   ├── exports/                      Instalación completa alternativa
│   └── testing/                      SQL de versiones anteriores para pruebas
├── scripts/                          Inicio, compilación y pruebas
└── docs/                             Diagramas, informes y evidencias
```

Java se identifica desde la raíz como `backend-java`. Dentro de su código, los paquetes `modelo`, `vista` y `controlador` tienen responsabilidades y clases ejecutables. `controlador` recibe las solicitudes, coordina los servicios de `modelo` y utiliza `vista/ApiView` para presentar las respuestas de catálogo, salud y errores en JSON. Las pantallas HTML y su MVC JavaScript se encuentran en `frontend`.

La persistencia se conecta al modelo mediante `CatalogStore`; el adaptador se encuentra en `infraestructura/jdbc` y los procedimientos SQL en `database`. Python conserva su servicio auxiliar para AccesI y precios. Los eventos, recintos y condiciones permanecen en el esquema MySQL.

Maven publica `views/index.html` como página inicial del JAR y copia el resto del frontend respetando sus carpetas. Por eso la URL de inicio sigue siendo `/`, mientras que los estilos se sirven desde `/static/css/`. Abrir la carpeta completa en VS Code permite ver esta organización sin mezclar los lenguajes.

## Barra de apoyos

La barra permanece visible al desplazarse y admite varios apoyos a la vez. Cada botón mantiene `aria-pressed` y se sincroniza con las casillas del formulario. “Todos los apoyos” elimina solo el filtro de apoyos; el botón “Limpiar filtros” reinicia todos los filtros. La selección se conserva en `sessionStorage` de esta pestaña y se valida contra los apoyos del catálogo; no se envía a un servicio de perfiles.

Para probar la persistencia: ejecutar `node --test scripts/test_support_preferences.mjs` con una versión actual de Node. Las otras pruebas se ejecutan con los scripts descritos en `PROYECTO.md`.

## Filtros y recuperación de errores

Fecha y precio están visibles; el panel adicional conserva distrito, disciplina, apoyos y selección de catálogo. Las etiquetas activas permiten quitar criterios individuales. Limpiar puede deshacerse y cerrar una ficha devuelve el foco a la tarjeta de origen. Las consultas tienen una espera máxima y reintento explícito. Los reportes conservan el comentario si hay un error y no se reenvían automáticamente.

El catálogo carga funciones, tipos de apoyo y condiciones en bloque mediante tres llamadas de persistencia. La revisión y sus escenarios están en `docs/Revision_UX_2026-10-25.md`.

## Separación Java y SQL

`CatalogRepository` convierte entradas y resultados; `StoredProcedureExecutor` configura las invocaciones y `CatalogProcedure` identifica sus parámetros. La lectura y escritura de tablas vive en los procedimientos MySQL. `python scripts/verify_structure.py` comprueba los tres paquetes MVC Java, la correspondencia entre paquetes y carpetas, la separación del modelo, la ausencia de consultas SQL en Java y la cobertura del manifiesto de rutinas.
