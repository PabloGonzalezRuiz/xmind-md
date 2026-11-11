# Auditoría funcional — tarea 6

- **Fecha:** 2026-11-11
- **Rama:** `main`
- **Commit validado:** `a36f36ddc53bc71ef288c829ec5abc6e1eb16cc6`
- **CI de referencia:** [run 43006735888](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/43006735888)
- **Estado:** completada; todos los jobs del run de referencia terminaron en success.
- **Alcance:** parser Markdown, puente IR, entidades y validación, resolución de estilos, configuración de estilos, adaptadores JSON/XMind, CLI, ejemplos y flujo de smoke test.

## 1. Dictamen

La auditoría encontró defectos funcionales que no estaban cubiertos por la suite anterior. Se corrigieron y se añadieron regresiones. El proyecto pasa ahora **161 pruebas** en Python 3.10, 3.11 y 3.12; Ruff, construcción e instalación de distribuciones y conversiones desde wheel/sdist también pasan.

La tarea no convierte el adaptador XMind en un exportador completo. La compatibilidad sigue siendo un perfil parcial y debe respetarse la matriz de capacidades.

## 2. Hallazgos corregidos

### 2.1 Parser y conversión al IR

1. **Tipo de tema detached inaccesible desde Markdown.** El adaptador admitía `detached`, pero la gramática del parser solo aceptaba `attached`, `callout` y `summary`. Se añadió `detached` al parser, con comprobación de tipo y restricción de que el tema raíz sea `attached`.
2. **Errores de tipo no controlados en YAML de temas.** Un `kind` o un `links[].kind` con lista/objeto podía producir `TypeError` en vez de un error de parsing. Ahora se validan antes de consultar conjuntos; los enlaces comprueban kind, destino, título e ID.
3. **Valores de marcadores insuficientemente validados.** Se restringen a escalares textuales o numéricos/booleanos; se rechazan objetos y listas.
4. **Pérdida de contenido de listas en la API legacy.** El campo de texto legacy se construía desde una estructura de bloques como si fueran cadenas, produciendo contenido vacío. Se reconstruye recursivamente y con saltos de línea reales.
5. **Pérdida de barras invertidas en tablas.** El parser consumía barras antes de cualquier carácter. Ahora solo interpreta `\|` como pipe escapado y conserva barras en rutas y otros datos.
6. **YAML aceptaba valores que no son JSON.** Se normalizan fechas a ISO 8601 y se rechazan NaN, infinito, bytes, sets y claves que colisionan al normalizarse a texto. Esto evita JSON no estándar o fallos de serialización posteriores.
7. **Directivas globales descartaban propiedades desconocidas.** Relaciones, boundaries y summaries ahora aceptan únicamente campos definidos más `extensions`; los campos desconocidos generan un error explícito.
8. **Extensiones perdidas durante la conversión.** Se preservan `extensions` del mapa dentro de `metadata.extensions`, y las extensiones de relaciones, boundaries y summaries en sus entidades IR.
9. **Metadatos textuales del mapa.** `author` y `description` se validan como texto o null; `style_set` debe ser texto no vacío.

### 2.2 Validación IR

1. **Referencias a estilos externos rechazadas prematuramente.** La validación del parser solo conocía estilos embebidos y rechazaba referencias que debían resolverse desde `--styles`. La comprobación de catálogo se difiere a `resolve_styles()`, que combina estilos embebidos y externos y falla si la referencia no se resuelve.
2. **Errores de tipo que podían escapar como excepciones de Python.** Se endureció la validación del título de hoja, bloques de contenido, objetos de enlace y metadatos de assets. Tamaños de assets deben ser enteros no negativos; booleanos no cuentan como enteros válidos.

### 2.3 Estilos

1. **Configuración de ejemplo incompatible con el resolutor real.** `config/styles.yaml` utilizaba un esquema anterior (`elements`, `applies_to`, `properties`, `extends`) que el resolutor actual no consume. Se migró al formato real: `style_sets`, propiedades por tipo de elemento y `styles` globales o por conjunto.
2. **Estilos de línea de relaciones no materializados.** Se añadieron los mapeos `line.color`, `line.width` y `line.pattern` al formato XMind.
3. **Booleanos de estilo interpretados por truthiness.** `text.bold` y `text.italic` ahora exigen booleanos reales; valores como `"false"` o `1` ya no se convierten silenciosamente en estilos activos.

### 2.4 Adaptador XMind y JSON

1. **Imágenes inline perdían información silenciosamente.** Los runs de imagen también contenían texto alternativo; el adaptador priorizaba ese texto y no llegaba a rechazar `image_source`. Ahora las imágenes inline producen un error explícito, igual que otros recursos no soportados.
2. **JSON no estricto.** Los adaptadores JSON y XMind serializan con `allow_nan=False`; NaN e infinito no pueden producir documentos JSON inválidos.

### 2.5 Ejemplos y ejecución de smoke test

1. **Asset inexistente en el ejemplo de Constitución.** Se añadió `examples/assets/escudo.svg`, un recurso ilustrativo original; se actualizaron el Markdown y el ejemplo IR para apuntar a él.
2. **Comando XMind de README no ejecutable con el ejemplo avanzado.** El documento de Constitución contiene recursos, descripción, tareas, boundaries y summaries que el perfil XMind actual rechaza expresamente. El comando de exportación XMind ahora usa `examples/xmind-smoke-test.md`; Constitución permanece como ejemplo de entrada/IR JSON.
3. **Smoke test con conjunto de estilos externo.** El ejemplo mínimo declara `BASE_ACADEMICO`; `scripts/create_xmind_smoke.py` carga `config/styles.yaml` y resuelve estilos antes de exportar.

## 3. Evidencia de validación

Run [43006735888](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/43006735888), commit `a36f36ddc53bc71ef288c829ec5abc6e1eb16cc6`, finalizó `completed / success`.

| Job | Resultado |
|---|---|
| Ubuntu / Python 3.10 | Ruff lint y format correctos; **161 pruebas superadas**; XMind smoke generado |
| Ubuntu / Python 3.11 | Ruff lint y format correctos; **161 pruebas superadas**; XMind smoke generado |
| Ubuntu / Python 3.12 | Ruff lint y format correctos; **161 pruebas superadas**; XMind smoke generado |
| Build e instalación de distribuciones | wheel y sdist construidos, verificados e instalados en entornos limpios; conversiones JSON/XMind correctas |

Artefactos:
- `python-distributions`: ID `13849240803`, 77.807 bytes, digest SHA-256 del ZIP de Actions `0d638d960a62909f2c21a1c60687baf4f99e6529f7926eaf7d8e2a4348a048bf`.
- `xmind-desktop-smoke-test-py3.10`: ID `13847858956`.
- `xmind-desktop-smoke-test-py3.11`: ID `13847903592`.
- `xmind-desktop-smoke-test-py3.12`: ID `13849106285`.

El digest identifica el ZIP del artefacto de Actions, no los hashes individuales del wheel o del sdist.

## 4. Limitaciones funcionales que permanecen

- La gramática no es un parser completo de CommonMark/GFM; listas con líneas de continuación, extensiones Markdown arbitrarias y otras construcciones fuera del subconjunto documentado no están garantizadas.
- El adaptador XMind no exporta recursos/imágenes, imágenes inline, tareas, boundaries, summaries ni extensiones. El tipo de tema `summary` puede representarse en IR, pero no en el perfil XMind actual.
- El contenido de bloques se aplana a texto de notas XMind; se pierde parte de la estructura y formato inline. Los enlaces inline dentro de contenido no conservan todas sus semánticas.
- `examples/constitucion.md` no es un fixture de exportación XMind; su finalidad es demostrar el parsing/IR/JSON y las características avanzadas.
- El smoke XMind generado con el nuevo conjunto de estilos ha pasado la validación estructural de CI. No se ha realizado una nueva inspección manual de ese archivo en XMind Desktop; la inspección manual anterior corresponde al fixture versionado y a XMind Desktop 26.05.01107.
- CI ejecuta en Ubuntu. No se deduce compatibilidad Windows de esa matriz.
- Python 3.10 sigue en la matriz de compatibilidad técnica, pero está fuera de soporte upstream desde 2026-10-01.
- No se ha publicado tag ni GitHub Release. La versión sigue siendo 0.1.0.

## 5. Trabajo pendiente

1. **Tarea 7 — sincronización documental final:** revisar README, gramática, especificación IR, sistema de estilos, matriz XMind, guía de desarrollo, catálogo de archivos y ejemplos frente al comportamiento actual. En particular, aclarar el esquema real de `config/styles.yaml`, la resolución de estilos externos, el soporte de `detached` y las limitaciones XMind.
2. **Tarea 8 — publicación:** preparar changelog, fijar versión/tag, ejecutar auditoría final de release y publicar wheel/sdist con GitHub Release, una vez completada la revisión documental.

La tarea 6 está cerrada. No iniciar la tarea 7 sin autorización expresa del usuario.
