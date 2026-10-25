package pe.culturaaccesible.controlador;

import org.junit.jupiter.api.Test;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import pe.culturaaccesible.modelo.catalogo.CatalogService;
import pe.culturaaccesible.modelo.puertos.CatalogStore;
import pe.culturaaccesible.modelo.chat.ChatService;
import pe.culturaaccesible.modelo.precios.PricingService;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

class ApiValidationTest {
    @Test void identifiesTheInvalidCommentWithoutCallingTheService() throws Exception {
        var catalog=mock(CatalogService.class);
        var mvc=MockMvcBuilders.standaloneSetup(new ApiController(catalog,mock(CatalogStore.class),mock(PricingService.class),mock(ChatService.class)))
            .setControllerAdvice(new ApiErrors()).build();
        mvc.perform(post("/api/reports").contentType("application/json").content("{\"function_id\":1,\"comment\":\"corto\"}"))
            .andExpect(status().isBadRequest()).andExpect(jsonPath("$.fields.comment").value("Escribe entre 10 y 1000 caracteres."))
            .andExpect(jsonPath("$.id").doesNotExist());
        verifyNoInteractions(catalog);
    }
    @Test void identifiesAnInvalidMonthInSpanish() throws Exception {
        var pricing=mock(PricingService.class);
        var mvc=MockMvcBuilders.standaloneSetup(new ApiController(mock(CatalogService.class),mock(CatalogStore.class),pricing,mock(ChatService.class)))
            .setControllerAdvice(new ApiErrors()).build();
        mvc.perform(post("/api/estimates").contentType("application/json").content("{\"category\":\"Teatro\",\"district\":\"Miraflores\",\"month\":13}"))
            .andExpect(status().isBadRequest()).andExpect(jsonPath("$.fields.month").value("Elige un mes del 1 al 12."));
        verifyNoInteractions(pricing);
    }
}
