package pe.culturaaccesible.modelo.puertos;

import java.util.List;
import java.util.Map;

/** Puerto de persistencia del catálogo. No depende de JDBC, HTTP ni MySQL. */
public interface CatalogStore {
    List<Map<String,Object>> functions();
    List<Map<String,Object>> conditions(long functionId);
    List<Map<String,Object>> supportTypes();
    long createReport(long functionId, Long conditionId, String comment);
    boolean healthy();
}
