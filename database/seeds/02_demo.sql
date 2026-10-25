-- Semilla para una base VACÍA. Todos los nombres, precios y apoyos son FICTICIOS.
-- Las fechas se calculan al cargar la semilla para facilitar la demostración.
INSERT IGNORE INTO categorias(nombre) VALUES ('Teatro'),('Museo'),('Música'),('Danza'),('Exposición');
INSERT IGNORE INTO distritos(nombre) VALUES ('Miraflores'),('Cercado de Lima'),('Barranco'),('San Borja');
INSERT INTO recintos(id,nombre,distrito_id,direccion) VALUES
 (1,'Teatro Horizonte · recinto ficticio',(SELECT id FROM distritos WHERE nombre='Miraflores'),'Dirección de demostración 101'),
 (2,'Museo Encuentro · recinto ficticio',(SELECT id FROM distritos WHERE nombre='Cercado de Lima'),'Dirección de demostración 202'),
 (3,'Casa de las Artes · recinto ficticio',(SELECT id FROM distritos WHERE nombre='Barranco'),'Dirección de demostración 303'),
 (4,'Sala Abierta · recinto ficticio',(SELECT id FROM distritos WHERE nombre='San Borja'),'Dirección de demostración 404')
 ON DUPLICATE KEY UPDATE id=recintos.id;
INSERT INTO eventos(id,nombre,descripcion,categoria_id,es_demo) VALUES
 (1,'Escena abierta con LSP','Una historia sobre la ciudad, presentada con interpretación en LSP y subtítulos. Escenario académico ficticio.',(SELECT id FROM categorias WHERE nombre='Teatro'),1),
 (2,'Museo para escuchar y tocar','Recorrido de demostración con narración y materiales táctiles. No corresponde a una visita real.',(SELECT id FROM categorias WHERE nombre='Museo'),1),
 (3,'Ritmos de nuestra ciudad','Presentación ficticia de música con información de acceso físico y apoyos pendientes de confirmar.',(SELECT id FROM categorias WHERE nombre='Música'),1),
 (4,'Danza en movimiento','Función ficticia de danza contemporánea. El precio todavía no está informado en el escenario.',(SELECT id FROM categorias WHERE nombre='Danza'),1),
 (5,'Colores que nos reúnen','Exposición ficticia de artes visuales de ingreso gratuito. Los estados permiten practicar la lectura de evidencia.',(SELECT id FROM categorias WHERE nombre='Exposición'),1),
 (6,'Historias del barrio','Segunda función teatral de demostración. La evidencia de LSP está vencida para probar su tratamiento.',(SELECT id FROM categorias WHERE nombre='Teatro'),1),
 (7,'Encuentro de voces','Actividad musical ficticia. Algunos apoyos cuentan con declaración negativa explícita.',(SELECT id FROM categorias WHERE nombre='Música'),1),
 (8,'Una ciudad para imaginar','Visita de museo ficticia sin precio publicado para demostrar la consulta a Python.',(SELECT id FROM categorias WHERE nombre='Museo'),1)
 ON DUPLICATE KEY UPDATE id=eventos.id;
INSERT INTO funciones(id,evento_id,recinto_id,fecha,hora,precio_oficial,url_oficial) VALUES
 (1,1,1,CURRENT_DATE,'19:00:00',35.00,NULL),
 (2,2,2,DATE_ADD(CURRENT_DATE,INTERVAL 1 DAY),'11:00:00',0.00,NULL),
 (3,3,3,DATE_ADD(CURRENT_DATE,INTERVAL 2 DAY),'20:00:00',65.00,NULL),
 (4,4,1,DATE_ADD(CURRENT_DATE,INTERVAL 3 DAY),'18:30:00',NULL,NULL),
 (5,5,4,DATE_ADD(CURRENT_DATE,INTERVAL 5 DAY),'10:00:00',0.00,NULL),
 (6,6,1,DATE_ADD(CURRENT_DATE,INTERVAL 7 DAY),'19:00:00',25.00,NULL),
 (7,7,4,DATE_ADD(CURRENT_DATE,INTERVAL 10 DAY),'18:00:00',45.00,NULL),
 (8,8,2,DATE_ADD(CURRENT_DATE,INTERVAL 12 DAY),'12:00:00',NULL,NULL)
 ON DUPLICATE KEY UPDATE id=funciones.id;
INSERT INTO tipos_apoyo(id,codigo,nombre) VALUES
 (1,'silla_ruedas','Espacio para silla de ruedas'),(2,'sin_escalones','Ingreso sin escalones'),
 (3,'bano_adaptado','Baño adaptado'),(4,'lsp','Interpretación en LSP'),
 (5,'subtitulos','Subtítulos'),(6,'audiodescripcion','Audiodescripción'),(7,'tactil','Material o recorrido táctil')
 ON DUPLICATE KEY UPDATE id=tipos_apoyo.id;
INSERT INTO evidencias(id,fuente,url,fecha_revision,valida_hasta,es_demo) VALUES
 (1,'Ficha simulada por el equipo: evidencia ficticia',NULL,CURRENT_DATE,DATE_ADD(CURRENT_DATE,INTERVAL 30 DAY),1),
 (2,'Ficha simulada vencida: no acredita disponibilidad actual',NULL,DATE_SUB(CURRENT_DATE,INTERVAL 35 DAY),DATE_SUB(CURRENT_DATE,INTERVAL 1 DAY),1)
 ON DUPLICATE KEY UPDATE id=evidencias.id;
INSERT INTO condiciones(tipo_apoyo_id,alcance,recinto_id,funcion_id,estado,evidencia_id,observacion) VALUES
 (1,'RECINTO',1,NULL,'DISPONIBLE',1,'Declaración simulada del recinto. El cupo de cada función requiere coordinación.'),
 (2,'RECINTO',1,NULL,'DISPONIBLE',1,'Rampa y trayecto simulados para el escenario académico.'),
 (3,'RECINTO',1,NULL,'DISPONIBLE',1,'Baño adaptado ficticio declarado por el recinto.'),
 (1,'RECINTO',2,NULL,'DISPONIBLE',1,'Espacio de demostración disponible.'),
 (2,'RECINTO',2,NULL,'DISPONIBLE',1,'Ingreso de demostración sin escalones.'),
 (3,'RECINTO',2,NULL,'DISPONIBLE',1,'Condición ficticia para la prueba del filtro.'),
 (2,'RECINTO',3,NULL,'NO_DISPONIBLE',1,'El escenario de prueba incluye un acceso con escalones.'),
 (3,'RECINTO',3,NULL,'NO_CONFIRMADO',NULL,'No se ha documentado esta condición.'),
 (1,'RECINTO',4,NULL,'DISPONIBLE',1,'Espacios simulados; no representan cupos reales.'),
 (2,'RECINTO',4,NULL,'DISPONIBLE',1,'Ruta interna simulada para la demostración.'),
 (4,'FUNCION',NULL,1,'DISPONIBLE',1,'Intérprete ficticio asignado únicamente a esta función.'),
 (5,'FUNCION',NULL,1,'DISPONIBLE',1,'Subtítulos simulados para esta fecha.'),
 (6,'FUNCION',NULL,1,'NO_DISPONIBLE',1,'Ausencia explícita simulada; no se deduce de datos faltantes.'),
 (6,'FUNCION',NULL,2,'DISPONIBLE',1,'Narración de demostración para el recorrido.'),
 (7,'FUNCION',NULL,2,'DISPONIBLE',1,'Materiales táctiles ficticios para esta sesión.'),
 (4,'FUNCION',NULL,3,'NO_CONFIRMADO',NULL,'No existe evidencia para confirmar LSP.'),
 (4,'FUNCION',NULL,6,'DISPONIBLE',2,'La declaración está vencida y la aplicación debe mostrar No confirmado.'),
 (5,'FUNCION',NULL,7,'NO_DISPONIBLE',1,'El escenario declara expresamente que no habrá subtítulos.'),
 (6,'FUNCION',NULL,8,'DISPONIBLE',1,'Audiodescripción ficticia prevista para esta sesión.')
 ON DUPLICATE KEY UPDATE id=condiciones.id;
