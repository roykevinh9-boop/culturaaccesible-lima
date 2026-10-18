package pe.culturaaccesible.catalog;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;
import java.util.*;

/** Persistencia JDBC. Las consultas son parametrizadas y no dependen de la vista. */
@Repository
public class CatalogRepository {
    private final JdbcTemplate db;
    public CatalogRepository(JdbcTemplate db) { this.db = db; }

    public List<Map<String,Object>> functions() {
        return db.queryForList("""
          SELECT f.id, e.nombre AS title, e.descripcion AS description, e.categoria AS category,
                 r.nombre AS venue, r.distrito AS district, r.direccion AS address,
                 f.fecha AS event_date, f.hora AS event_time, f.precio_oficial AS official_price,
                 f.url_oficial AS official_url, e.es_demo AS demo
          FROM funciones f JOIN eventos e ON e.id=f.evento_id JOIN recintos r ON r.id=f.recinto_id
          ORDER BY f.fecha, f.hora, f.id
          """);
    }

    public List<Map<String,Object>> conditions(long functionId) {
        return db.queryForList("""
          SELECT c.id, t.codigo AS code, t.nombre AS label, c.estado AS state,
                 c.alcance AS scope, c.observacion AS note,
                 ev.fuente AS source, ev.url AS source_url, ev.fecha_revision AS reviewed_at,
                 ev.valida_hasta AS valid_until
          FROM condiciones c JOIN tipos_apoyo t ON t.id=c.tipo_apoyo_id
          JOIN funciones f ON f.id=?
          LEFT JOIN evidencias ev ON ev.id=c.evidencia_id
          WHERE c.funcion_id=f.id OR (c.recinto_id=f.recinto_id AND c.alcance='RECINTO')
          ORDER BY t.id, CASE WHEN c.alcance='FUNCION' THEN 0 ELSE 1 END, c.id
          """, functionId);
    }

    public List<Map<String,Object>> supportTypes() {
        return db.queryForList("SELECT codigo AS code, nombre AS label FROM tipos_apoyo ORDER BY id");
    }

    public long createReport(long functionId, Long conditionId, String comment) {
        if (conditionId != null && db.queryForObject("""
             SELECT COUNT(*) FROM condiciones c JOIN funciones f ON f.id=?
             WHERE c.id=? AND (c.funcion_id=f.id OR c.recinto_id=f.recinto_id)
             """, Integer.class, functionId, conditionId) == 0) {
            throw new IllegalArgumentException("La condición no pertenece a esta función.");
        }
        var holder = new org.springframework.jdbc.support.GeneratedKeyHolder();
        db.update(connection -> {
            var stmt = connection.prepareStatement("INSERT INTO reportes (funcion_id,condicion_id,comentario,estado) VALUES (?,?,?,'PENDIENTE')", java.sql.Statement.RETURN_GENERATED_KEYS);
            stmt.setLong(1, functionId);
            if (conditionId == null) stmt.setNull(2, java.sql.Types.BIGINT); else stmt.setLong(2, conditionId);
            stmt.setString(3, comment);
            return stmt;
        }, holder);
        return Objects.requireNonNull(holder.getKey()).longValue();
    }

    public boolean healthy() {
        return Objects.equals(db.queryForObject("SELECT 1", Integer.class), 1);
    }
}
