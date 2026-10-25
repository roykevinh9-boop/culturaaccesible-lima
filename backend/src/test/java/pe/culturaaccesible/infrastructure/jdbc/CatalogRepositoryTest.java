package pe.culturaaccesible.infrastructure.jdbc;

import java.math.BigInteger;
import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.dao.DataAccessResourceFailureException;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.dao.DataRetrievalFailureException;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

class CatalogRepositoryTest {
    private StoredProcedureExecutor executor;
    private CatalogRepository repository;

    @BeforeEach void setup() {
        executor = mock(StoredProcedureExecutor.class);
        repository = new CatalogRepository(executor);
    }

    @Test void acceptsAnUnsignedIdentifierReturnedByMysql() {
        when(executor.execute(eq(CatalogProcedure.CREATE_REPORT), anyMap()))
            .thenReturn(List.of(Map.of("id", BigInteger.valueOf(27))));
        assertEquals(27L, repository.createReport(1L, null, "Revisar una fuente publicada"));
    }

    @Test void acceptsANullOptionalConditionWithoutDroppingTheParameter() {
        when(executor.execute(eq(CatalogProcedure.CREATE_REPORT), anyMap()))
            .thenReturn(List.of(Map.of("id", 12L)));
        repository.createReport(1L, null, "Revisar una fuente publicada");
        verify(executor).execute(eq(CatalogProcedure.CREATE_REPORT), argThat(parameters ->
            parameters.containsKey("p_condition_id") && parameters.get("p_condition_id") == null));
    }

    @Test void translatesAnExplicitDatabaseRejectionIntoInvalidInput() {
        when(executor.execute(eq(CatalogProcedure.CREATE_REPORT), anyMap()))
            .thenThrow(new DataIntegrityViolationException("Entrada rechazada",
                new SQLException("La condicion no pertenece a esta funcion.", "45000", 1644)));
        var error = assertThrows(IllegalArgumentException.class,
            () -> repository.createReport(1L, 999L, "Comentario suficientemente largo"));
        assertEquals("La condicion no pertenece a esta funcion.", error.getMessage());
    }

    @Test void doesNotTranslateAnOutageIntoAValidationError() {
        var outage = new DataAccessResourceFailureException("Servidor no disponible");
        when(executor.execute(eq(CatalogProcedure.CREATE_REPORT), anyMap())).thenThrow(outage);
        assertSame(outage, assertThrows(DataAccessResourceFailureException.class,
            () -> repository.createReport(1L, null, "Comentario suficientemente largo")));
    }

    @Test void doesNotConfirmASaveWhenTheRoutineReturnsNoIdentifier() {
        when(executor.execute(eq(CatalogProcedure.CREATE_REPORT), anyMap())).thenReturn(List.of());
        assertThrows(DataRetrievalFailureException.class,
            () -> repository.createReport(1L, null, "Comentario suficientemente largo"));
    }

    @Test void rejectsAmbiguousMultipleIdentifiers() {
        when(executor.execute(eq(CatalogProcedure.CREATE_REPORT), anyMap()))
            .thenReturn(List.of(Map.of("id", 1L), Map.of("id", 2L)));
        assertThrows(DataRetrievalFailureException.class,
            () -> repository.createReport(1L, null, "Comentario suficientemente largo"));
    }
}
