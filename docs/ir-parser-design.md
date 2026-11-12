# Diseño de parsing directo al IR

**Estado:** diseño técnico de la tarea 1.2; pendiente de implementación y validación.
**Contrato de destino:** IR 1.0.0, sin cambios de esquema en esta tarea.

## 1. Problema observado

El parser actual combina tres responsabilidades:

1. Reconoce sintaxis Markdown, YAML, directivas y bloques.
2. Construye un árbol de dominio legacy (model.MindMap / model.Topic).
3. Conserva representaciones auxiliares legacy de contenido, recursos y anotaciones.

Después, ir_parser.py recorre ese árbol y construye una segunda representación de dominio IR. La conversión no es una simple serialización: transforma bloques, normaliza enlaces inline, crea IDs de etiquetas/marcadores/notas/assets, ubica relaciones y otras entidades dentro de Sheet, y valida el documento.

La ruta objetivo debe eliminar el árbol legacy como paso intermedio sin mezclar parsing, reglas de negocio del IR y serialización XMind.

## 2. Decisión de diseño

Separar el flujo en cuatro responsabilidades:

    Markdown
       |
       v
    parser.py / syntax.py
       |
       v
    AST sintáctico temporal
       |
       v
    ir_builder.py
       |
       v
    IR 1.0.0
       |
       +--> resolución de estilos / adaptadores / CLI

La API de compatibilidad utiliza el mismo análisis sintáctico, pero proyecta el AST a la estructura antigua:

    parse_markdown() / parse_file()
       |
       v
    parser.py → DocumentSyntax
       |
       v
    legacy_adapter.py
       |
       v
    model.MindMap / model.Topic

Esta ruta solo se ejecuta cuando un consumidor invoca explícitamente la API antigua. No participa en la ruta canónica IR ni se utiliza por CLI o adaptadores. Se mantiene separada porque el contrato legacy conserva datos de autoría (por ejemplo, nivel exacto del encabezado y texto Markdown original) que el IR no pretende almacenar.

## 3. AST sintáctico temporal

El AST representa lo que el documento dice y cómo aparece, no el modelo de ejecución final.

Tipos conceptuales:

- DocumentSyntax: front matter normalizado, ruta de origen, raíz sintáctica y directivas globales.
- TopicSyntax: texto del encabezado, nivel, propiedades YAML pendientes aplicadas, posición de origen, bloques y temas hijos.
- BlockSyntax: tipo de construcción reconocida, datos sintácticos (runs, filas, elementos, texto literal) y rango de origen.
- GlobalDirectiveSyntax: tipo, payload normalizado y ubicación de origen.

Invariantes:

- El AST no importa ni instancia entidades de ir/ ni clases de model.py.
- No mantiene campos duplicados para compatibilidad, como content y content_blocks.
- No calcula estilos resueltos ni traduce propiedades XMind.
- Conserva orden, IDs explícitos, referencias, texto, rangos y datos necesarios para una conversión sin pérdida.
- Los datos YAML ya normalizados a tipos JSON y validados sintácticamente no se reinterpretan en el builder.
- El AST es temporal y no forma parte de la API pública ni del contrato serializado.

No se introducirá una jerarquía de nodos AST compleja si dataclasses pequeñas y tipos discriminados bastan para el subconjunto gramatical actual.

## 4. Constructor IR

ir_builder.py será responsable de transformar el AST en entidades canónicas:

- Crear MindMap, Sheet, Topic y SheetLayout.
- Convertir bloques sintácticos a ContentBlock.
- Convertir etiquetas, marcadores, tareas y notas a Annotation.
- Crear Asset y referencias de recursos con IDs deterministas.
- Convertir enlaces y referencias internas.
- Crear relaciones, límites y resúmenes en Sheet.
- Conservar source.file, line_start y line_end.
- Aplicar exactamente las reglas actuales de generación de IDs.
- Ejecutar validate_mind_map() al finalizar.

El builder no analizará texto Markdown ni YAML. Tampoco resolverá estilos ni generará JSON XMind.

## 5. API y módulos

Diseño objetivo de módulos:

| Módulo | Responsabilidad |
|---|---|
| syntax.py | Tipos AST sintácticos y, si conviene, utilidades de procedencia. |
| parser.py | Gramática actual; produce DocumentSyntax. Las funciones antiguas delegan en el adaptador legacy. |
| ir_builder.py | AST → IR, con constructores deterministas. |
| ir_parser.py | Fachada pública parse_markdown_ir() y parse_file_ir(); orquesta parser + builder. |
| legacy_adapter.py | AST → model.MindMap / model.Topic para compatibilidad temporal. |
| ir/entities.py | Entidades canónicas, sin dependencia de parser ni adaptadores. |

Para evitar importaciones circulares, parser.py no importa ir_parser.py. ir_parser.py importa parse_markdown_syntax(); el parser solo importa legacy_adapter dentro de las funciones antiguas. El adaptador consume DocumentSyntax y construye model.MindMap / model.Topic sin intervenir en la ruta IR.

Las funciones parse_markdown_ir() y parse_file_ir() son la única ruta canónica. parse_markdown() y parse_file() reutilizan el mismo AST y lo proyectan al modelo antiguo.

## 6. Compatibilidad y fidelidad

La migración no cambia la gramática ni el contrato IR 1.0.0. Se deben preservar:

- Mensajes y condiciones de error relevantes de la gramática actual.
- IDs explícitos y deterministas.
- Orden y jerarquía de temas y bloques.
- Estilos, conjuntos, overrides, anotaciones y enlaces.
- Conversión de enlaces inline topic: y enlaces web.
- Assets deduplicados por la regla actual y referencias de recursos.
- Relaciones, límites y resúmenes y sus validaciones.
- Metadatos y trazabilidad de fuente.
- Semántica actual de notas y contenido de listas/tablas.

La adaptación IR → legacy puede reconstruir los campos legacy derivados cuando exista una equivalencia definida. Si una característica del IR no puede representarse fielmente en el modelo antiguo, el adaptador debe documentar esa limitación y fallar explícitamente antes que descartarla silenciosamente.

## 7. Secuencia de implementación

1. Crear AST sintáctico y pruebas unitarias de sus tipos/estructura.
2. Separar el reconocimiento sintáctico de la construcción de entidades legacy.
3. Implementar el builder IR reutilizando las reglas actuales de conversión, sin duplicar lógica.
4. Cambiar parse_markdown_ir() para consumir AST directamente y retirar _convert() / _topic() del camino canónico.
5. Implementar el adaptador AST → legacy y hacer que las funciones antiguas reutilicen el análisis sintáctico común.
6. Añadir pruebas de equivalencia de ida y vuelta para el contrato legacy observable y pruebas de que la ruta IR no instancia model.MindMap ni model.Topic.
7. Migrar el resolutor legacy de estilos o encapsularlo detrás del adaptador; retirar dependencias internas de model.py cuando las pruebas lo permitan.
8. Ejecutar suite completa, Ruff, build/install y CI en Python 3.10–3.12.

Cada paso se realizará en commits pequeños. No se retirará model.py ni se cambiará una API pública sin evidencia de compatibilidad y actualización de documentación.

## 8. Criterios de aceptación

- parse_markdown_ir() y parse_file_ir() producen IR sin construir objetos del modelo legacy.
- No existe conversión legacy → IR en la ruta canónica.
- El AST no es un modelo de dominio alternativo ni persiste en el resultado.
- Las APIs legacy conservan su forma y comportamiento documentados mediante un adaptador AST → legacy aislado.
- El fixture de caracterización y las pruebas de parsing/IR conservan IDs, contenido, orden, referencias y procedencia.
- Las pruebas negativas mantienen la validación de YAML, directivas, IDs y referencias.
- La CLI y los adaptadores siguen consumiendo IR directamente.
- No se modifica el esquema ni la versión IR 1.0.0.
- CI completa verde en Python 3.10, 3.11 y 3.12, además de build e instalación de wheel/sdist.

## 9. Riesgos y puntos de atención

- Representaciones inline: el parser produce runs de sintaxis; el builder debe reproducir exactamente la conversión actual a runs IR.
- Imágenes: hoy se reconocen como bloques y también se conservan en recursos legacy; el IR debe indexar assets una sola vez y mantener todas las referencias.
- Notas: hoy se analizan después con _inline_runs(); la nueva ruta debe conservar formato y generación de ID.
- Validación de referencias: las relaciones se validan al terminar de construir el árbol; los enlaces internos se validan en la validación IR. No adelantar validaciones si cambia el error observable sin justificarlo.
- Estilos legacy: styles.py todavía importa model.Topic; su retirada es una parte separada de la consolidación y no debe bloquear el primer corte del parser.
- Compatibilidad externa: no se conocen consumidores externos. Mantener temporalmente las funciones legacy es la opción conservadora. La ruta antigua no se fuerza a pasar por IR cuando ello perdería información de autoría que el modelo legacy sí conservaba.

## 10. Estado

Este documento define el diseño; no afirma que AST, builder o adaptador inverso estén implementados. La auditoría de hechos observados sigue en ir-consolidation-audit.md, y el estado de ejecución en roadmap.md.
