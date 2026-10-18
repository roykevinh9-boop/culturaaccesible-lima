-- Consultas para ejecutar en Workbench sobre la conexión local 127.0.0.1:3307.
USE culturaaccesible;

SELECT e.es_demo, COUNT(*) AS funciones
FROM funciones f JOIN eventos e ON e.id=f.evento_id
GROUP BY e.es_demo;

SELECT f.id,e.nombre,r.nombre AS recinto,d.nombre AS distrito,cat.nombre AS categoria,f.fecha,f.hora,
       f.precio_oficial,f.precio_desde,f.url_oficial,e.imagen_url
FROM funciones f
JOIN eventos e ON e.id=f.evento_id
JOIN recintos r ON r.id=f.recinto_id
JOIN categorias cat ON cat.id=e.categoria_id
JOIN distritos d ON d.id=r.distrito_id
WHERE e.es_demo=0
ORDER BY f.fecha,f.hora,f.id;

SELECT id,funcion_id,estado,comentario FROM reportes ORDER BY id DESC;

-- Catálogos compartidos y cantidad de referencias.
SELECT c.id,c.nombre,COUNT(e.id) AS eventos FROM categorias c LEFT JOIN eventos e ON e.categoria_id=c.id GROUP BY c.id,c.nombre;
SELECT d.id,d.nombre,COUNT(r.id) AS recintos FROM distritos d LEFT JOIN recintos r ON r.distrito_id=d.id GROUP BY d.id,d.nombre;
