# Análisis de referencia XMind: Tema1

**Fecha:** 2026-11-12. **Estado:** análisis de referencia completado para la Fase 1 de la hoja de ruta.

## 1. Alcance y fuentes

Se han contrastado los tres archivos versionados en `themes/Tema1/`:

- `content.json`: exportación estructural y de propiedades de XMind.
- `Tema1.svg`: exportación visual de la misma referencia.
- `Tema1.md`: exportación Markdown de XMind.

No está versionado el archivo editable `.xmind` original. Por tanto, el análisis describe lo que muestran las exportaciones disponibles; no atribuye al documento original información que no aparezca en ellas.

## 2. Estructura recuperada del JSON

El JSON contiene una hoja y 10 temas:

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

La estructura es jerárquica, pero no todos los datos de presentación se deducen de la profundidad. El tema raíz declara `org.xmind.ui.tree.branch-aligned.left`; varios nodos también declaran esta clase de estructura. `Articulo` declara `org.xmind.ui.treetable.toptitle`.

| Nodo | Profundidad | Estructura | Clase de forma | Marcadores |
|---|---:|---|---|---|
| Tema1 | 0 | `tree.branch-aligned.left` | — | — |
| ListaBloque | 1 | No declarada | — | — |
| BloqueLey | 1 | `tree.branch-aligned.left` | — | — |
| Nombre | 2 | `tree.branch-aligned.left` | — | — |
| RESUMEN | 3 | `tree.branch-aligned.left` | `roundedRect` | — |
| Titulo | 4 | `tree.branch-aligned.left` | `doubleunderline` | `flag-red` |
| Capitulo | 5 | `tree.branch-aligned.left` | `doubleunderline` | — |
| Articulo | 6 | `treetable.toptitle` | `treeTableCell` | `flag-red`, `task-oct` |
| Cabecera | 7 | No declarada | `treeTableCell` | — |
| cuerpo | 7 | No declarada | `treeTableCell` | — |

Los nombres de clase de la tabla se abrevian para facilitar la lectura; los valores completos están en `content.json`. Es importante conservar la distinción entre `structureClass` y la propiedad de estilo `shape-class`: son campos distintos y no deben fusionarse en un único concepto PMD.

## 3. Estilos: tres capas que deben distinguirse

### 3.1 Tema general y valores de nivel

La hoja incluye `theme` con perfiles como `centralTopic`, `mainTopic`, `subTopic`, `floatingTopic`, `summaryTopic`, `calloutTopic`, `importantTopic`, `minorTopic`, `expiredTopic`, además de `boundary`, `summary`, `relationship` y niveles adicionales.

También hay un estilo de hoja y un estilo del tema raíz. Estos valores constituyen contexto visual de la hoja y no equivalen a estilos semánticos de autoría PMD.

### 3.2 Estilos explícitos por tema

Nueve de los diez temas tienen un objeto `style` propio. `ListaBloque` no contiene estilo explícito en su objeto de tema. Los estilos de los demás temas no son uniformes: algunos declaran muchas propiedades y otros solo unas pocas.

Ejemplos relevantes:

- `RESUMEN` define tipografía, color, relleno, línea, borde, forma y conexión.
- `Titulo` y `Capitulo` tienen propiedades similares, pero no idénticas; cambian especialmente propiedades del borde.
- `Articulo` define relleno gris, tipografía, borde y forma de conexión; además declara la estructura de tabla de árbol.
- `Cabecera` y `cuerpo` comparten `shape-class=treeTableCell`, pero tienen rellenos distintos: `#EEEEEEFF` y `#f6a04d33`.
- En `cuerpo`, varias propiedades del borde tienen el valor literal `inherited`; esto no es equivalente a omitirlas.

### 3.3 Valores heredados

En esta exportación aparecen tres situaciones distintas:

1. Propiedad ausente en el estilo del tema.
2. Propiedad presente con valor concreto.
3. Propiedad presente con el valor especial `inherited`.

El resolutor PMD futuro deberá definir cómo interpreta cada situación y conservar la procedencia de los valores. No se debe inferir que una propiedad ausente equivale siempre a heredar del padre, ni que el valor `inherited` equivale a heredar del primer hermano.

## 4. Tabla de árbol y celdas

El dato estructural inequívoco es:

- `Articulo.structureClass = org.xmind.ui.treetable.toptitle`.
- Los dos hijos, `Cabecera` y `cuerpo`, tienen `shape-class = org.xmind.internal.topicShape.treeTableCell`.
- Los dos hijos son temas hermanos y sus estilos explícitos difieren.

La representación confirma que PMD debe poder expresar la estructura especial de tabla y el rol/formato de cada celda. No basta con representar los dos elementos como viñetas subordinadas al artículo.

Esta referencia no demuestra que XMind haya aplicado automáticamente el estilo de la primera celda a la segunda. De hecho, ambas celdas contienen estilos propios en el JSON. Por ello, la herencia PMD por referencia al primer hijo sigue siendo una regla de autoría futura, no una descripción del comportamiento nativo probado por este ejemplo.

## 5. Marcadores

Los marcadores observados son:

- `Titulo`: `flag-red`.
- `Articulo`: `flag-red` y `task-oct`.

Deben modelarse como anotaciones/indicadores independientes del estilo visual del tema. La IA podrá seleccionar marcadores mediante reglas semánticas, pero el catálogo deberá distinguirlos de los estilos de forma, texto y celda.

## 6. Correspondencia con SVG

La exportación SVG tiene 856.804 caracteres y contiene:

- 10 elementos `foreignObject`, uno por cada título.
- 0 elementos SVG `text` convencionales para los títulos.
- 61 grupos `g`, 33 rutas `path`, 3 imágenes y 6 declaraciones `@font-face`.
- 103 atributos `data-view-id`.

Los 10 elementos de título utilizan identificadores `data-view-id="topic-title:<topic-id>"`. El UUID después de `topic-title:` coincide con el `id` del tema en `content.json`. Esto permite asociar de forma directa cada tema JSON con su representación visual y comprobar el texto y parte de la tipografía renderizada.

Los títulos se representan mediante `foreignObject` con contenido XHTML y estilos CSS inline. El SVG también incluye recursos gráficos y tipográficos embebidos. Estos detalles sirven para analizar y reproducir la apariencia, pero no son un contrato que PMD deba copiar literalmente.

**Decisión vigente:** el SVG generado debe ser lo más fiel posible a la apariencia original de XMind. No se exige igualdad byte a byte ni reproducción exacta de XML, atributos, IDs o recursos internos.

## 7. Qué conserva y qué pierde el Markdown

`Tema1.md` conserva:

- Los textos de los 10 temas.
- La jerarquía general, mediante un encabezado raíz y listas anidadas.
- Algunos énfasis en negrita.

No conserva de forma estructurada:

- La clase de estructura de tabla de árbol.
- La distinción entre título superior de tabla y celdas.
- Los estilos explícitos ni la diferencia entre propiedades ausentes, concretas e `inherited`.
- Los marcadores.
- Las formas, rellenos, patrones, bordes, tipografía y conexiones.
- La correspondencia por ID entre cada tema y su representación visual.

Conclusión: la importación Markdown de XMind es una vía de intercambio textual, no una representación de autoría suficientemente expresiva para reconstruir mapas de estudio complejos.

## 8. Requisitos derivados para PMD y su catálogo

1. Separar contenido, jerarquía, rol semántico, estructura visual y anotaciones.
2. Poder declarar una estructura especial, como tabla de árbol, sin codificar clases internas de XMind.
3. Identificar roles de celda, como cabecera y cuerpo, independientemente del texto literal.
4. Referenciar estilos reutilizables con identificadores estables.
5. Documentar cada estilo para personas e IA: significado, cuándo usarlo, destinatarios, restricciones, ejemplos positivos y negativos.
6. Combinar reglas semánticas prioritarias con reglas estructurales contextuales.
7. Resolver herencia y excepciones de forma determinista, sin delegar la resolución final a la IA.
8. Distinguir defaults de tema, estilos explícitos, propiedades ausentes, herencia declarada y overrides.
9. Mantener marcadores separados de los estilos visuales.
10. Mantener las claves neutrales PMD independientes de los nombres internos de XMind.

## 9. Límites y cuestiones aún abiertas

- No se dispone del `.xmind` editable original en el repositorio.
- Este ejemplo muestra una tabla de árbol con dos celdas; no basta para definir todas las variantes posibles de tablas.
- El SVG permite relacionar títulos con IDs, pero no constituye por sí solo un algoritmo completo de reconstrucción.
- No se ha especificado aún el catálogo semántico, el vocabulario de roles, la sintaxis PMD ni la precedencia completa entre reglas y herencia.
- No se ha implementado conversión IA → PMD ni el generador SVG final.

## 10. Resultado de la Fase 1

La referencia Tema1 ya permite distinguir qué información existe en el JSON, qué parte se refleja en el SVG y qué se pierde en Markdown. Se han identificado los roles estructurales de la tabla, las celdas, los estilos y marcadores, y las necesidades que deben guiar la siguiente fase.

La Fase 1 puede considerarse cerrada para esta referencia. La Fase 2 debe especificar el catálogo reutilizable, las reglas semánticas/estructurales y la resolución de herencia antes de aprobar la sintaxis PMD.
