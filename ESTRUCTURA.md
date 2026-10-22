# Mapa del proyecto MVC

```text
CulturaAccesibleLima/
├── frontend/                         Interfaz del navegador
│   ├── index.html                    Página y diálogos
│   ├── styles.css                    Maquetación adaptable
│   ├── theme.css                     Colores y barra persistente
│   └── js/
│       ├── app.js                    Conecta modelo, vista y controlador
│       ├── models/
│       │   ├── catalog-model.js      Datos de la API
│       │   └── support-preferences.js Selección de apoyos de la pestaña
│       ├── views/
│       │   ├── catalog-view.js       Tarjetas, fichas y filtros
│       │   └── support-bar-view.js   Barra de apoyos y estados de selección
│       └── controllers/
│           ├── catalog-controller.js Acciones, rutas y búsqueda
│           └── chat-controller.js   Conversación con AccesI
├── backend/src/main/java/pe/culturaaccesible/
│   ├── api/                          Controlador REST y errores HTTP
│   ├── catalog/                      Reglas y puerto CatalogStore
│   ├── infrastructure/jdbc/          Adaptador MySQL
│   ├── chat/                         Servicio de conversación
│   └── pricing/                      Servicio de precios
├── python-service/
│   ├── main.py                       Inicio de FastAPI
│   ├── api/                          Rutas y validación de entradas
│   ├── application/                  Casos de uso
│   ├── assistant.py                  Clasificación y reglas de AccesI
│   ├── model.py                      Modelos de precios sintéticos
│   ├── data/                         Datos académicos sintéticos
│   └── tests/                        Pruebas Python
├── database/                         Esquema SQL, consultas y migraciones
├── scripts/                          Inicio, compilación y pruebas
└── docs/                             Diagramas, informes y evidencias
```

La división MVC es explícita en la interfaz. El servidor Java usa Spring MVC para su API y mantiene reglas y persistencia separadas mediante un puerto. Python conserva un servicio auxiliar: sus modelos predictivos no son las entidades de la base de datos. Los eventos, recintos y condiciones se definen en el esquema MySQL; no se agregan archivos de entidades vacíos para imitar otro framework.

## Barra de apoyos

La barra permanece visible al desplazarse y admite varios apoyos a la vez. Cada botón mantiene `aria-pressed` y se sincroniza con las casillas del formulario. “Todos los apoyos” elimina solo el filtro de apoyos; el botón “Limpiar filtros” reinicia todos los filtros. La selección se conserva en `sessionStorage` de esta pestaña y se valida contra los apoyos del catálogo; no se envía a un servicio de perfiles.

Para probar la persistencia: ejecutar `node --test scripts/test_support_preferences.mjs` con una versión actual de Node. Las otras pruebas se ejecutan con los scripts descritos en `PROYECTO.md`.
