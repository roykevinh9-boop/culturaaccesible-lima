package pe.culturaaccesible.catalog;

import pe.culturaaccesible.infrastructure.jdbc.CatalogRepository;
import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;
import java.math.BigDecimal;
import java.time.*;
import java.util.*;

class CatalogServiceTest {
    static class FakeRepository extends CatalogRepository {
        Map<String,Object> function;
        List<Map<String,Object>> rows=List.of();
        int writes=0;
        FakeRepository(){super(null);}
        @Override public List<Map<String,Object>> functions(){return List.of(function);}
        @Override public List<Map<String,Object>> conditions(long id){return rows;}
        @Override public List<Map<String,Object>> supportTypes(){return List.of(Map.of("code","lsp","label","Interpretación en LSP"));}
        @Override public long createReport(long id,Long condition,String comment){writes++;return 17L;}
    }
    FakeRepository repository;
    CatalogService service;
    Map<String,Object> function;
    @BeforeEach void setup(){
        repository=new FakeRepository();
        service=new CatalogService(repository,Clock.fixed(Instant.parse("2026-10-17T17:00:00Z"),ZoneId.of("America/Lima")));
        function=new HashMap<>(Map.of("id",1L,"title","Escena Abierta","description","Ejemplo","category","Teatro","venue","Sala","district","Miraflores","address","Dirección","event_date","2026-10-17","event_time","19:00:00"));
        function.put("official_price",new BigDecimal("25"));function.put("demo",1);repository.function=function;
    }
    Map<String,Object> condition(String state,String scope,String source,String expires){
        var row=new HashMap<String,Object>(Map.of("id",2L,"code","lsp","label","Interpretación en LSP","state",state,"scope",scope,"note","Nota"));
        if(source!=null){row.put("source",source);row.put("reviewed_at","2026-10-01");}
        if(expires!=null)row.put("valid_until",expires);return row;
    }
    @Test void missingConditionIsUnconfirmed(){assertEquals("NO_CONFIRMADO",service.effectiveConditions(1).get(0).get("state"));}
    @Test void missingEvidenceCannotConfirm(){repository.rows=List.of(condition("DISPONIBLE","FUNCION",null,null));assertEquals("NO_CONFIRMADO",service.effectiveConditions(1).get(0).get("state"));}
    @Test void expiredEvidenceCannotConfirm(){repository.rows=List.of(condition("DISPONIBLE","FUNCION","Fuente","2026-10-16"));assertEquals("NO_CONFIRMADO",service.effectiveConditions(1).get(0).get("state"));}
    @Test void evidenceValidTodayIsAccepted(){repository.rows=List.of(condition("DISPONIBLE","FUNCION","Fuente","2026-10-17"));assertEquals("DISPONIBLE",service.effectiveConditions(1).get(0).get("state"));}
    @Test void venueLspDoesNotImplySessionSupport(){repository.rows=List.of(condition("DISPONIBLE","RECINTO","Fuente",null));assertEquals("NO_CONFIRMADO",service.effectiveConditions(1).get(0).get("state"));}
    @Test void explicitUnavailableIsPreserved(){repository.rows=List.of(condition("NO_DISPONIBLE","FUNCION","Fuente",null));assertEquals("NO_DISPONIBLE",service.effectiveConditions(1).get(0).get("state"));}
    @Test void functionOverrideHasPriority(){repository.rows=List.of(condition("NO_DISPONIBLE","FUNCION","Fuente",null),condition("DISPONIBLE","RECINTO","Fuente",null));assertEquals("NO_DISPONIBLE",service.effectiveConditions(1).get(0).get("state"));}
    @Test void unknownPriceIsNotFree(){function.put("official_price",null);assertTrue(service.search("","","","all","free",null).isEmpty());assertEquals(1,service.search("","","","all","unknown",null).size());}
    @Test void zeroPriceIsFree(){function.put("official_price",BigDecimal.ZERO);assertEquals(1,service.search("","","","all","free",null).size());assertTrue(service.search("","","","all","paid",null).isEmpty());}
    @Test void filtersCombine(){assertEquals(1,service.search("escena","Miraflores","Teatro","today","paid",null).size());assertTrue(service.search("escena","Barranco","Teatro","today","paid",null).isEmpty());}
    @Test void supportsRequireAvailable(){assertTrue(service.search("","","","all","all",List.of("lsp")).isEmpty());repository.rows=List.of(condition("DISPONIBLE","FUNCION","Fuente",null));assertEquals(1,service.search("","","","all","all",List.of("lsp")).size());}
    @Test void invalidSupportIsRejected(){assertThrows(IllegalArgumentException.class,()->service.search("","","","all","all",List.of("inventado")));}
    @Test void invalidDateIsRejected(){assertThrows(IllegalArgumentException.class,()->service.search("","","","mañana","all",null));}
    @Test void invalidPriceFilterIsRejected(){assertThrows(IllegalArgumentException.class,()->service.search("","","","all","cheap",null));}
    @Test void accentsDoNotBlockSearch(){function.put("title","Exposición de música");assertEquals(1,service.search("exposicion","","","all","all",null).size());}
    @Test void noMatchesReturnsEmpty(){assertTrue(service.search("palabrainexistente","","","all","all",null).isEmpty());}
    @Test void invalidReportNeverWrites(){assertThrows(IllegalArgumentException.class,()->service.report(1L,null,"   "));assertEquals(0,repository.writes);}
    @Test void validReportHasPendingState(){assertEquals("PENDIENTE",service.report(1L,null,"Fuente desactualizada").get("state"));assertEquals(1,repository.writes);}
    @Test void unknownFunctionIsNotFound(){assertThrows(org.springframework.web.server.ResponseStatusException.class,()->service.detail(999));}
    @Test void saturdayWeekendIncludesSunday(){function.put("event_date","2026-10-18");assertEquals(1,service.search("","","","weekend","all",null).size());function.put("event_date","2026-10-19");assertTrue(service.search("","","","weekend","all",null).isEmpty());}
}
