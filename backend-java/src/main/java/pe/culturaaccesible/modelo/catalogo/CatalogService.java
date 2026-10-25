package pe.culturaaccesible.modelo.catalogo;

import pe.culturaaccesible.modelo.puertos.CatalogStore;

import org.springframework.stereotype.Service;
import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;
import java.math.BigDecimal;
import java.text.Normalizer;
import java.time.*;
import java.util.*;

/** Reglas de catálogo y confianza. Falta de evidencia jamás significa Disponible. */
@Service
public class CatalogService {
    private final CatalogStore repository;
    private final Clock clock;
    @org.springframework.beans.factory.annotation.Autowired
    public CatalogService(CatalogStore repository) { this(repository, Clock.system(ZoneId.of("America/Lima"))); }
    CatalogService(CatalogStore repository, Clock clock) { this.repository=repository; this.clock=clock; }
    public static String normalized(String text) {
        return Normalizer.normalize(text == null ? "" : text, Normalizer.Form.NFD).replaceAll("\\p{M}", "").toLowerCase(Locale.ROOT).trim();
    }

    public Map<String,Object> metadata() {
        return metadata("official");
    }
    public Map<String,Object> metadata(String source) {
        var types=repository.supportTypes();
        var functions=filterCatalog(all(types),source);
        return Map.of("districts", functions.stream().map(f->f.get("district")).distinct().sorted(Comparator.comparing(Object::toString)).toList(),
          "categories", functions.stream().map(f->f.get("category")).distinct().sorted(Comparator.comparing(Object::toString)).toList(),
          "supports", types, "today", LocalDate.now(clock).toString(), "demo", "demo".equals(source),"consulted_at","2026-10-17");
    }
    public List<Map<String,Object>> filterCatalog(List<Map<String,Object>> items,String source) {
        if(!Set.of("official","demo","all").contains(source)) throw new IllegalArgumentException("Catálogo no reconocido.");
        return items.stream().filter(f->"all".equals(source)||((Boolean)f.get("demo"))=="demo".equals(source)).toList();
    }

    private List<Map<String,Object>> all() {
        return all(repository.supportTypes());
    }

    private List<Map<String,Object>> all(List<Map<String,Object>> types) {
        Map<Long,List<Map<String,Object>>> grouped=new HashMap<>();
        for (var condition:repository.catalogConditions()) {
            long id=((Number)condition.get("function_id")).longValue();
            grouped.computeIfAbsent(id,key->new ArrayList<>()).add(condition);
        }
        return repository.functions().stream().map(row -> {
            Map<String,Object> result=new LinkedHashMap<>();
            result.put("id", ((Number)row.get("id")).longValue());
            for (String key:List.of("title","description","category","venue","district","address","official_url","image_url","image_alt","image_credit")) result.put(key,row.get(key));
            result.put("date", row.get("event_date").toString());
            result.put("time", row.get("event_time")==null?null:row.get("event_time").toString());
            result.put("price_from",row.get("price_from")!=null && ((Number)row.get("price_from")).intValue()==1);
            result.put("consulted_at",row.get("consulted_at")==null?null:row.get("consulted_at").toString());
            result.put("official_price", row.get("official_price"));
            result.put("demo", ((Number)row.get("demo")).intValue()==1);
            result.put("conditions", effectiveConditions(grouped.getOrDefault(
                ((Number)row.get("id")).longValue(),List.of()),types));
            return result;
        }).toList();
    }

    public List<Map<String,Object>> effectiveConditions(long id) {
        return effectiveConditions(repository.conditions(id),repository.supportTypes());
    }

    private List<Map<String,Object>> effectiveConditions(List<Map<String,Object>> raw,List<Map<String,Object>> types) {
        Map<String,Map<String,Object>> unique=new LinkedHashMap<>();
        LocalDate today=LocalDate.now(clock);
        for (var row:raw) {
            String code=row.get("code").toString();
            if (unique.containsKey(code)) continue; // Una declaración de función prevalece sobre recinto.
            Map<String,Object> item=new LinkedHashMap<>();
            row.forEach((key,value)->{if(!"function_id".equalsIgnoreCase(key))item.put(key.toLowerCase(Locale.ROOT),value==null?null:value.toString());});
            item.put("id",((Number)row.get("id")).longValue());
            boolean hasEvidence=row.get("source")!=null && row.get("reviewed_at")!=null;
            boolean expired=row.get("valid_until")!=null && LocalDate.parse(row.get("valid_until").toString()).isBefore(today);
            boolean sessionOnly=Set.of("lsp","subtitulos","audiodescripcion","tactil").contains(code);
            boolean wrongScope=sessionOnly && !"FUNCION".equals(row.get("scope"));
            if (!hasEvidence || expired || wrongScope) {
                item.put("state","NO_CONFIRMADO");
                item.put("verification_note",expired?"Evidencia vencida: requiere nueva revisión.":wrongScope?"Este apoyo requiere confirmación para la función.":"Falta una fuente y fecha de revisión.");
            }
            unique.put(code,item);
        }
        for (var type:types) {
            String code=type.get("code").toString();
            unique.computeIfAbsent(code,k->new LinkedHashMap<>(Map.of("code",code,"label",type.get("label"),"state","NO_CONFIRMADO","scope","FUNCION","verification_note","Sin información documentada.")));
        }
        return new ArrayList<>(unique.values());
    }

    @SuppressWarnings("unchecked")
    public List<Map<String,Object>> search(String q,String district,String category,String date,String price,List<String> needs) {
        if (q!=null && q.length()>150) throw new IllegalArgumentException("La búsqueda admite hasta 150 caracteres.");
        if (needs==null) needs=List.of();
        var types=repository.supportTypes();
        var validCodes=types.stream().map(r->r.get("code").toString()).toList();
        if (!validCodes.containsAll(needs)) throw new IllegalArgumentException("Hay un apoyo no reconocido.");
        LocalDate today=LocalDate.now(clock);
        LocalDate start=null, end=null;
        switch(date==null?"all":date) {
            case "all" -> { }
            case "today" -> { start=today; end=today; }
            case "month" -> {start=today;end=today.withDayOfMonth(today.lengthOfMonth());}
            case "weekend" -> {int offset=(DayOfWeek.SATURDAY.getValue()-today.getDayOfWeek().getValue()+7)%7; if(today.getDayOfWeek()==DayOfWeek.SUNDAY) {start=today;end=today;} else {start=today.plusDays(offset);end=start.plusDays(1);}}
            default -> throw new IllegalArgumentException("Filtro de fecha no válido.");
        }
        if (price!=null && !Set.of("all","free","paid","unknown").contains(price)) throw new IllegalArgumentException("Filtro de precio no válido.");
        final LocalDate from=start,to=end;
        final List<String> required=List.copyOf(needs);
        String query=normalized(q);
        return all(types).stream().filter(f->{
            String haystack=normalized(f.get("title")+" "+f.get("category")+" "+f.get("venue"));
            if(!query.isEmpty() && !haystack.contains(query)) return false;
            if(district!=null && !district.isBlank() && !normalized(district).equals(normalized(f.get("district").toString()))) return false;
            if(category!=null && !category.isBlank() && !normalized(category).equals(normalized(f.get("category").toString()))) return false;
            LocalDate eventDate=LocalDate.parse(f.get("date").toString());
            if(from!=null && (eventDate.isBefore(from)||eventDate.isAfter(to))) return false;
            BigDecimal amount=f.get("official_price")==null?null:new BigDecimal(f.get("official_price").toString());
            if("free".equals(price) && (amount==null||amount.signum()!=0)) return false;
            if("paid".equals(price) && (amount==null||amount.signum()<=0)) return false;
            if("unknown".equals(price) && amount!=null) return false;
            var conditions=(List<Map<String,Object>>)f.get("conditions");
            return required.stream().allMatch(code->conditions.stream().anyMatch(c->code.equals(c.get("code"))&&"DISPONIBLE".equals(c.get("state"))));
        }).toList();
    }

    public Map<String,Object> detail(long id) {
        return all().stream().filter(f->((Number)f.get("id")).longValue()==id).findFirst().orElseThrow(()->new ResponseStatusException(HttpStatus.NOT_FOUND,"Función no encontrada."));
    }

    public Map<String,Object> report(long functionId,Long conditionId,String comment) {
        detail(functionId);
        String value=comment==null?"":comment.trim();
        if(value.length()<10 || value.length()>1000) throw new IllegalArgumentException("Escribe entre 10 y 1000 caracteres.");
        long id=repository.createReport(functionId,conditionId,value);
        return Map.of("id",id,"state","PENDIENTE","message","Reporte registrado para revisión. La ficha aún no ha sido modificada.");
    }
}
