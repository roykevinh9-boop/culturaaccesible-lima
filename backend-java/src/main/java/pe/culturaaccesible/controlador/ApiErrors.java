package pe.culturaaccesible.controlador;

import org.springframework.web.bind.annotation.*;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.http.*;
import org.springframework.dao.DataAccessException;
import org.springframework.web.server.ResponseStatusException;
import pe.culturaaccesible.vista.ApiView;

@RestControllerAdvice
public class ApiErrors {
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<?> badInput(IllegalArgumentException e) {return ResponseEntity.badRequest().body(ApiView.message(e.getMessage()));}
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<?> invalid(MethodArgumentNotValidException e) {return ResponseEntity.badRequest().body(ApiView.message("Revisa los campos obligatorios y sus valores."));}
    @ExceptionHandler(ResponseStatusException.class)
    public ResponseEntity<?> status(ResponseStatusException e) {return ResponseEntity.status(e.getStatusCode()).body(ApiView.message(e.getReason()==null?"No se pudo completar la operación.":e.getReason()));}
    @ExceptionHandler(DataAccessException.class)
    public ResponseEntity<?> database(DataAccessException e) {return ResponseEntity.status(503).body(ApiView.message("No pudimos consultar o guardar los datos. Intenta nuevamente; la operación no está confirmada."));}
    @ExceptionHandler(org.springframework.http.converter.HttpMessageNotReadableException.class)
    public ResponseEntity<?> malformed(Exception e) {return ResponseEntity.badRequest().body(ApiView.message("El formato de los datos no es válido."));}
}
