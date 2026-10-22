# CulturaAccesible Lima

Aplicación académica para consultar eventos y condiciones de accesibilidad por función. Java sirve la página y consulta MySQL; Python atiende AccesI y la orientación de precios sintéticos.

## Ubicación de los archivos

| Carpeta | Contenido |
|---|---|
| frontend | HTML, estilos y módulos MVC del navegador |
| backend | API Java, servicios, puerto de persistencia y adaptador JDBC |
| python-service | Rutas HTTP, esquemas de entrada, servicios y modelos de demostración |
| database | Esquema, semillas, migración, consultas y exportación SQL |
| scripts | Inicio, compilación, importación y pruebas |
| docs | Diagramas, informes y evidencias con fecha |

Abrir `Abrir-demo.cmd` en Windows y mantener la ventana abierta. Página: http://127.0.0.1:8080/. La base local utiliza el puerto 3307. Las credenciales y los datos privados están en `.local`, excluidos de Git.

Para compilar: `scripts/Compilar.ps1`. Con la demo iniciada, ejecutar `scripts/Probar.ps1`. La compilación incorpora los archivos de frontend al JAR; editar HTML o JavaScript requiere volver a compilar y reiniciar para verlo en la página.

## Documentación vigente

- `docs/Arquitectura_actual.md`: MVC, módulos y límites de la separación de capas.
- `docs/Diseno_visual.md`: colores semánticos y validación de contraste.
- `database/Mapa_SQL.md`: orden y propósito de los scripts.
- `docs/Informe_Semana10.pdf`: entrega histórica del 18/10/2026; describe la versión previa con MVP en la interfaz. El cambio a MVC del 22/10/2026 se documenta por separado para preparar APF3.

Repositorio privado: https://github.com/roykevinh9-boop/culturaaccesible-lima

Tablero privado: https://trello.com/b/ykyaVYXr/culturaaccesible-lima-semana-10

El titular debe gestionar el acceso de quienes revisan. El requisito APF3 de repositorio público sigue pendiente; esta reorganización conserva la visibilidad actual.
