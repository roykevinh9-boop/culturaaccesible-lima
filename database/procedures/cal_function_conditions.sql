-- Ejecutar sobre el esquema de la aplicacion; no elimina registros.
DROP PROCEDURE IF EXISTS cal_function_conditions;
DELIMITER $$
CREATE PROCEDURE cal_function_conditions(IN p_function_id BIGINT)
SQL SECURITY INVOKER
READS SQL DATA
BEGIN
  SELECT c.id, t.codigo AS code, t.nombre AS label, c.estado AS state,
                 c.alcance AS scope, c.observacion AS note,
                 ev.fuente AS source, ev.url AS source_url, ev.fecha_revision AS reviewed_at,
                 ev.valida_hasta AS valid_until
          FROM condiciones c JOIN tipos_apoyo t ON t.id=c.tipo_apoyo_id
          JOIN funciones f ON f.id=p_function_id
          LEFT JOIN evidencias ev ON ev.id=c.evidencia_id
          WHERE c.funcion_id=f.id OR (c.recinto_id=f.recinto_id AND c.alcance='RECINTO')
          ORDER BY t.id, CASE WHEN c.alcance='FUNCION' THEN 0 ELSE 1 END, c.id;
END$$
DELIMITER ;
