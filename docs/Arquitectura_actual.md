# Arquitectura y estructura modular

Actualización del 22/10/2026 para APF3. Se organiza el navegador con MVC y el servidor por responsabilidades. MVC describe la interacción de la interfaz; la separación de capas describe dependencias del sistema. No son tres arquitecturas independientes que haya que implementar simultáneamente.

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
| Transporte HTTP | Java `api/ApiController` y Python `api/routes.py`, validación y respuestas |
| Aplicación y reglas | Java `catalog/CatalogService`, `chat/ChatService`, `pricing/PricingService`; Python `application/services.py`, `assistant.py` y `model.py` |
| Infraestructura y datos | Java `infrastructure/jdbc/CatalogRepository`, MySQL y clientes HTTP de Python |

## Principio de Arquitectura Limpia aplicado

`CatalogService` depende del contrato `catalog/port/CatalogStore`. `CatalogRepository` implementa ese contrato y delega en `StoredProcedureExecutor`; `CatalogProcedure` define los nombres y los parámetros de las rutinas. `SimpleJdbcCall` construye la invocación parametrizada. Las sentencias SQL están en `database/procedures/catalog`, `reports` y `system`; Java no conserva cadenas CALL. El servicio puede recibir otra implementación sin importar JDBC. Spring inyecta la implementación concreta al iniciar.

Esto es una mejora de inversión de dependencias, no una migración completa a Clean Architecture: el servicio aún tiene anotaciones Spring y errores HTTP; los contratos utilizan mapas; los clientes de precios y chat todavía contienen transporte HTTP. Separar entidades tipadas, excepciones de dominio y puertos de esos servicios es trabajo posterior.

En Python, `main.py` solo compone la aplicación. `api/schemas.py` valida entradas, `api/routes.py` traduce errores HTTP y `application/services.py` coordina las operaciones sin importar FastAPI. Se conservan `model.py`, `assistant.py` y las rutas públicas para compatibilidad con los datos y pruebas existentes.

Los archivos SQL se agrupan por propósito y las rutas del instalador y de las pruebas se actualizan juntas. El manifiesto centraliza la ubicación y el orden de las cinco rutinas. La reorganización conserva nombres de procedimientos, tablas y datos; no requiere migrar las tablas existentes.
