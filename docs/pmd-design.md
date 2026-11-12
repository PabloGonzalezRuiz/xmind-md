# Dirección de producto y diseño de PMD

**Fecha:** 2026-11-12. **Estado:** dirección y principios aceptados; sintaxis PMD 1.0.0 especificada en Fase 4; ejecución pendiente.

## 1. Problema y objetivo

La importación nativa de Markdown en XMind conserva principalmente texto y jerarquía. No expresa de forma suficiente estructuras, estilos, marcadores y detalles visuales de mapas de estudio; obliga a mucho formateo manual posterior.

El objetivo no es imitar esa importación, sino crear **PMD (Pableras Markdown)**: un lenguaje de autoría legible por personas y fácil de generar por IA, que permita describir un mapa con suficiente riqueza para que el programa construya un XMind prácticamente terminado.

PMD deberá expresar jerarquía, orden, roles semánticos, estructuras (incluidas tablas de árbol y celdas), referencias a estilos reutilizables, marcadores y excepciones locales. La sintaxis PMD 1.0.0 está aprobada y documentada en [pmd-language-spec.md](pmd-language-spec.md); su implementación debe minimizar las anotaciones manuales.

## 2. Flujo objetivo

```text
Markdown ordinario / documento de origen
                 |
                 v
        Interpretación mediante IA
       (estructura, semántica, contexto)
                 |
                 v
              PMD
  (contenido + estructura + roles + estilos)
                 |
                 v
        Parser y validador PMD
                 |
                 v
        IR neutral de ejecución
                 |
                 v
        Resolución determinista
                 |
                 v
           Adaptador XMind
                 |
                 v
              .xmind
                 |
                 v
        SVG visualmente fiel a XMind
```

- Markdown de origen aporta el contenido.
- La IA identifica estructura y significado y genera PMD consultando el catálogo y las reglas; no inventa contenido ni estilos.
- PMD expresa intención de autoría y no se acopla a detalles internos de XMind.
- IR sigue siendo el contrato neutral entre parser, resolución y adaptadores. PMD no es sinónimo de IR.
- El motor valida y resuelve estilos de forma determinista.
- El SVG generado debe ser lo más fiel posible a la apariencia original de XMind. No se exige igualdad byte a byte ni reproducción exacta de XML, atributos o IDs internos.

La ruta actualmente implementada sigue siendo Markdown → IR 1.0.0 → JSON/XMind. La ruta PMD/IA es la evolución objetivo y no debe anunciarse como implementada.

## 3. Biblioteca de estilos orientada a IA

Los estilos deben almacenarse en una biblioteca reutilizable, separada del contenido de cada mapa. El catálogo estructurado debe poder ser leído por el motor y suministrado a la IA. Cada estilo debe incluir, según proceda:

- Identificador estable.
- Descripción semántica: qué representa y cuándo se utiliza.
- Elementos destinatarios.
- Propiedades visuales neutrales.
- Restricciones, exclusiones y requisitos.
- Ejemplos de aplicación correcta e incorrecta.

El catálogo de autoría está definido en `catalog/style-catalog.json`, con contrato en `docs/style-catalog.md` y esquema independiente. No confundirlo con el YAML `style_sets`/`styles` que consume el resolutor IR 1.x; la integración entre ambos sigue pendiente.

## 4. Reglas de aplicación

Se combinarán dos familias:

- **Semánticas:** basadas en el significado/rol del contenido (artículo, apartado, excepción, definición, cabecera, celda, etc.).
- **Estructurales:** basadas en el contexto (tipo de estructura, relación padre-hijo, posición entre hermanos, nivel o tipo de celda).

La semántica será el criterio principal; la estructura será complementaria y podrá actuar como fallback. Los conflictos y precedencias deben ser explícitos y deterministas, nunca una elección arbitraria de la IA.

## 5. Herencia por referencia al primer hijo

Se conserva el principio propuesto por el usuario:

- El primer hijo puede actuar como referencia de formato predeterminado para sus hermanos.
- Los demás hijos adoptan ese formato si no declaran una excepción.
- Un hijo puede declarar un formato distinto; la excepción se respeta.
- El mecanismo se repite recursivamente en niveles inferiores.

Es especialmente útil en tablas de árbol, donde las celdas pueden tener formatos diferentes dentro de una misma estructura.

La política se especifica en `docs/style-catalog.md` y `docs/pmd-language-spec.md`: el primer hijo aporta su estilo efectivo, la herencia rellena propiedades ausentes, las excepciones son locales por propiedad y las filas de `tree_table` son grupos independientes. No confundirla con la herencia actual del conjunto de estilos por rama del IR.

## 6. Papel de la IA

La IA deberá analizar contenido, reconocer numeración y relaciones semánticas, inferir estructuras candidatas, seleccionar roles y estilos existentes y generar PMD válido. Debe señalar ambigüedades en vez de inventar datos. El motor valida PMD y resuelve las reglas; la IA no debe repetir colores o propiedades de bajo nivel cuando existe un estilo reutilizable.

La IA no será una dependencia obligatoria del núcleo Python: el conversor podrá procesar PMD creado externamente.

## 7. Referencia Tema1

`themes/Tema1/` contiene `content.json`, `Tema1.svg` y `Tema1.md`, exportaciones de referencia; no contiene un `.xmind` original versionado. El análisis detallado y la tabla completa de nodos están en [reference-analysis-tema1.md](reference-analysis-tema1.md).

Hallazgos confirmados: 10 temas; nueve tienen estilo explícito y `ListaBloque` no declara uno en su objeto. `Articulo` usa `structureClass=org.xmind.ui.treetable.toptitle`; sus hijos `Cabecera` y `cuerpo` comparten `shape-class=org.xmind.internal.topicShape.treeTableCell`, pero tienen rellenos distintos (`#EEEEEEFF` y `#f6a04d33`). `cuerpo` contiene propiedades de borde con valor `inherited`. `Titulo` lleva `flag-red`; `Articulo`, `flag-red` y `task-oct`.

El SVG relaciona los 10 títulos con los IDs del JSON mediante `data-view-id=topic-title:<id>`; utiliza `foreignObject` para los títulos. El Markdown conserva principalmente texto y jerarquía, pero pierde estructura de tabla, distinción de celdas, estilos y marcadores.

Esta referencia no demuestra herencia nativa del primer hijo hacia los demás. La regla de herencia por primer hijo es una decisión de autoría PMD futura y debe distinguirse de los valores `inherited` y de los perfiles generales del tema XMind.

## 8. Decisiones aceptadas

1. PMD debe reducir drásticamente el formateo manual.
2. PMD será legible y apto para generación mediante IA.
3. La IA consultará catálogo, reglas y ejemplos.
4. Se combinarán reglas semánticas y estructurales, con prioridad semántica.
5. Se conservará la herencia por referencia al primer hijo, con excepciones y recursividad.
6. La resolución será determinista.
7. El SVG buscará fidelidad visual, no identidad XML.

## 9. Especificación PMD aprobada en Fase 4

La gramática normativa PMD 1.0.0 está en [`pmd-language-spec.md`](pmd-language-spec.md). Define front matter versionado, encabezados como única fuente de temas, directivas `:::pmd`, roles, referencias visuales, overrides, `tree_table`, notas, anotaciones, referencias globales, IDs, escapes, diagnósticos y correspondencia con IR 1.1.0.

Los ejemplos de referencia son [`constitucion-estructura.pmd.md`](../examples/pmd/constitucion-estructura.pmd.md) y [`tabla-arbol-tema1.pmd.md`](../examples/pmd/tabla-arbol-tema1.pmd.md). La especificación está aprobada como contrato de lenguaje; no existe todavía parser ni ejecución runtime.

## 10. Continuidad

- [Especificación normativa PMD 1.0.0](pmd-language-spec.md)
- [Hoja de ruta](roadmap.md)
- [Arquitectura](architecture.md)
- [Sistema de estilos](style-system.md)
- [Gramática actual](grammar.md)
- [Prompt maestro](ai-reconstruction-prompt.md)
- [Referencia Tema1](../themes/Tema1/README.md)

## 11. Contrato del catálogo aprobado en Fase 3

El catálogo PMD 1.0.0 está definido en [`catalog/style-catalog.json`](../catalog/style-catalog.json), con esquema [`style-catalog.schema.json`](style-catalog.schema.json), guía [`style-catalog.md`](style-catalog.md) y casos [`style-resolution-cases.md`](style-resolution-cases.md).

Se mantienen separados rol semántico, estructura, estilo visual y anotación. La prioridad de reglas semánticas es superior a la de reglas estructurales; estas últimas son complementarias y sirven de fallback. La herencia por primer hijo copia propiedades efectivas ausentes, con grupos separados por fila en `tree_table`, resolución recursiva top-down y excepciones por propiedad.

Este catálogo es una especificación de autoría y no sustituye ni modifica `config/styles.yaml` o el resolutor IR 1.x. Su implementación queda fuera de la Fase 3.
