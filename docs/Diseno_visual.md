# Color e información accesible

Actualización del 22/10/2026. La intención visual es mantener una identidad cultural tranquila y una jerarquía clara. Es una decisión de diseño que requiere validación con personas; no se afirma que un color cause confianza o una emoción universal.

| Uso | Texto | Fondo | Propósito |
|---|---|---|---|
| Acción principal | #FFFFFF | #12675E | Identificar búsqueda y acciones principales |
| Texto general | #17343B | #F7FAF9 | Lectura sobre fondo claro |
| Texto secundario | #4C6268 | #F7FAF9 | Explicaciones con contraste legible |
| Disponible | #155E43 | #E8F5ED | Diferenciar disponibilidad respaldada |
| No confirmado | #744B00 | #FFF4D6 | Señalar información pendiente sin presentarla como disponible |
| No disponible | #8A2635 | #FCECEF | Distinguir una declaración negativa documentada |

Los tres estados conservan etiquetas textuales: el significado nunca depende solo de verde, ámbar o rojo. El foco tiene contorno visible, y el modo de alto contraste sustituye las combinaciones por texto negro sobre blanco. Se conservan tamaño de texto, reducción de movimiento y subrayado de enlaces.

Los estilos semánticos se agrupan en `frontend/theme.css`; la maquetación existente permanece en `styles.css`. Los contrastes calculados se registran en `docs/evidencias/contraste-1.4.json`. El cálculo de estas parejas no equivale a una auditoría completa WCAG ni reemplaza las pruebas con usuarios y tecnologías de apoyo.
