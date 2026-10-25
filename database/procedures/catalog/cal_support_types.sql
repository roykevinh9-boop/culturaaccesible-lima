-- Ejecutar sobre el esquema de la aplicacion; no elimina registros.
DROP PROCEDURE IF EXISTS cal_support_types;
DELIMITER $$
CREATE PROCEDURE cal_support_types()
SQL SECURITY INVOKER
READS SQL DATA
BEGIN
  SELECT codigo AS code, nombre AS label FROM tipos_apoyo ORDER BY id;
END$$
DELIMITER ;
