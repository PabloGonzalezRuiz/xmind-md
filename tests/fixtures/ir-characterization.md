---
title: Mapa de caracterización
id: mapa_caracterizacion
author: Equipo de pruebas
description: Fixture estable para proteger la conversión Markdown a IR.
style_set: LEGISLACION
styles:
  destacado:
    topic:
      text:
        bold: true
style_sets:
  LEGISLACION:
    topic:
      text:
        color: "#123456"
extensions:
  vendor:
    source: fixture
layout:
  structure: mind_map
  direction: balanced
---

# Mapa

Introducción con **énfasis** y [Artículo 1](topic:articulo_1).

:::xmind
id: articulo_1
style: destacado
labels: [IMPORTANTE]
markers:
  - group: priority
    value: 1
task:
  status: in_progress
  progress: 50
links:
  - kind: web
    target: https://www.boe.es/
:::
## Artículo 1

Texto **clave**.

- Regla
  - Excepción

| Concepto | Contenido |
|---|---|
| Ámbito | General |

> Cita normativa

---

![Escudo](assets/escudo.svg)

```python
print("ok")
```

:::xmind-note
Nota **clave**.
:::

:::xmind-relationship
id: rel_articulo
source: articulo_1
target: articulo_1
title: Relación de prueba
:::
