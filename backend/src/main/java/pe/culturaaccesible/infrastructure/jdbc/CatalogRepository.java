package pe.culturaaccesible.infrastructure.jdbc;

import pe.culturaaccesible.catalog.port.CatalogStore;
import org.springframework.dao.DataAccessException;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;
import java.sql.SQLException;
import java.util.*;

/** Adaptador JDBC: solo invoca procedimientos; las consultas viven en database/procedures. */
@Repository
public class CatalogRepository implements CatalogStore {
    private final JdbcTemplate db;
    public CatalogRepository(JdbcTemplate db) { this.db = db; }

    public List<Map<String,Object>> functions() {
        return db.queryForList("CALL cal_list_functions()");
    }

    public List<Map<String,Object>> conditions(long functionId) {
        return db.queryForList("CALL cal_function_conditions(?)", functionId);
    }

    public List<Map<String,Object>> supportTypes() {
        return db.queryForList("CALL cal_support_types()");
    }

    public long createReport(long functionId, Long conditionId, String comment) {
        try {
            return Objects.requireNonNull(db.queryForObject(
                "CALL cal_create_report(?,?,?)", Long.class, functionId, conditionId, comment));
        } catch (DataAccessException error) {
            // MySQL SIGNAL 45000 representa una entrada rechazada, no una caída del servidor.
            if (error.getMostSpecificCause() instanceof SQLException sql && "45000".equals(sql.getSQLState())) {
                throw new IllegalArgumentException(sql.getMessage(), error);
            }
            throw error;
        }
    }

    public boolean healthy() {
        return Objects.equals(db.queryForObject("CALL cal_health()", Integer.class), 1);
    }
}
