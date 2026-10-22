-- Permisos de ejecucion para la cuenta local existente de la aplicacion.
-- Ejecutar como administrador de la base; no concede CREATE ROUTINE ni administracion.
GRANT EXECUTE ON PROCEDURE culturaaccesible.cal_list_functions TO 'cal_app'@'127.0.0.1';
GRANT EXECUTE ON PROCEDURE culturaaccesible.cal_function_conditions TO 'cal_app'@'127.0.0.1';
GRANT EXECUTE ON PROCEDURE culturaaccesible.cal_support_types TO 'cal_app'@'127.0.0.1';
GRANT EXECUTE ON PROCEDURE culturaaccesible.cal_health TO 'cal_app'@'127.0.0.1';
GRANT EXECUTE ON PROCEDURE culturaaccesible.cal_create_report TO 'cal_app'@'127.0.0.1';
