# Diseño del contrato IR 1.1.0

**Estado:** diseño aprobado para implementación en Fase 2  
**Versión base:** IR 1.0.0  
**Versión objetivo:** IR 1.1.0  
**Decisión:** ADR-002

## 1. Objetivos

1. Separar la clase de representación del tema de su significado documental.
2. Representar explícitamente una tabla de árbol sin copiar el modelo privado de XMind.
3. Conservar el árbol de temas como única fuente de verdad para títulos y contenido.
4. Definir referencias y orden verificables por el validador.
5. Mantener legibles los documentos IR 1.0.0.

## 2. Topic.kind y Topic.semantic_role

kind mantiene su significado actual y no se reutiliza para etiquetar artículos, excepciones o celdas.

semantic_role es un identificador textual opcional, abierto y neutral. Se recomienda una forma namespaced:

| Rol | Uso |
|---|---|
| legal.article | Tema cuyo significado es un artículo jurídico |
| legal.exception | Excepción normativa |
| legal.definition | Definición |
| table.header_cell | Tema que actúa como celda de cabecera |
| table.body_cell | Tema que actúa como celda de contenido |

No se fija un enum cerrado: la biblioteca de estilos de la Fase 3 será la fuente de conocimiento del vocabulario reconocido. El IR conserva roles desconocidos para permitir extensibilidad; la validación solo exige que el valor sea texto no vacío.

## 3. Topic.structure

Es un descriptor opcional de organización compuesta del tema. En IR 1.1.0 el primer tipo es tree_table.

Ejemplo JSON (fragmento):

    {
      "id": "topic_article",
      "title": "Artículo",
      "kind": "attached",
      "semantic_role": "legal.article",
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
      },
      "children": [
        {
          "id": "topic_header",
          "title": "Cabecera",
          "semantic_role": "table.header_cell"
        },
        {
          "id": "topic_body",
          "title": "cuerpo",
          "semantic_role": "table.body_cell"
        }
      ]
    }

El fragmento es ilustrativo; los temas completos mantienen los campos obligatorios del contrato.

### 3.1 Filas y celdas

- rows es una lista ordenada.
- Cada fila contiene una lista ordenada cells.
- Cada celda contiene topic_id, referencia al ID de un hijo directo del tema que declara la estructura.
- La posición en las listas expresa el orden; no se duplica con índices numéricos.
- El rol de celda está en semantic_role del tema referenciado, no en el descriptor de celda.
- Cada hijo directo debe aparecer una sola vez y todas las celdas deben apuntar a hijos directos existentes.

### 3.2 Fuente única de contenido

El descriptor de estructura no copia título ni contenido. La celda toma el título, los bloques, las anotaciones, los recursos y el estilo del Topic referenciado. Esto evita divergencias entre una tabla y el árbol de temas.

### 3.3 Anidamiento

Una celda puede ser a su vez contenedor de una estructura compuesta: su Topic puede declarar su propio structure y sus propios hijos. El anidamiento sigue el árbol y no crea referencias recursivas adicionales.

### 3.4 Límites de la primera implementación

No se incluyen todavía celdas sin Topic propio, celdas combinadas, rowspan, colspan, coordenadas explícitas ni una jerarquía de filas independiente. No hay evidencia en Tema1 que obligue a incluirlos y se evita sobreespecificar antes de estudiar más ejemplos.

## 4. Neutralidad y mapeo XMind

El IR no contendrá org.xmind.ui.treetable.toptitle, org.xmind.internal.topicShape.treeTableCell, structureClass ni shape-class como vocabulario estructural neutral.

El adaptador XMind de la Fase 7 será responsable de mapear:

- Topic.structure.type = tree_table a la clase estructural que corresponda en la versión objetivo de XMind.
- semantic_role de cada hijo a su papel de celda y a su estilo.
- El orden de filas y celdas al orden visual de la estructura.

La Fase 2 solo define y valida el contrato; no afirma todavía que la exportación XMind esté implementada.

## 5. Semántica de propiedades de estilo

| Estado | Representación | Significado |
|---|---|---|
| Ausente | La clave no aparece | No declara valor; se aplica la cascada |
| Explícito | Cualquier valor permitido | Declara ese valor |
| Reinicio | null | Reinicio explícito según la política de la propiedad |
| Literal inherited | "inherited" | Texto literal que se conserva; no es una orden del motor IR |

El valor inherited observado en Tema1 procede de JSON exportado por XMind. No se transformará automáticamente en ausencia ni en una directiva de herencia del IR.

La herencia de conjuntos de estilos por descendencia es una regla existente. La futura herencia de formato desde el primer hijo será una regla separada del catálogo PMD, no una semántica implícita de null o del literal inherited.

## 6. Versionado y compatibilidad

- IR 1.0.0 mantiene su significado y sus documentos de referencia.
- IR 1.1.0 añade los campos opcionales semantic_role y structure.
- Los campos nuevos solo pueden aparecer en documentos declarados como 1.1.0.
- Los lectores de esta versión aceptarán 1.0.0 y 1.1.0.
- El valor por defecto de constructores existentes no se cambia silenciosamente.
- La migración 1.0.0 → 1.1.0 es explícita y no infiere roles a partir de títulos, estilos o clases XMind.
- La propiedad antigua layout.structure_class se conserva para lectura histórica de 1.0.0; no se usa en documentos nuevos 1.1.0. Su conversión requiere evidencia y decisión explícita.

## 7. Validación semántica

Para cada Topic:

1. semantic_role, si aparece, debe ser texto no vacío.
2. structure.type debe ser un tipo conocido por esta versión.
3. En tree_table, debe haber al menos una fila y cada fila al menos una celda.
4. Cada topic_id debe referenciar un hijo directo.
5. No puede repetirse un topic_id.
6. Todos los hijos directos deben aparecer exactamente una vez.
7. Un hijo referenciado puede declarar otra estructura, lo que permite anidamiento.

El esquema JSON valida forma y tipos; validate_mind_map() valida relaciones entre entidades.

## 8. Pruebas requeridas

### Positivas
- IR 1.0.0 existente sin campos nuevos.
- IR 1.1.0 con rol semántico en tema y celdas.
- Tabla de árbol con varias filas y celdas ordenadas.
- Tabla anidada en una celda.
- Celdas con contenido, anotaciones y estilos conservados.
- Serialización determinista y round-trip JSON.

### Negativas
- Campos nuevos en IR 1.0.0.
- Rol vacío o no textual.
- Tipo de estructura desconocido.
- Tabla sin filas o fila sin celdas.
- Referencia a tema inexistente o no hijo directo.
- Celda repetida.
- Hijo omitido.
- Estructura con referencias cruzadas/ciclos.
- Valor no textual para topic_id.

## 9. Fuera de alcance

- Catálogo de roles y estilos (Fase 3).
- Gramática PMD (Fase 4).
- Parser PMD (Fase 5).
- Conversión Markdown → PMD por IA (Fase 6).
- Traducción a content.json XMind y pruebas Desktop (Fase 7).
- Celdas combinadas o estructura tabular bidimensional general.
