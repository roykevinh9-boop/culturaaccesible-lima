-- Consultas para ejecutar en Workbench sobre la conexión local 127.0.0.1:3307.
USE culturaaccesible;

SELECT e.es_demo, COUNT(*) AS funciones
FROM funciones f JOIN eventos e ON e.id=f.evento_id
GROUP BY e.es_demo;

SELECT f.id,e.nombre,r.nombre AS recinto,r.distrito,f.fecha,f.hora,
       f.precio_oficial,f.precio_desde,f.url_oficial,e.imagen_url
FROM funciones f
JOIN eventos e ON e.id=f.evento_id
JOIN recintos r ON r.id=f.recinto_id
WHERE e.es_demo=0
ORDER BY f.fecha,f.hora,f.id;

SELECT id,funcion_id,estado,comentario FROM reportes ORDER BY id DESC;
