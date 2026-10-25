package pe.culturaaccesible.modelo.catalogo;

import java.util.*;
import java.util.stream.LongStream;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import pe.culturaaccesible.modelo.puertos.CatalogStore;
import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.*;

class CatalogBatchTest {
    @ParameterizedTest @ValueSource(ints={1,57,250})
    void searchesUseThreeCallsRegardlessOfCatalogSize(int count) {
        var repository=mock(CatalogStore.class);
        when(repository.supportTypes()).thenReturn(List.of(Map.of("code","lsp","label","Intérprete de LSP")));
        when(repository.functions()).thenReturn(LongStream.rangeClosed(1,count).mapToObj(id->{
            Map<String,Object> row=new HashMap<>();
            row.put("id",id);row.put("title","Función "+id);row.put("category","Teatro");
            row.put("venue","Sala");row.put("district","Miraflores");row.put("demo",0);
            row.put("event_date","2026-10-24");row.put("official_price",0);return row;
        }).toList());
        when(repository.catalogConditions()).thenReturn(List.of(Map.of(
            "function_id",1L,"id",1L,"code","lsp","label","Intérprete de LSP",
            "state","DISPONIBLE","scope","FUNCION","source","Fuente",
            "reviewed_at","2026-10-24")));
        var results=new CatalogService(repository).search("","","","all","all",List.of());
        assertEquals(count,results.size());
        var conditions=(List<Map<String,Object>>)results.get(0).get("conditions");
        assertEquals("DISPONIBLE",conditions.get(0).get("state"));
        assertFalse(conditions.get(0).containsKey("function_id"));
        if(count>1)assertEquals("NO_CONFIRMADO",((List<Map<String,Object>>)results.get(1).get("conditions")).get(0).get("state"));
        verify(repository,times(1)).functions();verify(repository,times(1)).catalogConditions();
        verify(repository,times(1)).supportTypes();verifyNoMoreInteractions(repository);
    }
}
