package pe.culturaaccesible.vista;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class ApiViewTest {
    private final ObjectMapper json = new ObjectMapper();

    @Test void preservesTheCatalogJsonContractAndSeparatesDemo() throws Exception {
        var response = ApiView.catalog(List.of(Map.of("id", 12L)), "official");
        var value = json.readTree(json.writeValueAsString(response));
        assertEquals(5, value.size());
        assertEquals(12L, value.get("items").get(0).get("id").longValue());
        assertEquals(1, value.get("total").intValue());
        assertFalse(value.get("demo").booleanValue());
        assertEquals("official", value.get("source").textValue());
        assertEquals("2026-10-17", value.get("consulted_at").textValue());
        assertTrue(ApiView.catalog(List.of(), "demo").demo());
    }

    @Test void keepsTheDisplayedTotalConsistentIfTheSourceListChanges() {
        var items = new ArrayList<Map<String, Object>>();
        items.add(Map.of("id", 1L));
        var response = ApiView.catalog(items, "official");
        items.clear();
        assertEquals(response.total(), response.items().size());
        assertEquals(1, response.total());
        assertThrows(UnsupportedOperationException.class, () -> response.items().clear());
    }

    @Test void preservesHealthAndErrorResponsesWithoutConfirmingAFailure() throws Exception {
        var health = json.readTree(json.writeValueAsString(ApiView.health(false)));
        assertEquals("error", health.get("status").textValue());
        assertEquals("mysql", health.get("database").textValue());
        assertEquals("CulturaAccesible Lima", health.get("application").textValue());
        var failure = json.readTree(json.writeValueAsString(ApiView.message("No se confirmó el guardado.")));
        assertEquals(1, failure.size());
        assertFalse(failure.has("id"));
        assertEquals("No se confirmó el guardado.", failure.get("message").textValue());
    }
}
