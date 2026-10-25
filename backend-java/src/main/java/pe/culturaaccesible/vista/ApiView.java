package pe.culturaaccesible.vista;

import java.util.List;
import java.util.Map;

/** Representaciones JSON de la API. Las pantallas HTML viven en frontend/views. */
public final class ApiView {
    private ApiView() {}

    public record CatalogResponse(List<Map<String, Object>> items, int total,
                                  boolean demo, String source, String consulted_at) {}
    public record HealthResponse(String status, String database, String application) {}
    public record MessageResponse(String message) {}
    public record ValidationResponse(String message, Map<String,String> fields) {}

    public static CatalogResponse catalog(List<Map<String, Object>> items, String source) {
        List<Map<String, Object>> snapshot = List.copyOf(items);
        return new CatalogResponse(snapshot, snapshot.size(), "demo".equals(source), source, "2026-10-17");
    }

    public static HealthResponse health(boolean healthy) {
        return new HealthResponse(healthy ? "ok" : "error", "mysql", "CulturaAccesible Lima");
    }

    public static MessageResponse message(String text) {
        return new MessageResponse(text);
    }
}
