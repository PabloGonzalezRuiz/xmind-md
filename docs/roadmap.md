# Hoja de ruta XMind MD / PMD

**Actualizada:** 2026-11-12. **Rama:** `main`. **Referencia de auditoría:** informe [Tema1](reference-analysis-tema1.md); verificar HEAD antes de cada nueva tarea.

Esta es la hoja de ruta vigente. El histórico de tareas Alpha se conserva en `development-status.md`; no debe confundirse con el trabajo futuro.

## Estado de partida

- IR 1.0.0, parser Markdown, resolución de estilos, adaptadores y CLI implementados.
- Ruta actual: Markdown → IR → JSON/XMind.
- Adaptador XMind parcial; pérdidas y rechazos en `xmind-adapter.md`.
- Release [v0.1.0](https://github.com/PabloGonzalezRuiz/xmind-md/releases/tag/v0.1.0) publicada el 2026-11-11 como Alpha/prerelease; incluye wheel, sdist y `SHA256SUMS.txt`.
- CI del commit auditado: [43206029166](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/43206029166), cuatro jobs `success` (tests Python 3.10/3.11/3.12 y build/install de distribuciones).
- Análisis XMind: [43058441322](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/43058441322), `success` para el commit `00f05cf`.

## Fase 1 — Analizar referencias reales XMind

**Estado: COMPLETADA para la referencia Tema1.**

- [x] Incorporar `themes/Tema1/content.json`, `Tema1.svg` y `Tema1.md`.
- [x] Confirmar que Markdown conserva principalmente texto y jerarquía.
- [x] Identificar `Articulo` como tabla de árbol y `Cabecera`/`cuerpo` como celdas.
- [x] Documentar la jerarquía completa, estilos explícitos, marcadores y diferencias entre nodos.
- [x] Relacionar los 10 nodos JSON con los títulos SVG mediante `data-view-id` y documentar las pérdidas de Markdown.
- [x] Extraer requisitos semánticos/estructurales sin convertir detalles internos de XMind en sintaxis PMD obligatoria.

**Cierre:** cumplido para Tema1. El informe reproducible está en [reference-analysis-tema1.md](reference-analysis-tema1.md). No se dispone del `.xmind` original y el análisis no pretende cubrir todas las variantes de tablas.

## Fase 2 — Especificar biblioteca de estilos y reglas

**Estado: dirección aceptada; especificación pendiente.**

- Definir catálogo reutilizable con identificador, descripción semántica, destinatarios, propiedades, restricciones y ejemplos.
- Diseñar reglas semánticas (criterio principal) y estructurales (complemento).
- Formalizar herencia por referencia al primer hijo, excepciones y recursividad.
- Definir defaults, fallback, overrides y precedencia por propiedad.
- Separar datos estructurados para máquina de documentación para personas/IA.
- Mantener separado el catálogo futuro del YAML runtime actual.

**Cierre:** especificación, ejemplos y casos de prueba conceptuales; no implica implementación.

## Fase 3 — Diseñar sintaxis PMD

Definir documento, relación con Markdown, sintaxis mínima de roles, estructuras, tablas de árbol, estilos y excepciones; escapes, IDs, referencias y errores. Priorizar legibilidad y poca anotación manual.

**Cierre:** gramática y ejemplos inequívocos que puedan escribir una persona o generar una IA.

## Fase 4 — Definir PMD → IR y validación

Reutilizar IR donde baste; identificar brechas antes de modificarlo; proponer versionado/migración si hay cambios incompatibles; validar referencias, estructuras y estilos.

**Cierre:** mapeo, esquema/validación y ejemplos PMD convertidos a IR.

## Fase 5 — Conversión Markdown → PMD mediante IA

Preparar instrucciones con catálogo/reglas/ejemplos; reconocer semántica y estructura; evitar invención; identificar ambigüedades; crear corpus Markdown/PMD esperado y evaluación reproducible.

**Cierre:** PMD válido en documentos reales y reducción demostrable del formateo manual.

## Fase 6 — Generación XMind y fidelidad visual

Priorizar estructuras de estudio/legislación; implementar mapeos requeridos; comparar con referencias reales; generar SVG lo más fiel posible a la apariencia original de XMind. No exigir identidad XML, atributos o IDs internos. Documentar límites.

**Cierre:** referencias reconstruidas con fidelidad visual suficiente y limitaciones explícitas.

## Fase 7 — Integración, CLI, pruebas y documentación

Integrar PMD sin romper Markdown→IR; pruebas unitarias/integración/regresión; CI; CLI y guía; comprobar Windows por ser entorno de uso.

**Cierre:** flujo reproducible Markdown → IA → PMD → XMind, CI verde y ejemplos verificables.

## Reglas de ejecución

1. Auditar GitHub antes de cada cambio.
2. Trabajar por tareas pequeñas y autorizadas.
3. Separar implementado, decidido y pendiente.
4. Actualizar este documento, `development-status.md` y el prompt maestro al cerrar tareas/decisiones.
5. No modificar código durante tareas de documentación/diseño sin autorización.
6. No avanzar de fase sin cumplir criterios, salvo autorización expresa.

## Siguiente paso

La Fase 1 está cerrada para la referencia Tema1. El siguiente trabajo es la **Fase 2: especificación de la biblioteca de estilos, reglas semánticas/estructurales y herencia**. Antes de diseñar la sintaxis PMD, hay que concretar el esquema que la IA consultará, los metadatos de cada estilo y la resolución determinista. Esta fase requiere autorización expresa del usuario. No implementar todavía parser PMD ni catálogo runtime.
