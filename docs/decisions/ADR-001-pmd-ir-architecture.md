# ADR-001: Arquitectura objetivo de PMD e IR

- **Estado:** Aceptada
- **Fecha:** 2026-11-12
- **Ámbito:** arquitectura, autoría PMD, modelo intermedio, estilos y generación XMind
- **Sustituye:** ninguna decisión de contrato IR 1.0.0; define la dirección de evolución

## Contexto

La situación inicial era Markdown → modelo legacy → IR 1.0.0. En la rama de trabajo, esa duplicidad ya se ha eliminado de la ruta canónica: parser.py produce AST temporal, ir_builder.py construye directamente el IR e ir_parser.py es una fachada. Las API antiguas y la resolución legacy se mantienen aisladas en módulos de compatibilidad porque no se conocen consumidores externos.

Además, el IR actual no expresa explícitamente roles semánticos de los temas ni estructuras compuestas como la tabla de árbol observada en `themes/Tema1/`. La tabla Markdown existente no representa esa estructura. El catálogo de estilos actual resuelve propiedades visuales, pero todavía no constituye una biblioteca semántica diseñada para que una IA seleccione estilos y reglas.

## Decisiones

### D1. PMD será un lenguaje de autoría separado del IR

PMD expresará contenido, jerarquía, roles semánticos, estructuras, referencias a estilos y excepciones. No expondrá claves privadas de XMind, IDs internos del serializador ni propiedades de bajo nivel cuando exista una abstracción semántica adecuada.

La IA podrá convertir documentos ordinarios a PMD consultando catálogo, reglas y ejemplos. El núcleo Python no dependerá de un proveedor de IA.

### D2. El IR será el único modelo de dominio de ejecución

El parser podrá utilizar nodos sintácticos/AST temporales, pero no construirá un segundo modelo de dominio que después haya que convertir al IR. La migración será gradual: se caracterizará el comportamiento público, se construirá IR directamente desde AST y las rutas antiguas se aislarán como adaptadores. No se retirará model.py ni se romperán las API legacy hasta contar con una política de compatibilidad y evidencia sobre consumidores externos.

### D3. El IR será neutral y tendrá semántica explícita

Se distinguirán:
- tipo de entidad/topic (por ejemplo, attached, detached, callout o summary);
- rol semántico (por ejemplo, article, exception, definition, header_cell o body_cell);
- estructura compuesta (por ejemplo, tree_table);
- propiedades de presentación neutrales.

No se introducirán en el IR nombres internos de XMind como `org.xmind.ui.treetable.toptitle` ni `org.xmind.internal.topicShape.treeTableCell`. El adaptador traducirá los conceptos neutrales al perfil XMind soportado.

### D4. Tabla Markdown y tabla de árbol serán estructuras distintas

La tabla Markdown seguirá siendo una secuencia de filas y celdas de contenido. La tabla de árbol será una estructura compuesta explícita, con roles y relaciones de fila/celda adecuados a su semántica. No se inferirá una tabla de árbol por el mero hecho de que un tema tenga hijos.

### D5. Catálogo semántico y estilos visuales estarán separados

La biblioteca futura contendrá metadatos legibles por IA: identificador, significado, cuándo usar/no usar, destinatarios, ejemplos, restricciones y referencia a reglas visuales. La representación visual mantendrá propiedades neutrales y mapeos específicos del adaptador. El esquema del catálogo se diseñará antes de implementarlo.

### D6. La resolución será determinista y auditable

La resolución combinará reglas semánticas (prioritarias), reglas estructurales (complementarias), defaults, estilos nombrados, herencia y overrides. La procedencia por propiedad deberá poder explicar qué regla produjo el valor final.

Se mantendrán diferenciados:
- propiedad ausente;
- valor explícito;
- valor literal especial `inherited`;
- herencia de conjuntos de estilos por descendencia ya existente;
- futura herencia PMD por referencia al primer hijo;
- comportamiento nativo de herencia del motor XMind.

La herencia por primer hijo será una regla PMD de autoría, recursiva y con excepciones explícitas; no se afirmará que sea una característica nativa de XMind.

### D7. Adaptadores separados y dependencias externas opcionales

Se conservarán adaptadores separados. Los proyectos oficiales `xmindmark`, `xmind-generator`, `xmind-sdk-js` y `xmind-model` se usarán como referencias y fuentes de pruebas, no como dependencias runtime obligatorias salvo ADR posterior.

El adaptador XMind implementará incrementalmente el perfil requerido y rechazará explícitamente lo no soportado. No se copiarán perfiles ZIP históricos sin validación en XMind Desktop.

### D8. Compatibilidad y versionado explícitos

IR 1.0.0 no se modificará silenciosamente. Los cambios compatibles se evaluarán para una versión menor; los cambios incompatibles exigirán versión mayor y migración documentada. Cada fase incluirá pruebas de regresión y sincronización del esquema, ejemplos y documentación.

### D9. SVG orientado a fidelidad visual

El SVG generado debe ser lo más fiel posible a la apariencia de referencia XMind. No se exige identidad XML, IDs internos ni igualdad de atributos. Las comparaciones visuales/estructurales son herramientas de validación, no contratos de identidad.

### D10. Compatibilidad legacy aislada

Las funciones parse_markdown() / parse_file() conservan su resultado antiguo mediante legacy_adapter.py, que proyecta el AST sintáctico al modelo legacy. Se elige AST → legacy en vez de IR → legacy porque el modelo antiguo expone datos de autoría que el IR no conserva como contrato (por ejemplo, nivel exacto de encabezado y texto Markdown original).

La resolución de estilos para objetos legacy se encapsula en legacy_styles.py. styles.py es la fachada pública: la ruta IR usa resolve_ir_styles(); solo los objetos antiguos se derivan al módulo de compatibilidad. model.py se conserva por ahora, sin prometer retirada ni deprecación, porque no se conocen consumidores externos. Ningún componente de la ruta canónica parser → builder → IR → CLI/adaptadores depende de model.py.

## Consecuencias

- La sintaxis PMD queda bloqueada hasta que las necesidades semánticas/estructurales del IR estén suficientemente definidas.
- La migración del parser es prioritaria y deberá preservar el comportamiento actual mediante pruebas de caracterización.
- El IR requerirá evolución para roles semánticos y estructuras compuestas.
- El sistema de estilos actual se conservará mientras se diseña el catálogo nuevo; no se reemplazará a ciegas.
- La compatibilidad con XMind Desktop se declarará por características y versiones probadas.
- Se mantendrá operativo el flujo Markdown → IR → JSON/XMind durante la transición.

## Orden de implementación

1. Consolidar el modelo y eliminar gradualmente el puente de dominio legacy.
2. Ampliar IR con roles semánticos y estructuras compuestas.
3. Especificar el catálogo semántico/visual y el algoritmo de resolución.
4. Especificar y después implementar PMD.
5. Ampliar el adaptador XMind y validar SVG/fixtures.
6. Integrar, documentar y publicar con regresión completa.

## Criterios para revisar esta decisión

Revisar este ADR si la consolidación impide conservar compatibilidad razonable, si aparece una especificación normativa XMind que requiera otro límite de abstracción, o si las pruebas en XMind Desktop demuestran que el modelo neutral propuesto no puede representar una estructura necesaria.
