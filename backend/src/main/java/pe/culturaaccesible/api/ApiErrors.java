package pe.culturaaccesible.api;

import org.springframework.web.bind.annotation.*;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.http.*;
import org.springframework.dao.DataAccessException;
import org.springframework.web.server.ResponseStatusException;
import java.util.Map;

@RestControllerAdvice
public class ApiErrors {
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<?> badInput(IllegalArgumentException e) {return ResponseEntity.badRequest().body(Map.of("message",e.getMessage()));}
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<?> invalid(MethodArgumentNotValidException e) {return ResponseEntity.badRequest().body(Map.of("message","Revisa los campos obligatorios y sus valores."));}
    @ExceptionHandler(ResponseStatusException.class)
    public ResponseEntity<?> status(ResponseStatusException e) {return ResponseEntity.status(e.getStatusCode()).body(Map.of("message",e.getReason()==null?"No se pudo completar la operación.":e.getReason()));}
    @ExceptionHandler(DataAccessException.class)
    public ResponseEntity<?> database(DataAccessException e) {return ResponseEntity.status(503).body(Map.of("message","No pudimos consultar o guardar los datos. Intenta nuevamente; la operación no está confirmada."));}
    @ExceptionHandler(org.springframework.http.converter.HttpMessageNotReadableException.class)
    public ResponseEntity<?> malformed(Exception e) {return ResponseEntity.badRequest().body(Map.of("message","El formato de los datos no es válido."));}
}
