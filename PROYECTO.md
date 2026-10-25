# CulturaAccesible Lima

Aplicación académica para consultar eventos y condiciones de accesibilidad por función. Java sirve la página e invoca procedimientos MySQL mediante un adaptador; Python atiende AccesI y la orientación de precios sintéticos.

## Ubicación de los archivos

| Carpeta | Contenido |
|---|---|
| frontend | HTML, estilos y módulos MVC del navegador |
| backend-java | Servidor Java 17: paquetes modelo, vista y controlador, con adaptador JDBC separado |
| python-service | Rutas HTTP, esquemas de entrada, servicios y modelos de demostración |
| database | SQL separado en schema, seeds, migrations, procedures, permissions, queries, validation, workbench, exports y testing |
| scripts | Inicio, compilación, importación y pruebas |
| docs | Diagramas, informes y evidencias con fecha |

Abrir `Abrir-demo.cmd` en Windows y mantener la ventana abierta. Página: http://127.0.0.1:8080/. La base local utiliza el puerto 3307. Las credenciales y los datos privados están en `.local`, excluidos de Git.

Para compilar: `scripts/Compilar.ps1`, que utiliza `backend-java/pom.xml` y limpia clases anteriores antes de compilar. Con la demo iniciada, ejecutar `scripts/Probar.ps1`. La compilación incorpora los archivos de frontend al JAR; editar HTML o JavaScript requiere volver a compilar y reiniciar para verlo en la página.

Para revisar los paquetes MVC Java y la separación de lenguajes sin iniciar servicios: `python scripts/verify_structure.py`. Cada rutina tiene su archivo SQL y se registra en `database/procedures/manifest.json`. Java no contiene consultas ni instrucciones CALL escritas como texto.

## Documentación vigente

- `ESTRUCTURA.md`: árbol de carpetas MVC y funcionamiento de la barra de apoyos.
- `docs/Arquitectura_actual.md`: MVC, módulos y límites de la separación de capas.
- `docs/Diseno_visual.md`: colores semánticos y validación de contraste.
- `database/Mapa_SQL.md`: orden y propósito de los scripts.
- `docs/Procedimientos_MySQL.md`: consultas en MySQL y llamadas parametrizadas desde Java.
- `docs/Informe_Semana10.pdf`: entrega histórica del 18/10/2026; describe la versión previa con MVP en la interfaz. El cambio a MVC del 22/10/2026 se documenta por separado para preparar APF3.

Repositorio público: https://github.com/roykevinh9-boop/culturaaccesible-lima

Tablero privado: https://trello.com/b/ykyaVYXr/culturaaccesible-lima-semana-10

El tablero requiere acceso de su titular. Las contraseñas y los datos locales de MySQL se mantienen fuera del código publicado.
