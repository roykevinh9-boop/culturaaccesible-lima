-- Ejecutar sobre el esquema de la aplicacion; no elimina registros.
DROP PROCEDURE IF EXISTS cal_list_functions;
DELIMITER $$
CREATE PROCEDURE cal_list_functions()
SQL SECURITY INVOKER
READS SQL DATA
BEGIN
  SELECT f.id, e.nombre AS title, e.descripcion AS description, cat.nombre AS category,
                 r.nombre AS venue, d.nombre AS district, r.direccion AS address,
                 f.fecha AS event_date, f.hora AS event_time, f.precio_oficial AS official_price,
                 f.url_oficial AS official_url, e.es_demo AS demo,
                 e.imagen_url AS image_url, e.imagen_alt AS image_alt, e.imagen_credito AS image_credit,
                 f.precio_desde AS price_from, f.consultado_en AS consulted_at
          FROM funciones f JOIN eventos e ON e.id=f.evento_id JOIN recintos r ON r.id=f.recinto_id
          JOIN categorias cat ON cat.id=e.categoria_id JOIN distritos d ON d.id=r.distrito_id
          ORDER BY f.fecha, f.hora, f.id;
END$$
DELIMITER ;
