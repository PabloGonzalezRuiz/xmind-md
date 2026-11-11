# Auditoría documental — tarea 7

- **Fecha:** 2026-11-11
- **Rama:** `main`
- **Alcance:** README, gramática Markdown, contrato IR, sistema de estilos, adaptador XMind, guía de desarrollo, catálogo de archivos, ejemplos y documentos de continuidad/release.
- **Estado:** revisión editorial y técnica completada; validación CI final pendiente de registrar.

## 1. Dictamen

Se han contrastado las afirmaciones documentales con el parser, el modelo IR, el resolutor de estilos, el adaptador XMind, la configuración ejecutable y el workflow CI. Se han corregido las discrepancias detectadas y se ha explicitado qué forma parte del contrato neutral, qué genera el parser y qué puede exportar el perfil XMind actual.

## 2. Cambios documentales

### README

- Actualizado el número de pruebas a 161 por versión, en Python 3.10, 3.11 y 3.12.
- La sección de CI identifica la matriz real de versiones.
- El ejemplo de exportación XMind utiliza `examples/xmind-smoke-test.md`.
- Se aclara que `examples/constitucion.md` es el ejemplo avanzado de parsing/IR/JSON y no es exportable al perfil XMind actual.
- Se documenta el requisito de coordenadas para temas `detached`.

### Gramática Markdown

- `kind` enumera `attached`, `detached`, `callout` y `summary`; la raíz debe ser `attached`.
- Se especifica que el perfil XMind exporta `attached`, `detached` y `callout`; `detached` exige `layout.position.x/y`, y `summary` no se exporta.
- El ejemplo YAML externo se ha migrado al esquema realmente consumido: `style_sets` y `styles`, propiedades agrupadas por tipo de elemento.
- Se documentan valores YAML JSON-compatibles, la normalización ISO de fechas y el rechazo de NaN/infinito y tipos no representables.
- Se ha corregido el texto de las restricciones de enlaces e imágenes inline.

### Especificación IR

- Se distingue la capacidad representacional del IR de la cobertura del parser y del adaptador.
- Se documentan los cuatro tipos de tema y la restricción de exportación XMind.
- Se aclara que las referencias de estilo se resuelven después de combinar catálogos embebidos y externos.

### Sistema de estilos

- Se identifica el esquema YAML ejecutable actual y se retiran como formato activo las estructuras obsoletas `extends`, `elements`, `applies_to` y `properties`.
- Se actualizan ejemplos de conjuntos y estilos nombrados.
- Se documenta la precedencia real de `resolve_ir_styles()`: defaults del sistema, `metadata.style_defaults`, conjunto, estilo nombrado y overrides locales.
- Se diferencia el vocabulario neutral de diseño de la lista de propiedades efectivamente exportables.

### Adaptador XMind

- Se corrige la contradicción sobre temas `detached` y `callout`: ambos están soportados; `detached` requiere coordenadas.
- Se mantiene `summary` como tipo IR no exportable.
- Se aclaran los enlaces `web`, `topic` y `file://`.
- Se documenta el mapeo de propiedades de línea de relaciones y el rechazo de recursos, tareas, boundaries, summaries, extensiones y estilos no admitidos.
- Se normaliza el formato Markdown del documento para que los identificadores técnicos se representen correctamente.

### Guía de desarrollo y catálogo

- Los ejemplos CLI de salida XMind utilizan el fixture compatible.
- La guía describe la matriz de tres versiones y el job de distribución que instala wheel/sdist en Python 3.12.
- Se conserva la advertencia de que CI es Ubuntu y no acredita compatibilidad Windows.
- El catálogo incluye este informe de auditoría.

## 3. Ejemplos y pruebas manuales

- `examples/constitucion.md` demuestra el subconjunto enriquecido y genera IR/JSON; incluye recursos, tareas, boundaries y summaries no exportables a XMind.
- `examples/xmind-smoke-test.md` es el documento mínimo para generar un libro XMind.
- El fixture versionado `tests/fixtures/xmind/xmind-md-smoke-test.xmind` fue abierto, guardado y reabierto manualmente en XMind Desktop 26.05.01107. Esa prueba no equivale a una inspección manual del smoke más reciente con estilos.

## 4. Limitaciones que deben permanecer visibles

- No es un parser CommonMark/GFM completo.
- XMind no exporta assets/imágenes, tareas, boundaries, summaries, extensiones ni temas `summary`.
- Los bloques de contenido se aplanan a notas; se pierden estructura y parte del formato inline.
- El smoke actual se valida estructuralmente en CI, pero no se ha reabierto manualmente en XMind Desktop tras la última incorporación de estilos.
- La CI ejecuta en Ubuntu. No hay evidencia de ejecución Windows.
- Python 3.10 permanece declarado por compatibilidad técnica, aunque upstream dejó de darle soporte el 2026-10-01.

## 5. Evidencia y cierre

La tarea se considera documentalmente completa cuando el workflow CI del commit que contiene estas modificaciones finaliza con `completed / success`. El identificador del run y su commit validado se añadirán aquí y en los documentos de continuidad tras la ejecución.
