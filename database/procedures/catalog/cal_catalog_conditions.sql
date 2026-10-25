-- Recupera las condiciones del catalogo en una sola llamada, sin modificar datos.
DROP PROCEDURE IF EXISTS cal_catalog_conditions;
DELIMITER $$
CREATE PROCEDURE cal_catalog_conditions()
SQL SECURITY INVOKER
READS SQL DATA
BEGIN
  SELECT f.id AS function_id, c.id, t.codigo AS code, t.nombre AS label,
         c.estado AS state, c.alcance AS scope, c.observacion AS note,
         ev.fuente AS source, ev.url AS source_url,
         ev.fecha_revision AS reviewed_at, ev.valida_hasta AS valid_until
    FROM funciones f
    JOIN condiciones c ON c.funcion_id=f.id
      OR (c.recinto_id=f.recinto_id AND c.alcance='RECINTO')
    JOIN tipos_apoyo t ON t.id=c.tipo_apoyo_id
    LEFT JOIN evidencias ev ON ev.id=c.evidencia_id
   ORDER BY f.id, t.id, CASE WHEN c.alcance='FUNCION' THEN 0 ELSE 1 END, c.id;
END$$
DELIMITER ;
