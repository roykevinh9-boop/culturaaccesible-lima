-- Migración 1.3.0 para la base culturaaccesible existente. No elimina filas.
-- Antes de ejecutarla manualmente, hacer un respaldo. El inicio automático lo guarda en .local/backups/.
-- DDL de MySQL confirma por sentencia: ejecutar el archivo completo y no interrumpirlo.
-- Se puede repetir: inspecciona columnas y claves antes de modificarlas.
USE culturaaccesible;

CREATE TABLE IF NOT EXISTS categorias (
 id BIGINT PRIMARY KEY AUTO_INCREMENT,
 nombre VARCHAR(60) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS distritos (
 id BIGINT PRIMARY KEY AUTO_INCREMENT,
 nombre VARCHAR(80) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET @cal_sql = IF((SELECT COUNT(*) FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='eventos' AND column_name='categoria'), 'INSERT IGNORE INTO categorias(nombre) SELECT DISTINCT categoria FROM eventos ORDER BY categoria', 'SELECT 1');
PREPARE cal_stmt FROM @cal_sql;
EXECUTE cal_stmt;
DEALLOCATE PREPARE cal_stmt;

SET @cal_sql = IF((SELECT COUNT(*)=0 FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='eventos' AND column_name='categoria_id'), 'ALTER TABLE eventos ADD COLUMN categoria_id BIGINT NULL', 'SELECT 1');
PREPARE cal_stmt FROM @cal_sql;
EXECUTE cal_stmt;
DEALLOCATE PREPARE cal_stmt;

SET @cal_sql = IF((SELECT COUNT(*) FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='eventos' AND column_name='categoria'), 'UPDATE eventos t JOIN categorias d ON d.nombre=t.categoria SET t.categoria_id=d.id', 'SELECT 1');
PREPARE cal_stmt FROM @cal_sql;
EXECUTE cal_stmt;
DEALLOCATE PREPARE cal_stmt;

ALTER TABLE eventos MODIFY categoria_id BIGINT NOT NULL;

SET @cal_sql = IF((SELECT COUNT(*)=0 FROM information_schema.table_constraints WHERE constraint_schema=DATABASE() AND table_name='eventos' AND constraint_name='fk_eventos_categoria'), 'ALTER TABLE eventos ADD CONSTRAINT fk_eventos_categoria FOREIGN KEY (categoria_id) REFERENCES categorias(id)', 'SELECT 1');
PREPARE cal_stmt FROM @cal_sql;
EXECUTE cal_stmt;
DEALLOCATE PREPARE cal_stmt;

SET @cal_sql = IF((SELECT COUNT(*) FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='eventos' AND column_name='categoria'), 'ALTER TABLE eventos DROP COLUMN categoria', 'SELECT 1');
PREPARE cal_stmt FROM @cal_sql;
EXECUTE cal_stmt;
DEALLOCATE PREPARE cal_stmt;

SET @cal_sql = IF((SELECT COUNT(*) FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='recintos' AND column_name='distrito'), 'INSERT IGNORE INTO distritos(nombre) SELECT DISTINCT distrito FROM recintos ORDER BY distrito', 'SELECT 1');
PREPARE cal_stmt FROM @cal_sql;
EXECUTE cal_stmt;
DEALLOCATE PREPARE cal_stmt;

SET @cal_sql = IF((SELECT COUNT(*)=0 FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='recintos' AND column_name='distrito_id'), 'ALTER TABLE recintos ADD COLUMN distrito_id BIGINT NULL', 'SELECT 1');
PREPARE cal_stmt FROM @cal_sql;
EXECUTE cal_stmt;
DEALLOCATE PREPARE cal_stmt;

SET @cal_sql = IF((SELECT COUNT(*) FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='recintos' AND column_name='distrito'), 'UPDATE recintos t JOIN distritos d ON d.nombre=t.distrito SET t.distrito_id=d.id', 'SELECT 1');
PREPARE cal_stmt FROM @cal_sql;
EXECUTE cal_stmt;
DEALLOCATE PREPARE cal_stmt;

ALTER TABLE recintos MODIFY distrito_id BIGINT NOT NULL;

SET @cal_sql = IF((SELECT COUNT(*)=0 FROM information_schema.table_constraints WHERE constraint_schema=DATABASE() AND table_name='recintos' AND constraint_name='fk_recintos_distrito'), 'ALTER TABLE recintos ADD CONSTRAINT fk_recintos_distrito FOREIGN KEY (distrito_id) REFERENCES distritos(id)', 'SELECT 1');
PREPARE cal_stmt FROM @cal_sql;
EXECUTE cal_stmt;
DEALLOCATE PREPARE cal_stmt;

SET @cal_sql = IF((SELECT COUNT(*) FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='recintos' AND column_name='distrito'), 'ALTER TABLE recintos DROP COLUMN distrito', 'SELECT 1');
PREPARE cal_stmt FROM @cal_sql;
EXECUTE cal_stmt;
DEALLOCATE PREPARE cal_stmt;
