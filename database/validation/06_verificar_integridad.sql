-- Consultas de diagnóstico; no modifican las tablas ni los registros.
USE culturaaccesible;

SELECT 'eventos' AS entidad, COUNT(*) AS registros FROM eventos
UNION ALL SELECT 'funciones', COUNT(*) FROM funciones
UNION ALL SELECT 'categorias', COUNT(*) FROM categorias
UNION ALL SELECT 'distritos', COUNT(*) FROM distritos;

-- Ambos resultados deben ser cero si la integridad referencial está intacta.
SELECT COUNT(*) AS eventos_sin_categoria
FROM eventos e LEFT JOIN categorias c ON c.id=e.categoria_id
WHERE c.id IS NULL;

SELECT COUNT(*) AS recintos_sin_distrito
FROM recintos r LEFT JOIN distritos d ON d.id=r.distrito_id
WHERE d.id IS NULL;
