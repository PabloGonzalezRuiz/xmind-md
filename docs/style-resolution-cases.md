# Casos de resolución de referencia del catálogo PMD 1.0.0

**Naturaleza:** vectores de prueba conceptuales. No son pruebas Python ni acreditan que el runtime actual los ejecute.

Notación:
- `D`: default.
- `S`: regla estructural.
- `H`: herencia del primer hijo.
- `M`: regla semántica.
- `R`: estilo explícito referenciado.
- `O`: override local.
- Las capas se fusionan por propiedad, no sustituyendo el objeto completo.

## Caso 1 — Semántica prevalece sobre estructura

Entrada: un hijo de una estructura `tree_table` tiene `semantic_role=table.header_cell`.

Candidatos: regla estructural `table.body-cell` y regla semántica `table.header-cell`.

Esperado: aplicar el estilo semántico de cabecera. La regla estructural no puede reemplazarlo aunque tenga una prioridad numérica mayor.

## Caso 2 — Fallback estructural sin rol

Entrada: un hijo de `tree_table` no declara rol semántico y no hay regla semántica coincidente.

Esperado: aplicar la regla estructural `structural.tree-table-cell` y el estilo `table.body-cell`.

## Caso 3 — Herencia de propiedades parciales

Primer hijo efectivo: `text.font_family=Arial`, `text.font_size=13`, `fill.color=#EEEEEE`, `border.width=1.5`.

Segundo hijo: rol `table.body_cell`, cuyo estilo semántico declara `fill.color=#F6A04D`.

Esperado: heredar familia, tamaño y borde; conservar relleno naranja del estilo semántico. Procedencia: herencia para tipografía/borde y regla semántica para relleno.

## Caso 4 — Excepción local parcial

Heredado: `text.font_size=13`, `fill.color=#EEEEEE`.

Hijo: override local `text.font_size=15`.

Esperado: tamaño 15 por override local; relleno gris heredado. No se sustituye el estilo completo.

## Caso 5 — Primer hijo sin estilo explícito

Primer hijo: no tiene referencia ni override, pero recibe defaults y una regla semántica que produce estilo efectivo.

Segundo hijo: sin regla ni excepción.

Esperado: segundo hijo recibe las propiedades efectivas del primero que no estén definidas por una capa de mayor prioridad. No se requiere que el primero declare un estilo manual.

## Caso 6 — Tabla con varias filas

Fila 1: celdas A1, B1. Fila 2: celdas A2, B2.

Esperado: B1 toma como fuente A1; B2 toma como fuente A2. No se hereda A1 → A2 ni B1 → A2 por estar en la misma tabla.

## Caso 7 — Recursividad

El primer hijo de un grupo hereda de su propio primer hermano en el nivel superior. Ese primer hijo contiene a su vez varios hijos.

Esperado: primero se resuelve el nodo con el contexto heredado del nivel superior; después se resuelve su propio grupo de hijos tomando el primer hijo local como fuente. No hay ciclos ni dependencia hacia descendientes.

## Caso 8 — Conflicto entre reglas de igual prioridad

Dos reglas semánticas coinciden con el mismo tema, misma prioridad y estilos que asignan colores distintos a `topic.text.color`.

Esperado: error de ambigüedad. No se usa orden de declaración ni orden alfabético como desempate.

## Caso 9 — null frente a ausencia

Un estilo declara `topic.fill.color=null`; otra capa inferior ofrece `#FFFFFF`.

Esperado: se restablece al default general de catálogo y se bloquea el valor inferior. Una capa posterior de mayor prioridad puede declarar otro color.

## Caso 10 — Literal inherited

Un importador recibe la cadena `"inherited"` en un atributo legado XMind.

Esperado: conservarla como dato de origen/compatibilidad, sin convertirla en ausencia ni en instrucción de herencia PMD. El validador del catálogo PMD no la acepta como valor visual.

## Caso 11 — Procedencia

Un valor final `topic.text.color` proviene de un override local.

Esperado: resultado incluye el valor y procedencia `local_override`, además del ID del tema y del estilo/regla de origen cuando corresponda. Para herencia incluye el ID del primer hijo fuente.

## Caso 12 — Estilo incompatible

Un estilo de relación se referencia desde un tema.

Esperado: error de incompatibilidad entre `applies_to` y el elemento destinatario.
