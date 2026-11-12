# Tema1 — referencia de estructura y estilos XMind

**Estado:** exportaciones incorporadas; análisis inicial realizado; análisis completo pendiente.  
**Objetivo:** utilizar este mapa para diseñar PMD y comprobar qué información pierde la importación nativa de Markdown.

## Archivos disponibles

| Archivo | Contenido | Estado |
|---|---|---|
| `content.json` | Estructura de hoja, temas, clases estructurales, estilos y marcadores exportados por XMind | Incorporado |
| `Tema1.svg` | Representación visual exportada por XMind | Incorporado |
| `Tema1.md` | Markdown de referencia con títulos, jerarquía y énfasis | Incorporado |
| `Tema1.xmind` | Archivo editable original | No está versionado en esta carpeta |

## Jerarquía identificada

```text
Tema1
├── ListaBloque
└── BloqueLey
    └── Nombre
        └── RESUMEN
            └── Titulo
                └── Capitulo
                    └── Articulo
                        ├── Cabecera
                        └── cuerpo
```

El JSON contiene 10 temas: raíz `Tema1` y 9 descendientes.

## Estructuras especiales

- `Articulo` declara `structureClass: org.xmind.ui.treetable.toptitle`, correspondiente a la estructura de tabla de árbol.
- Sus hijos `Cabecera` y `cuerpo` usan `shape-class: org.xmind.internal.topicShape.treeTableCell`.
- Las dos celdas comparten clase estructural, pero tienen estilos distintos; por ejemplo, sus rellenos son `#EEEEEEFF` y `#f6a04d33`.
- PMD debe poder expresar tanto la estructura de tabla como el formato diferenciado de cada celda.

## Estilos y marcadores observados

- Hay estilos explícitos en la raíz y en varios descendientes.
- `Titulo` tiene el marcador `flag-red`.
- `Articulo` tiene `flag-red` y `task-oct`.
- Las propiedades exportadas incluyen tipografía, color de texto, relleno, patrones, bordes, formas y conexiones. Los valores internos de XMind deberán traducirse a conceptos neutrales; no deben convertirse automáticamente en sintaxis PMD propietaria.

## Diferencia con Markdown

`Tema1.md` representa la raíz y sus descendientes mediante encabezados/listas y conserva algunos énfasis. No expresa:

- La estructura de tabla de árbol de `Articulo`.
- La identidad de `Cabecera` y `cuerpo` como celdas.
- Los estilos explícitos, colores, rellenos, bordes, formas y tipografías.
- Los marcadores de `Titulo` y `Articulo`.

El Markdown nativo es una referencia de texto y jerarquía, no una descripción suficiente del mapa XMind original.

## Observaciones del SVG

La exportación tiene aproximadamente 857 kB y utiliza `foreignObject` para títulos, además de grupos, paths, imágenes, fuentes embebidas y referencias `data-view-id`. Los títulos no aparecen como elementos SVG `text` convencionales en esta exportación.

Esta estructura ayuda a comprender el resultado visual, pero la decisión vigente es priorizar la fidelidad visual y mantener sencilla la implementación. No se exige reproducir exactamente XML, atributos, IDs ni recursos internos de XMind.

## Trabajo pendiente

- [ ] Documentar propiedades de estilo de cada nodo y distinguir explícitas/heredadas.
- [ ] Analizar reglas de herencia y formatos por defecto en grupos de hermanos.
- [ ] Describir con precisión la tabla de árbol y sus celdas.
- [ ] Relacionar nodos del JSON con elementos visuales del SVG.
- [ ] Derivar requisitos semánticos y estructurales para el catálogo.
- [ ] Derivar un ejemplo PMD cuando la sintaxis esté aprobada.

## Decisiones PMD relacionadas

- El primer hijo puede actuar como referencia de formato predeterminado para sus hermanos.
- Los hermanos pueden declarar excepciones explícitas.
- La regla se aplica recursivamente.
- La IA utilizará estilos semánticos y reglas estructurales del catálogo, no valores XMind internos repetidos en cada nodo.

Son decisiones de diseño; el algoritmo y la sintaxis están pendientes. Fuente normativa: [docs/pmd-design.md](../../docs/pmd-design.md).
