package pe.culturaaccesible.api;

import pe.culturaaccesible.catalog.*;
import pe.culturaaccesible.catalog.port.CatalogStore;
import pe.culturaaccesible.pricing.PricingService;
import pe.culturaaccesible.chat.ChatService;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.HttpStatus;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import java.util.*;

@RestController
@RequestMapping("/api")
public class ApiController {
    private final CatalogService catalog;
    private final CatalogStore repository;
    private final PricingService pricing;
    private final ChatService chat;
    public ApiController(CatalogService catalog,CatalogStore repository,PricingService pricing,ChatService chat) {this.catalog=catalog;this.repository=repository;this.pricing=pricing;this.chat=chat;}
    public record ChatInput(@NotBlank @Size(max=600) String message,Map<String,Object> context,@Pattern(regexp="official|demo") String source) {}
    @PostMapping("/chat") public Map<String,Object> chat(@Valid @RequestBody ChatInput input){return chat.reply(input.message(),input.context(),input.source()==null?"official":input.source());}
    @GetMapping("/health") public Map<String,Object> health() {return Map.of("status",repository.healthy()?"ok":"error","database","mysql","application","CulturaAccesible Lima");}
    @GetMapping("/metadata") public Map<String,Object> metadata(@RequestParam(defaultValue="official") String source) {return catalog.metadata(source);}
    @GetMapping("/functions") public Map<String,Object> functions(@RequestParam(defaultValue="") String q,@RequestParam(defaultValue="") String district,@RequestParam(defaultValue="") String category,@RequestParam(defaultValue="all") String date,@RequestParam(defaultValue="all") String price,@RequestParam(required=false) List<String> needs,@RequestParam(defaultValue="official") String source) {
        var items=catalog.filterCatalog(catalog.search(q,district,category,date,price,needs),source);
        return Map.of("items",items,"total",items.size(),"demo","demo".equals(source),"source",source,"consulted_at","2026-10-17");
    }
    @GetMapping("/functions/{id}") public Map<String,Object> detail(@PathVariable long id) {return catalog.detail(id);}
    public record ReportInput(@NotNull @Positive Long function_id,Long condition_id,@NotBlank @Size(min=10,max=1000) String comment) {}
    @PostMapping("/reports") @ResponseStatus(HttpStatus.CREATED)
    public Map<String,Object> report(@Valid @RequestBody ReportInput input) {return catalog.report(input.function_id(),input.condition_id(),input.comment());}
    public record EstimateInput(@NotBlank String category,@NotBlank String district,@NotNull @Min(1) @Max(12) Integer month) {}
    @PostMapping("/estimates") public Map<String,Object> estimate(@Valid @RequestBody EstimateInput input) {return pricing.estimate(input.category(),input.district(),input.month());}
}
