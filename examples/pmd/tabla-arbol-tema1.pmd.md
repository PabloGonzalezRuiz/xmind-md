---
pmd_version: "1.0.0"
title: Tema1 — patrón de tabla de árbol
id: map_tema1_tree_table
catalog:
  id: xmind-md.study
  version: "1.0.0"
---

:::pmd
id: tema1
role: study.note
:::
# Tema1

:::pmd
id: bloque_ley
role: legal.document_title
:::
## BloqueLey

:::pmd
id: nombre
role: study.note
:::
### Nombre

:::pmd
id: resumen
role: study.note
:::
#### RESUMEN

:::pmd
id: titulo
role: legal.title
:::
##### Titulo

:::pmd
id: capitulo
role: legal.chapter
:::
###### Capitulo

:::pmd
id: articulo
parent: capitulo
role: legal.article
structure:
  type: tree_table
  rows:
    - cells: [cabecera, cuerpo]
:::
###### Articulo

:::pmd
id: cabecera
parent: articulo
role: table.header_cell
style_ref: visual.table.header-cell
:::
###### Cabecera
**Unidad normativa**

:::pmd
id: cuerpo
parent: articulo
role: table.body_cell
style_ref: visual.table.body-cell
style_overrides:
  topic:
    fill:
      color: "#F6A04D"
:::
###### cuerpo
Contenido de la celda, que puede incluir párrafos, listas, notas, enlaces y otros bloques admitidos.

:::pmd-note
La profundidad adicional se representa mediante `parent`, que prevalece sobre la relación inferida por nivel de encabezado. Las celdas son los dos hijos directos del tema Articulo y mantienen sus propios roles y estilos.
:::
