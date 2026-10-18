# Tu proyecto CulturaAccesible Lima

Abre **http://127.0.0.1:8080/** y pulsa **Habla con AccesI**.

## Qué hace cada parte

| Parte | Para qué sirve | Dónde la editas |
|---|---|---|
| Página | Muestra fotos, filtros, fichas y el chat | `frontend/index.html`, `frontend/styles.css` |
| Java | Recibe las búsquedas, consulta MySQL y se comunica con Python | `backend/src/main/java/pe/culturaaccesible/` |
| Python | Reconoce intenciones de AccesI, aplica fechas/precios y ejecuta la demostración de precios | `python-service/assistant.py`, `python-service/main.py`, `python-service/model.py` |
| MySQL | Guarda funciones, recintos, apoyos, fuentes y reportes | `database/` |

Cuando escribes «eventos baratos en noviembre», el recorrido es:

**Página → Java → MySQL → Java → Python → respuesta en el chat.**

Java obtiene los eventos y apoyos de la base. Python interpreta la consulta y selecciona funciones reales de ese conjunto. El chat no inventa eventos ni ejecuta consultas SQL escritas por quien conversa.

## Prueba AccesI

1. `hola`: saluda y explica cómo buscar.
2. `eventos en noviembre`: muestra funciones del mes.
3. `y los más baratos`: conserva noviembre y ordena por precio publicado.
4. `los más caros el 18 de octubre`: cambia al día exacto.
5. `hasta 20 soles en octubre`: aplica un presupuesto.
6. `con LSP`: exige un apoyo confirmado; puede responder que no hay coincidencias.

**Nueva conversación** limpia los criterios. El selector del chat separa la cartelera cultural de los ejemplos ficticios. Las conversaciones no se guardan en MySQL ni se envían a un proveedor externo.

La IA es **local**: TF-IDF y regresión logística clasifican intenciones; un motor de reglas aplica los filtros y construye respuestas basadas en los datos. No es ChatGPT ni un modelo generativo. No necesita una clave API. El modelo de precios del curso es otra función y usa datos sintéticos; el chatbot no usa sus predicciones para afirmar precios oficiales.

## Tu conexión MySQL

- Servidor: `127.0.0.1` (esta PC).
- Puerto: `3307`.
- Base: `culturaaccesible`.
- Usuario de la aplicación: `cal_app`.
- Datos: `.local/mysql-data`.
- Credenciales privadas: `.local/runtime.json`; no compartirlo.

La conexión de la web con este servidor está comprobada. Workbench ya tiene guardada la conexión CulturaAccesible Lima. El 18/10/2026 se comprobó visualmente el puerto 3307, el usuario cal_app y la base culturaaccesible, además de las siete tablas y las 57 funciones. Si vuelve a pedir la contraseña, introdúcela desde el archivo local. `database/03_consultas.sql` contiene consultas para revisar las 49 funciones de cartelera y los ocho ejemplos.

## Iniciar, detener y editar

- Ejecuta `Abrir-demo.cmd` para iniciar Java, Python y MySQL.
- Mantén abierta su ventana mientras uses la página. Ctrl+C detiene los componentes.
- En VS Code abre `CulturaAccesibleLima.code-workspace`. Las tareas permiten iniciar, compilar y probar.
- Si cambias Java, HTML, CSS o JavaScript, detén la aplicación y ejecuta `scripts/Compilar.ps1`; después vuelve a iniciar.
- Si cambias Python, reinicia la aplicación.
- Los nuevos terminales de este proyecto utilizan CMD para evitar el aviso de PSReadLine. El terminal PowerShell que ya estaba abierto conserva su estado; abre uno nuevo con el botón +.

## Límites que debes explicar en la exposición

La cartelera es una instantánea recuperada el **17/10/2026**. Las imágenes y enlaces necesitan Internet. «Desde» indica la tarifa mínima publicada y no el precio de todas las entradas. Un apoyo sin evidencia suficiente se presenta como **No confirmado**. No se venden ni reservan entradas.
