package pe.culturaaccesible.infrastructure.jdbc;

import java.sql.Types;
import org.springframework.jdbc.core.SqlParameter;

/** Contratos de entrada de las rutinas; sus sentencias están en database/procedures. */
enum CatalogProcedure {
    LIST_FUNCTIONS("cal_list_functions"),
    FUNCTION_CONDITIONS("cal_function_conditions", new SqlParameter("p_function_id", Types.BIGINT)),
    SUPPORT_TYPES("cal_support_types"),
    HEALTH("cal_health"),
    CREATE_REPORT("cal_create_report",
        new SqlParameter("p_function_id", Types.BIGINT),
        new SqlParameter("p_condition_id", Types.BIGINT),
        new SqlParameter("p_comment", Types.LONGVARCHAR));

    private final String routineName;
    private final SqlParameter[] parameters;

    CatalogProcedure(String routineName, SqlParameter... parameters) {
        this.routineName = routineName;
        this.parameters = parameters.clone();
    }

    String routineName() { return routineName; }
    SqlParameter[] parameters() { return parameters.clone(); }
}
