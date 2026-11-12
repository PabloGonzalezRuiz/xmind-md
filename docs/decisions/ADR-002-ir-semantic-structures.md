# ADR-002: Evolución semántica y estructuras compuestas del IR

- **Estado:** Aceptada e implementada en la Fase 2 (CI 43246986236)
- **Fecha:** 2026-11-12
- **Ámbito:** contrato IR, roles semánticos y estructuras compuestas
- **Relacionada con:** ADR-001

## Contexto

IR 1.0.0 representa los temas jerárquicos mediante Topic.kind, pero no ofrece un campo independiente para el significado documental de cada tema. Además, Topic.layout.structure_class puede transportar directamente nombres internos de XMind. La tabla Markdown (ContentBlock type=table) no representa la tabla de árbol observada en themes/Tema1/content.json.

En Tema1, el tema Articulo contiene dos temas hijos (Cabecera y cuerpo) con estilos diferentes. El padre tiene la clase XMind org.xmind.ui.treetable.toptitle; las celdas hijas tienen org.xmind.internal.topicShape.treeTableCell. Esta evidencia justifica modelar la estructura de forma explícita, pero no justifica copiar las clases XMind al IR ni inferir automáticamente los roles a partir del estilo.

## Decisiones

### D1. Separar tipo de tema y rol semántico

- Topic.kind conserva su función actual: tipo de representación/relación del tema (attached, detached, callout, summary).
- Se añade Topic.semantic_role, opcional y textual, para describir el significado documental o funcional del tema.
- Ejemplos: legal.article, legal.exception, table.header_cell, table.body_cell.
- El vocabulario queda abierto; el futuro catálogo de estilos documentará los roles conocidos, su significado y sus restricciones. No se fija ahora un enum cerrado.

### D2. Añadir una estructura compuesta neutral al tema

Se añade Topic.structure, opcional y discriminada por type. La primera estructura soportada es tree_table.

Forma JSON canónica (fragmento):

    {
      "structure": {
        "type": "tree_table",
        "rows": [
          {
            "cells": [
              {"topic_id": "topic_header"},
              {"topic_id": "topic_body"}
            ]
          }
        ]
      }
    }

La estructura pertenece al tema contenedor. Las filas y celdas son descriptores de orden y agrupación; no duplican el contenido ni crean nuevos temas. Cada celda referencia un tema hijo directo por topic_id. El título, contenido, anotaciones, recursos, estilo y posibles subtemas de la celda permanecen en la entidad Topic referenciada.

### D3. Roles de celda y contenido

El rol de una celda se expresa mediante semantic_role del tema referenciado (por ejemplo, table.header_cell o table.body_cell). No se crea una segunda fuente de verdad en el descriptor de celda.

El contenido de la celda se compone del título y bloques de contenido del tema referenciado, más sus anotaciones y recursos según las reglas de presentación. La estructura no contiene copias de ese contenido.

### D4. Orden, integridad y anidamiento

- El orden de rows determina el orden de las filas.
- El orden de cells determina el orden de las celdas dentro de cada fila.
- Cada hijo directo del tema contenedor debe aparecer exactamente una vez en la tabla.
- No se permiten referencias a temas que no sean hijos directos, referencias repetidas ni hijos omitidos.
- Cada fila debe contener al menos una celda.
- Una celda puede contener otra estructura compuesta porque el Topic referenciado puede declarar su propio structure. Así se permite anidamiento sin duplicar árboles.
- En esta primera versión no se modelan celdas combinadas (rowspan / colspan), coordenadas absolutas ni celdas sin Topic propio. Se añadirán solo ante casos de referencia que lo requieran.

### D5. Neutralidad respecto a XMind

El IR 1.1.0 no admite claves internas XMind en Topic.structure. El adaptador será responsable de mapear tree_table y sus roles al perfil XMind probado.

La propiedad histórica layout.structure_class queda como compatibilidad de IR 1.0.0; no se utilizará en nuevos documentos 1.1.0. La migración no inferirá roles ni estructura a partir de clases XMind sin evidencia suficiente. Los valores históricos que no puedan transformarse sin pérdida se preservarán como extensiones namespaced y requerirán migración explícita.

### D6. Ausencia, valor explícito y literal inherited

- Una propiedad ausente no declara valor y permite que actúe la cascada correspondiente.
- Un valor explícito, incluido el texto literal "inherited", es un valor declarado y debe conservarse literalmente.
- null mantiene su significado actual de reinicio explícito en la resolución de estilos; no equivale a ausencia.
- La palabra inherited no se convierte en una instrucción de herencia del IR ni en una señal para copiar el estilo del padre o del primer hermano.
- La herencia de style_set por descendencia sigue siendo independiente.
- La futura regla PMD de herencia visual desde el primer hijo será una regla del sistema de estilos/catálogo, con procedencia y excepciones; no se implementa mediante el literal inherited.

### D7. Versionado

Los campos nuevos son opcionales y aditivos, por lo que la evolución se especifica como IR 1.1.0. Los documentos IR 1.0.0 seguirán siendo legibles y validables. Los documentos que utilicen semantic_role o structure deberán declarar ir_version: "1.1.0".

La validación y serialización mantendrán compatibilidad con 1.0.0. La migración 1.0.0 → 1.1.0 será explícita y no inventará roles ni estructuras. No se cambiará el valor por defecto de constructores existentes de forma que cambie silenciosamente la versión de los documentos generados.

## Consecuencias

- El modelo Python y el esquema JSON incorporarán los campos opcionales y los tipos de fila/celda.
- El validador comprobará referencias, orden, pertenencia de celdas a hijos directos y cobertura exacta de hijos.
- Se mantendrán fixtures positivos y negativos para 1.0.0 y 1.1.0.
- El adaptador XMind no se ampliará en esta fase; su implementación corresponde a la Fase 7.
- El catálogo de roles y las reglas de estilos se desarrollarán en la Fase 3.

## Criterios de revisión

Revisar esta decisión si nuevas referencias XMind muestran tablas de árbol que requieran celdas sin tema, spans, jerarquías de filas independientes o una relación distinta entre tema contenedor y celdas.
