package pe.culturaaccesible.infraestructura.jdbc;

import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import org.springframework.dao.DataRetrievalFailureException;
import org.springframework.jdbc.core.ColumnMapRowMapper;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.simple.SimpleJdbcCall;
import org.springframework.stereotype.Component;

/** Configura invocaciones parametrizadas, sin sentencias de consulta en el código Java. */
@Component
public class StoredProcedureExecutor {
    private static final String ROWS = "rows";
    private final Map<CatalogProcedure, SimpleJdbcCall> routines = new EnumMap<>(CatalogProcedure.class);

    public StoredProcedureExecutor(JdbcTemplate jdbc) {
        for (CatalogProcedure procedure : CatalogProcedure.values()) {
            routines.put(procedure, new SimpleJdbcCall(jdbc)
                .withProcedureName(procedure.routineName())
                .withoutProcedureColumnMetaDataAccess()
                .declareParameters(procedure.parameters())
                .returningResultSet(ROWS, new ColumnMapRowMapper()));
        }
    }

    @SuppressWarnings("unchecked")
    public List<Map<String, Object>> execute(CatalogProcedure procedure, Map<String, ?> parameters) {
        Object result = routines.get(procedure).execute(new MapSqlParameterSource(parameters)).get(ROWS);
        if (!(result instanceof List<?> rows)) {
            throw new DataRetrievalFailureException("La rutina " + procedure.routineName() + " no devolvió resultados.");
        }
        return (List<Map<String, Object>>) rows;
    }
}
