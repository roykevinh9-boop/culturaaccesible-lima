package pe.culturaaccesible.infraestructura.jdbc;

import pe.culturaaccesible.modelo.puertos.CatalogStore;
import org.springframework.dao.DataAccessException;
import org.springframework.dao.DataRetrievalFailureException;
import org.springframework.stereotype.Repository;
import java.sql.SQLException;
import java.util.*;

/** Adaptador de CatalogStore: transforma parámetros y resultados de procedimientos. */
@Repository
public class CatalogRepository implements CatalogStore {
    private final StoredProcedureExecutor procedures;
    public CatalogRepository(StoredProcedureExecutor procedures) { this.procedures = procedures; }

    public List<Map<String,Object>> functions() {
        return procedures.execute(CatalogProcedure.LIST_FUNCTIONS, Map.of());
    }

    public List<Map<String,Object>> conditions(long functionId) {
        return procedures.execute(CatalogProcedure.FUNCTION_CONDITIONS, Map.of("p_function_id", functionId));
    }

    public List<Map<String,Object>> catalogConditions() {
        return procedures.execute(CatalogProcedure.CATALOG_CONDITIONS, Map.of());
    }

    public List<Map<String,Object>> supportTypes() {
        return procedures.execute(CatalogProcedure.SUPPORT_TYPES, Map.of());
    }

    public long createReport(long functionId, Long conditionId, String comment) {
        try {
            Map<String, Object> parameters = new LinkedHashMap<>();
            parameters.put("p_function_id", functionId);
            parameters.put("p_condition_id", conditionId);
            parameters.put("p_comment", comment);
            return scalar(CatalogProcedure.CREATE_REPORT, parameters, "id").longValue();
        } catch (DataAccessException error) {
            // MySQL SIGNAL 45000 representa una entrada rechazada, no una caída del servidor.
            if (error.getMostSpecificCause() instanceof SQLException sql && "45000".equals(sql.getSQLState())) {
                throw new IllegalArgumentException(sql.getMessage(), error);
            }
            throw error;
        }
    }

    public boolean healthy() {
        return scalar(CatalogProcedure.HEALTH, Map.of(), "ok").intValue() == 1;
    }

    private Number scalar(CatalogProcedure procedure, Map<String, ?> parameters, String column) {
        List<Map<String, Object>> rows = procedures.execute(procedure, parameters);
        if (rows.size() != 1 || !(rows.get(0).get(column) instanceof Number value)) {
            throw new DataRetrievalFailureException("Respuesta inesperada de la rutina " + procedure.routineName() + ".");
        }
        return value;
    }
}
