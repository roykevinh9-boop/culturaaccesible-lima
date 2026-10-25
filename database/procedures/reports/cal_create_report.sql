-- Ejecutar sobre el esquema de la aplicacion; no elimina registros.
DROP PROCEDURE IF EXISTS cal_create_report;
DELIMITER $$
CREATE PROCEDURE cal_create_report(IN p_function_id BIGINT, IN p_condition_id BIGINT, IN p_comment TEXT)
SQL SECURITY INVOKER
MODIFIES SQL DATA
BEGIN
  IF p_comment IS NULL OR CHAR_LENGTH(TRIM(p_comment)) < 10 OR CHAR_LENGTH(TRIM(p_comment)) > 1000 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Escribe entre 10 y 1000 caracteres.';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM funciones WHERE id=p_function_id) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La funcion no existe.';
  END IF;
  IF p_condition_id IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM condiciones c JOIN funciones f ON f.id=p_function_id
    WHERE c.id=p_condition_id AND (c.funcion_id=f.id OR c.recinto_id=f.recinto_id)
  ) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La condicion no pertenece a esta funcion.';
  END IF;
  INSERT INTO reportes (funcion_id,condicion_id,comentario,estado)
    VALUES (p_function_id,p_condition_id,TRIM(p_comment),'PENDIENTE');
  SELECT LAST_INSERT_ID() AS id;
END$$
DELIMITER ;
