-- CulturaAccesible Lima. Ejecutar en una base NUEVA y vacía.
-- MySQL 8.0.16+; sin DROP DATABASE ni modificaciones a otras bases.
CREATE TABLE IF NOT EXISTS categorias (
 id BIGINT PRIMARY KEY AUTO_INCREMENT,
 nombre VARCHAR(60) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS distritos (
 id BIGINT PRIMARY KEY AUTO_INCREMENT,
 nombre VARCHAR(80) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS recintos (
 id BIGINT PRIMARY KEY AUTO_INCREMENT,
 nombre VARCHAR(160) NOT NULL, distrito_id BIGINT NOT NULL, direccion VARCHAR(200) NOT NULL,
 CONSTRAINT fk_recintos_distrito FOREIGN KEY(distrito_id) REFERENCES distritos(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS eventos (
 id BIGINT PRIMARY KEY AUTO_INCREMENT,
 nombre VARCHAR(180) NOT NULL, descripcion TEXT NOT NULL, categoria_id BIGINT NOT NULL,
 es_demo INT NOT NULL DEFAULT 1 CHECK (es_demo IN (0,1)),
 fuente_id VARCHAR(220) NULL UNIQUE, imagen_url VARCHAR(1200) NULL,
 imagen_alt VARCHAR(350) NULL, imagen_credito VARCHAR(180) NULL,
 CONSTRAINT fk_eventos_categoria FOREIGN KEY(categoria_id) REFERENCES categorias(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS funciones (
 id BIGINT PRIMARY KEY AUTO_INCREMENT, evento_id BIGINT NOT NULL, recinto_id BIGINT NOT NULL,
 fecha DATE NOT NULL, hora TIME NULL, precio_oficial DECIMAL(10,2) NULL,
 url_oficial VARCHAR(600) NULL, fuente_id VARCHAR(220) NULL UNIQUE,
 precio_desde INT NOT NULL DEFAULT 0 CHECK(precio_desde IN(0,1)), consultado_en DATE NULL,
 CONSTRAINT fk_funcion_evento FOREIGN KEY(evento_id) REFERENCES eventos(id),
 CONSTRAINT fk_funcion_recinto FOREIGN KEY(recinto_id) REFERENCES recintos(id),
 CONSTRAINT ck_precio CHECK(precio_oficial IS NULL OR precio_oficial>=0),
 INDEX idx_funcion_fecha(fecha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS tipos_apoyo (
 id BIGINT PRIMARY KEY AUTO_INCREMENT, codigo VARCHAR(40) NOT NULL UNIQUE, nombre VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS evidencias (
 id BIGINT PRIMARY KEY AUTO_INCREMENT, fuente VARCHAR(200) NOT NULL,
 url VARCHAR(600) NULL, fecha_revision DATE NOT NULL, valida_hasta DATE NULL,
 es_demo INT NOT NULL DEFAULT 1 CHECK(es_demo IN(0,1))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS condiciones (
 id BIGINT PRIMARY KEY AUTO_INCREMENT, tipo_apoyo_id BIGINT NOT NULL,
 alcance VARCHAR(15) NOT NULL, recinto_id BIGINT NULL, funcion_id BIGINT NULL,
 estado VARCHAR(20) NOT NULL DEFAULT 'NO_CONFIRMADO', evidencia_id BIGINT NULL,
 observacion VARCHAR(800) NOT NULL DEFAULT '',
 CONSTRAINT fk_condicion_tipo FOREIGN KEY(tipo_apoyo_id) REFERENCES tipos_apoyo(id),
 CONSTRAINT fk_condicion_recinto FOREIGN KEY(recinto_id) REFERENCES recintos(id),
 CONSTRAINT fk_condicion_funcion FOREIGN KEY(funcion_id) REFERENCES funciones(id),
 CONSTRAINT fk_condicion_evidencia FOREIGN KEY(evidencia_id) REFERENCES evidencias(id),
 CONSTRAINT ck_condicion_estado CHECK(estado IN('DISPONIBLE','NO_DISPONIBLE','NO_CONFIRMADO')),
 CONSTRAINT ck_condicion_alcance CHECK((alcance='RECINTO' AND recinto_id IS NOT NULL AND funcion_id IS NULL) OR (alcance='FUNCION' AND funcion_id IS NOT NULL AND recinto_id IS NULL)),
 CONSTRAINT uq_condicion_funcion UNIQUE(funcion_id,tipo_apoyo_id),
 CONSTRAINT uq_condicion_recinto UNIQUE(recinto_id,tipo_apoyo_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS reportes (
 id BIGINT PRIMARY KEY AUTO_INCREMENT, funcion_id BIGINT NOT NULL, condicion_id BIGINT NULL,
 comentario VARCHAR(1000) NOT NULL, estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE',
 creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
 CONSTRAINT fk_reporte_funcion FOREIGN KEY(funcion_id) REFERENCES funciones(id),
 CONSTRAINT fk_reporte_condicion FOREIGN KEY(condicion_id) REFERENCES condiciones(id),
 CONSTRAINT ck_reporte_estado CHECK(estado IN('PENDIENTE','EN_REVISION','RESUELTO'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
