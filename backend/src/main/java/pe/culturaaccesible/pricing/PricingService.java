package pe.culturaaccesible.pricing;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;
import java.net.URI;
import java.net.http.*;
import java.time.Duration;
import java.util.*;

@Service
public class PricingService {
    private final HttpClient client=HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2)).build();
    private final ObjectMapper json;
    private final String base;
    public PricingService(ObjectMapper json,@Value("${cal.python-url}") String base) {this.json=json;this.base=base;}
    public Map<String,Object> estimate(String category,String district,int month) {
        try {
            String body=json.writeValueAsString(Map.of("categoria",category,"distrito",district,"mes",month));
            var request=HttpRequest.newBuilder(URI.create(base+"/estimate")).timeout(Duration.ofSeconds(5)).header("Content-Type","application/json").POST(HttpRequest.BodyPublishers.ofString(body)).build();
            var response=client.send(request,HttpResponse.BodyHandlers.ofString());
            if(response.statusCode()==422 || response.statusCode()==400) throw new ResponseStatusException(HttpStatus.UNPROCESSABLE_ENTITY,"La estimación solo cubre Teatro, Museo, Danza, Música y Exposición en Miraflores o Cercado de Lima, con mes de 1 a 12.");
            if(response.statusCode()!=200) throw new java.io.IOException("Servicio de estimación no disponible");
            return json.readValue(response.body(),new TypeReference<>(){});
        } catch(ResponseStatusException e) {throw e;}
        catch(InterruptedException e) {Thread.currentThread().interrupt(); throw unavailable();}
        catch(Exception e) {throw unavailable();}
    }
    private ResponseStatusException unavailable() {return new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE,"La estimación no está disponible. Puedes continuar consultando el catálogo y las fichas.");}
}
