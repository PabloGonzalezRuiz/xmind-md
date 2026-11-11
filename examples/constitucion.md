---
title: Constitución Española
id: map_constitucion
author: Material de estudio
description: Ejemplo de gramática enriquecida de XMind MD.
style_set: TAI_LEGISLACION
layout:
  structure: mind_map
  direction: balanced
---

# Constitución Española

Norma suprema del ordenamiento jurídico español.

## Título preliminar

:::xmind
id: topic_articulo_1
:::
### Artículo 1

España se constituye en un Estado social y democrático de Derecho.

:::xmind
id: topic_articulo_14
style: concepto_importante
labels:
  - IMPORTANTE
  - EXAMEN
markers:
  - group: priority
    value: 1
task:
  status: in_progress
  progress: 50
:::
### Artículo 14

Los españoles son **iguales ante la ley**.

- No puede prevalecer discriminación alguna.
- Se prohíbe la discriminación por razón de nacimiento, raza, sexo, religión, opinión o cualquier otra condición o circunstancia personal o social.

| Concepto | Contenido |
|---|---|
| Principio | Igualdad ante la ley |
| Garantía | Prohibición de discriminación |

:::xmind-note
Este artículo reconoce el principio de igualdad y no discriminación.

Puede incluir **formato**, listas y [enlaces](https://www.boe.es/).
:::

Consulta el [Boletín Oficial del Estado](https://www.boe.es/).

![Escudo ilustrativo](assets/escudo.svg)

```python
def igualdad(persona_a, persona_b):
    return persona_a.derechos == persona_b.derechos
```

:::xmind-relationship
id: rel_igualdad
source: topic_articulo_1
target: topic_articulo_14
title: Principio constitucional relacionado
style: relacion_default
:::

:::xmind-boundary
id: boundary_derechos
topics:
  - topic_articulo_14
title: Derechos y principios
style: agrupacion_derechos
:::

:::xmind-summary
id: summary_igualdad
topics:
  - topic_articulo_14
title: Principio de igualdad
style: resumen
:::
