package pe.culturaaccesible.controlador;

import org.springframework.web.bind.annotation.*;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.http.*;
import org.springframework.dao.DataAccessException;
import org.springframework.web.server.ResponseStatusException;
import pe.culturaaccesible.vista.ApiView;
import java.util.LinkedHashMap;
import java.util.Map;

@RestControllerAdvice
public class ApiErrors {
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<?> badInput(IllegalArgumentException e) {return ResponseEntity.badRequest().body(ApiView.message(e.getMessage()));}
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<?> invalid(MethodArgumentNotValidException e) {
        Map<String,String> fields=new LinkedHashMap<>();
        for (var error:e.getBindingResult().getFieldErrors()) {
            String message=switch(error.getField()) {
                case "comment" -> "Escribe entre 10 y 1000 caracteres.";
                case "month" -> "Elige un mes del 1 al 12.";
                case "message" -> "Escribe un mensaje de 1 a 600 caracteres.";
                case "function_id" -> "Selecciona una función válida.";
                case "category" -> "Selecciona una disciplina.";
                case "district" -> "Selecciona un distrito.";
                case "source" -> "Selecciona la cartelera o los ejemplos del curso.";
                default -> "Revisa este campo.";
            };
            fields.putIfAbsent(error.getField(),message);
        }
        return ResponseEntity.badRequest().body(new ApiView.ValidationResponse("Revisa los campos indicados.",Map.copyOf(fields)));
    }
    @ExceptionHandler(ResponseStatusException.class)
    public ResponseEntity<?> status(ResponseStatusException e) {return ResponseEntity.status(e.getStatusCode()).body(ApiView.message(e.getReason()==null?"No se pudo completar la operación.":e.getReason()));}
    @ExceptionHandler(DataAccessException.class)
    public ResponseEntity<?> database(DataAccessException e) {return ResponseEntity.status(503).body(ApiView.message("No pudimos consultar o guardar los datos. Intenta nuevamente; la operación no está confirmada."));}
    @ExceptionHandler(org.springframework.http.converter.HttpMessageNotReadableException.class)
    public ResponseEntity<?> malformed(Exception e) {return ResponseEntity.badRequest().body(ApiView.message("El formato de los datos no es válido."));}
}
