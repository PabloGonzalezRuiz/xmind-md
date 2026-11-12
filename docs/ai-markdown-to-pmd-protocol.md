# Protocolo IA: Markdown convencional → PMD 1.0.0

**Estado:** protocolo inicial de Fase 6; todavía no se ha demostrado una mejora cuantitativa ni existe conversor automático integrado. **Contrato:** PMD 1.0.0 → IR 1.1.0. **Catálogo:** `xmind-md.study@1.0.0`.

## Entradas obligatorias
1. Markdown fuente completo, conservado sin reinterpretar el texto normativo.
2. `docs/pmd-language-spec.md`, `docs/pmd-parser.md` y `catalog/style-catalog.json` de una revisión fijada.
3. Instrucciones del autor sobre jerarquía, tablas de árbol y estilos, si las hay. No suponerlas.
4. Identificador estable de origen (`source_path`) para IDs deterministas.

## Salidas
- Un archivo `*.pmd.md` sintácticamente válido, sin explicaciones intercaladas.
- Un informe separado de decisiones y ambigüedades: fragmento de origen, decisión, evidencia, nivel de confianza cualitativo y acción requerida. No añadir claves no reconocidas a directivas PMD.
- Un resultado de validación ejecutada, o el estado explícito «no validado»; nunca afirmar que un modelo de lenguaje ha ejecutado el parser si no ocurrió.

## Instrucciones para el modelo
Eres un transformador conservador de Markdown a Pableras Markdown. Tu misión es preservar el contenido y la jerarquía verificables y añadir solo anotaciones semánticas justificadas. No crees, resumas, completes, corrijas ni reordenes texto jurídico sin orden expresa. No infieras vigencia legal ni autenticidad de la fuente.

1. Lee el catálogo real y utiliza exclusivamente los IDs de rol y estilo existentes. Un rol describe significado; `style_ref` describe apariencia. Prefiere omitir `style_ref` cuando el rol basta para que el futuro resolutor seleccione estilo.
2. Crea front matter `pmd_version: "1.0.0"`, título y referencia exacta al catálogo si hay roles o estilos.
3. El primer H1 es la raíz única. Conserva los encabezados de la fuente. Si falta un H1, propón uno editorial claramente identificado en el informe; no lo presentes como título legal oficial.
4. Solo los encabezados ATX crean temas. Listas, tablas pipe y negritas son contenido, no temas por defecto. No promociones apartados o listas a encabezados salvo estructura explícita o autorización del autor.
5. Usa `legal.article`, `legal.chapter`, etc. únicamente si los rótulos o el contexto proporcionan evidencia inequívoca. No conviertas una recomendación en obligación ni una condición en excepción.
6. No generes `tree_table` a partir de negritas, hermanos, listas o tablas Markdown. Solo si la fuente o las instrucciones describen inequívocamente filas, celdas y pertenencia, genera IDs explícitos para el contenedor y todos sus hijos directos, y comprueba cobertura exacta.
7. Conserva citas, números, puntuación, referencias, listas y orden de origen. No añadas artículos, plazos, prohibiciones o referencias no presentes.
8. Usa `:::pmd` inmediatamente antes del encabezado al que afecta. No escribas campos privados XMind ni directivas `:::xmind`.
9. No generes `style_overrides` sin instrucciones visuales expresas. No uses `inherited` como valor. No presupongas que la herencia por primer hijo ya funciona en runtime.
10. Ante ambigüedad, conserva Markdown sin rol o estructura inventados y regístrala en el informe separado. Prioriza un PMD menos anotado pero válido frente a otro más vistoso e infundado.

## Puerta de validación
1. Ejecutar `parse_pmd_markdown(pmd_text, source_path=source_path)` desde `xmind_md.ir_parser`.
2. Si hay `PMDParseError`, corregir solo sintaxis/referencias sin alterar el significado y repetir hasta pasar o registrar bloqueo.
3. Verificar manualmente invariantes de preservación: texto jurídico, numeración, orden, encabezados, enlaces y ausencia de contenido añadido.
4. Verificar todos los roles contra el catálogo y cada `tree_table` contra la evidencia de entrada.
5. Guardar junto al fixture la entrada, salida, informe de ambigüedades y resultado de validación.

## Evaluación reproducible (pendiente de implementación)
- **Validez PMD:** documentos que pasan el parser / documentos evaluados.
- **Precisión semántica:** roles correctos / roles propuestos, comparados con anotación humana.
- **Cobertura:** roles correctos / roles esperados, separada de precisión.
- **Preservación:** incidencias de texto, orden y referencias por documento; objetivo cero alteraciones no autorizadas.
- **Esfuerzo de edición:** número de correcciones manuales y minutos por documento antes/después, medidos con el mismo corpus y evaluador.
- **Tablas:** falsos positivos de `tree_table`; objetivo cero.

No declarar cumplido el criterio de cierre de Fase 6 hasta disponer de corpus versionado, ejecución reproducible, métricas y reducción de edición medida. La exportación XMind y la resolución visual completa no forman parte de esta fase.
