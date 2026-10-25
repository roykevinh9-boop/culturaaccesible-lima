# Arquitectura y estructura modular

Actualización del 24/10/2026 para APF3. El módulo `backend-java` identifica el servidor Java desde la raíz del repositorio. Java utiliza paquetes explícitos `modelo`, `vista` y `controlador`, junto con infraestructura de persistencia separada. El navegador conserva su organización MVC JavaScript.

## MVC del servidor Java

Ruta base: `backend-java/src/main/java/pe/culturaaccesible/`.

| Paquete | Responsabilidad y archivos |
|---|---|
| `modelo/catalogo` | `CatalogService`: filtros, reglas de evidencia y registro de reportes |
| `modelo/chat` | `ChatService`: coordinación de AccesI con el catálogo y Python |
| `modelo/precios` | `PricingService`: comunicación con el servicio de precios |
| `modelo/puertos` | `CatalogStore`: contrato de acceso al catálogo y sus reportes |
| `vista` | `ApiView`: representaciones JSON del catálogo, estado del servicio y mensajes de error |
| `controlador` | `ApiController` y `ApiErrors`: solicitudes HTTP, validación y coordinación de respuestas |
| `infraestructura/jdbc` | Implementación de `CatalogStore` mediante procedimientos almacenados |

Flujo de catálogo: solicitud HTTP → `controlador/ApiController` → `modelo/catalogo/CatalogService` → `modelo/puertos/CatalogStore` → adaptador JDBC → MySQL. El resultado vuelve al controlador y `vista/ApiView` construye la representación JSON. Los registros de `ApiView` mantienen los nombres de campos que utiliza el frontend. Otras operaciones conservan sus respuestas de servicio existentes.

La vista Java presenta datos para la API. La pantalla que ve el usuario se encuentra en `frontend/views`; Maven incorpora esa interfaz al JAR. Las pruebas de Java se distribuyen con los mismos paquetes en `backend-java/src/test/java`.

## MVC del navegador

- Modelo: `frontend/models/catalog-model.js`, acceso a la API y datos del cliente.
- Vista: `frontend/views/catalog-view.js` y `frontend/views/index.html`, representación y controles accesibles.
- Controladores: `frontend/controllers/catalog-controller.js` y `chat-controller.js`, recepción de acciones, navegación, consultas y coordinación de vistas.
- Composición: `frontend/static/js/app.js` conecta las instancias.

La reorganización mantiene la lógica de interacción ya implementada. Los controladores todavía usan utilidades DOM de la vista para enlazar eventos; no se presenta como una interfaz totalmente desacoplada del navegador.

## Cuatro responsabilidades del sistema

| Responsabilidad | Implementación |
|---|---|
| Presentación | HTML, CSS, vista y controladores JavaScript |
| Transporte HTTP y representación | Java `controlador/ApiController`, `controlador/ApiErrors` y `vista/ApiView`; Python `api/routes.py` |
| Aplicación y reglas | Java `modelo/catalogo/CatalogService`, `modelo/chat/ChatService`, `modelo/precios/PricingService`; Python `application/services.py`, `assistant.py` y `model.py` |
| Infraestructura y datos | Java `infraestructura/jdbc/CatalogRepository`, MySQL y clientes HTTP de Python |

## Principio de Arquitectura Limpia aplicado

`modelo/catalogo/CatalogService` depende del contrato `modelo/puertos/CatalogStore`. `infraestructura/jdbc/CatalogRepository` implementa ese contrato y delega en `StoredProcedureExecutor`; `CatalogProcedure` define los nombres y los parámetros de las rutinas. `SimpleJdbcCall` construye la invocación parametrizada. Las sentencias SQL están en `database/procedures/catalog`, `reports` y `system`; Java no conserva cadenas CALL. El servicio puede recibir otra implementación sin importar JDBC. Spring inyecta la implementación concreta al iniciar.

Esto es una mejora de inversión de dependencias, no una migración completa a Clean Architecture: el servicio aún tiene anotaciones Spring y errores HTTP; los contratos utilizan mapas; los clientes de precios y chat todavía contienen transporte HTTP. Separar entidades tipadas, excepciones de dominio y puertos de esos servicios es trabajo posterior.

En Python, `main.py` solo compone la aplicación. `api/schemas.py` valida entradas, `api/routes.py` traduce errores HTTP y `application/services.py` coordina las operaciones sin importar FastAPI. Se conservan `model.py`, `assistant.py` y las rutas públicas para compatibilidad con los datos y pruebas existentes.

Los archivos SQL se agrupan por propósito y las rutas del instalador y de las pruebas se actualizan juntas. El manifiesto centraliza la ubicación y el orden de las cinco rutinas. La reorganización conserva nombres de procedimientos, tablas y datos; no requiere migrar las tablas existentes.
