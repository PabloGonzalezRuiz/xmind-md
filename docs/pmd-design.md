# Dirección de producto y diseño de PMD

**Fecha:** 2026-11-12. **Estado:** dirección y principios aceptados; sintaxis y ejecución pendientes.

## 1. Problema y objetivo

La importación nativa de Markdown en XMind conserva principalmente texto y jerarquía. No expresa de forma suficiente estructuras, estilos, marcadores y detalles visuales de mapas de estudio; obliga a mucho formateo manual posterior.

El objetivo no es imitar esa importación, sino crear **PMD (Pableras Markdown)**: un lenguaje de autoría legible por personas y fácil de generar por IA, que permita describir un mapa con suficiente riqueza para que el programa construya un XMind prácticamente terminado.

PMD deberá expresar jerarquía, orden, roles semánticos, estructuras (incluidas tablas de árbol y celdas), referencias a estilos reutilizables, marcadores y excepciones locales. La sintaxis definitiva todavía no está aprobada y debe minimizar las anotaciones manuales.

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

Los datos estructurados pueden almacenarse en YAML/JSON y acompañarse de documentación Markdown. El formato exacto y el esquema definitivo quedan pendientes. No confundir este catálogo futuro con el YAML `style_sets`/`styles` que ya consume el resolutor IR 1.0.0.

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

Queda pendiente precisar qué ocurre si el primer hijo carece de estilo explícito, cómo se fusionan propiedades parciales y cómo se combinan esta regla, las reglas semánticas, los defaults y los overrides. No confundirla con la herencia actual del conjunto de estilos por rama del IR.

## 6. Papel de la IA

La IA deberá analizar contenido, reconocer numeración y relaciones semánticas, inferir estructuras candidatas, seleccionar roles y estilos existentes y generar PMD válido. Debe señalar ambigüedades en vez de inventar datos. El motor valida PMD y resuelve las reglas; la IA no debe repetir colores o propiedades de bajo nivel cuando existe un estilo reutilizable.

La IA no será una dependencia obligatoria del núcleo Python: el conversor podrá procesar PMD creado externamente.

## 7. Referencia Tema1

`themes/Tema1/` contiene `content.json`, `Tema1.svg` y `Tema1.md`, exportaciones de referencia; no contiene un `.xmind` original versionado.

El JSON contiene 10 temas. `Articulo` usa `org.xmind.ui.treetable.toptitle`; sus hijos `Cabecera` y `cuerpo` usan `org.xmind.internal.topicShape.treeTableCell`, con estilos distintos. `Titulo` lleva `flag-red`; `Articulo`, `flag-red` y `task-oct`. El Markdown conserva principalmente títulos y jerarquía, pero pierde estructura de tabla, estilos y marcadores.

## 8. Decisiones aceptadas

1. PMD debe reducir drásticamente el formateo manual.
2. PMD será legible y apto para generación mediante IA.
3. La IA consultará catálogo, reglas y ejemplos.
4. Se combinarán reglas semánticas y estructurales, con prioridad semántica.
5. Se conservará la herencia por referencia al primer hijo, con excepciones y recursividad.
6. La resolución será determinista.
7. El SVG buscará fidelidad visual, no identidad XML.

## 9. Cuestiones abiertas

Sintaxis PMD; extensión; esquema y estructura de archivos del catálogo; vocabulario semántico; algoritmo completo de herencia/fallback/precedencia; representación de tablas de árbol; mapeo PMD→IR y posible versionado del IR; evaluación de inferencias de IA; alcance del generador SVG.

## 10. Continuidad

- [Hoja de ruta](roadmap.md)
- [Arquitectura](architecture.md)
- [Sistema de estilos](style-system.md)
- [Gramática actual](grammar.md)
- [Prompt maestro](ai-reconstruction-prompt.md)
- [Referencia Tema1](../themes/Tema1/README.md)
