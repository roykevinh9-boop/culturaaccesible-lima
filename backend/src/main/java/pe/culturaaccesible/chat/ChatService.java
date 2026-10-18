package pe.culturaaccesible.chat;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;
import pe.culturaaccesible.catalog.CatalogService;
import java.net.URI;
import java.net.http.*;
import java.time.*;
import java.util.*;

/** Cada consulta recibe únicamente el catálogo autorizado desde MySQL, sin ejecutar SQL del usuario. */
@Service
public class ChatService {
    private final CatalogService catalog;
    private final ObjectMapper json;
    private final String base;
    private final HttpClient client=HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2)).build();
    public ChatService(CatalogService catalog,ObjectMapper json,@Value("${cal.python-url}") String base){this.catalog=catalog;this.json=json;this.base=base;}
    public Map<String,Object> reply(String message,Map<String,Object> context,String source){
        var items=catalog.filterCatalog(catalog.search("","","","all","all",List.of()),source);
        try{
            String body=json.writeValueAsString(Map.of("message",message,"context",context==null?Map.of():context,"items",items,"today",LocalDate.now(ZoneId.of("America/Lima")).toString()));
            var request=HttpRequest.newBuilder(URI.create(base+"/chat")).timeout(Duration.ofSeconds(8)).header("Content-Type","application/json").POST(HttpRequest.BodyPublishers.ofString(body)).build();
            var response=client.send(request,HttpResponse.BodyHandlers.ofString());
            if(response.statusCode()==422)throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"Revisa la consulta y los filtros del chat. Puedes iniciar una nueva conversación.");
            if(response.statusCode()!=200)throw new java.io.IOException();
            Map<String,Object> result=json.readValue(response.body(),new TypeReference<>(){});
            result.put("source",source);result.put("catalog_note","Instantánea recuperada el 17/10/2026. Consulta cambios con el organizador.");
            return result;
        }catch(ResponseStatusException e){throw e;}
        catch(InterruptedException e){Thread.currentThread().interrupt();throw unavailable();}
        catch(Exception e){throw unavailable();}
    }
    private ResponseStatusException unavailable(){return new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE,"AccesI no está disponible en este momento. Puedes seguir utilizando los filtros y las fichas del catálogo.");}
}
