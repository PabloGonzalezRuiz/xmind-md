# Auditoría documental — tarea 7

- **Fecha:** 2026-11-11
- **Rama:** `main`
- **Alcance:** README, gramática Markdown, contrato IR, sistema de estilos, adaptador XMind, guía de desarrollo, catálogo de archivos, ejemplos y documentos de continuidad/release.
- **Estado:** COMPLETADA Y VALIDADA.

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

## 3. Documentos complementarios revisados

- **Arquitectura:** flujo real de CLI, matriz de Python y evidencia CI actualizadas; se aclara la resolución de estilos externos.
- **Plan de migración IR:** marcado como registro histórico completado; se eliminan afirmaciones pendientes sobre integración XMind en CLI y consolidación del contrato.
- **Evaluación del motor XMind:** las secciones históricas de plan/resultado se sustituyen por el perfil real; relaciones con control points, integración CLI y estado de interoperabilidad quedan descritos.
- **Licencia MIT:** se corrige el hallazgo antiguo de `escudo.png`; el ejemplo utiliza el SVG original versionado y la suite comprueba su presencia. Se mantiene el límite del inventario de terceros (no es SBOM completo).
- **Pruebas de integración XMind:** se documenta la matriz CI actual, 161 pruebas por versión y validación wheel/sdist.
- **Catálogo de archivos:** incluye el nuevo informe de esta tarea.

## 4. Ejemplos y pruebas manuales

- `examples/constitucion.md` demuestra el subconjunto enriquecido y genera IR/JSON; incluye recursos, tareas, boundaries y summaries no exportables a XMind.
- `examples/xmind-smoke-test.md` es el documento mínimo para generar un libro XMind.
- El fixture versionado `tests/fixtures/xmind/xmind-md-smoke-test.xmind` fue abierto, guardado y reabierto manualmente en XMind Desktop 26.05.01107. Esa prueba no equivale a una inspección manual del smoke más reciente con estilos.

## 5. Limitaciones que deben permanecer visibles

- No es un parser CommonMark/GFM completo.
- XMind no exporta assets/imágenes, tareas, boundaries, summaries, extensiones ni temas `summary`.
- Los bloques de contenido se aplanan a notas; se pierden estructura y parte del formato inline.
- El smoke actual se valida estructuralmente en CI, pero no se ha reabierto manualmente en XMind Desktop tras la última incorporación de estilos.
- La CI ejecuta en Ubuntu. No hay evidencia de ejecución Windows.
- Python 3.10 permanece declarado por compatibilidad técnica, aunque upstream dejó de darle soporte el 2026-10-01.

## 6. Evidencia y cierre

Run [43009183421](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/43009183421), commit `6cd1c937ee090bc36483be49e7d1f5c740e0926a`, finalizó `completed / success`. Python 3.10/3.11/3.12: Ruff lint/format correctos y **161 pruebas superadas por versión**. Los tres jobs generaron sus XMind smoke. El job de distribuciones construyó wheel/sdist, verificó contenido/licencia, instaló ambos en entornos limpios separados y ejecutó conversiones CLI JSON/XMind; validación ZIP/MIME/JSON correcta.

Artefactos: `python-distributions` ID `13850260351` (78.103 bytes; SHA-256 del ZIP de Actions `c8109d8d722befe2a5ed1bc953af15711b0caaf9d0f2bf9928bc050796b38a0f`); smoke Python 3.10 ID `13849418602`, Python 3.11 ID `13848884276`, Python 3.12 ID `13849314179`.


## 7. Auditoría de continuidad y dirección PMD — 2026-11-12

Se contrastó de nuevo el estado de `main` y se corrigieron contradicciones de continuidad:

- La Release `v0.1.0` está publicada como Alpha/prerelease, con wheel, sdist y checksum; las notas anteriores que indicaban publicación pendiente son históricas y están supersedidas.
- La CI del commit `2c206dbc679ca6b77dded1f108192efff5ed442d` finalizó con éxito en cuatro jobs.
- La hoja de ruta activa de publicación se sustituye por `docs/roadmap.md`.
- La dirección PMD y las decisiones de estilos para IA se registran en `docs/pmd-design.md`.
- Se distingue PMD (autoría), IR (contrato runtime) y la ruta actual Markdown → IR → XMind.
- Se documenta Tema1: 10 temas, tabla de árbol en `Articulo`, celdas `Cabecera`/`cuerpo` con estilos distintos, marcadores y pérdida de información en Markdown.
- El catálogo semántico, las reglas de aplicación y la herencia por referencia al primer hijo son decisiones de diseño, no funciones implementadas.

Se actualizaron README, arquitectura, estado, prompt maestro, gramática, sistema y guía de estilos, catálogo de archivos y documentación de temas. No se modificaron código, esquema IR, parser, resolutor runtime ni pruebas.
