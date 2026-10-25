-- Ejecutar sobre el esquema de la aplicacion; no elimina registros.
DROP PROCEDURE IF EXISTS cal_health;
DELIMITER $$
CREATE PROCEDURE cal_health()
SQL SECURITY INVOKER
NO SQL
BEGIN
  SELECT 1 AS ok;
END$$
DELIMITER ;
