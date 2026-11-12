# Investigación de documentación y código oficial de XMind

**Fecha de consulta:** 2026-11-12.  
**Ámbito:** documentación pública y repositorios de la organización XMind Ltd., con atención a código TypeScript/MIT.  
**Objetivo:** extraer evidencia útil para interpretar, generar y convertir libros XMind sin confundir una implementación concreta con una especificación universal.

## 1. Conclusión ejecutiva

La investigación no ha localizado una especificación pública normativa, completa y versionada del formato moderno XMind que describa todos los archivos, campos JSON, reglas de validación, resolución de estilos y comportamiento del motor de presentación.

Sí existen fuentes oficiales de mucho valor:

1. **xmind-sdk-js**: SDK oficial TypeScript/JavaScript, MIT. Su README indica que implementa funciones similares a las aplicaciones XMind y que los archivos generados pueden abrirse con ellas.
2. **xmind-model**: modelo de datos utilizado por ese SDK, TypeScript, MIT. Contiene interfaces, clases y JSON Schema Draft-07 para hojas, temas, estilos, notas, marcadores, relaciones, límites, resúmenes y otros componentes. Su README advierte que no debe utilizarse directamente y que debe consumirse mediante xmind-sdk-js.
3. **xmind-generator**: generador TypeScript oficial de XMind Ltd., MIT. Su descripción indica que genera archivos XMind de forma semejante a las aplicaciones XMind. Su serializador permite observar cómo construye un ZIP con content.json, metadata.json, manifest.json y recursos.

Estas fuentes son documentación e implementaciones oficiales, pero **no constituyen por sí mismas una especificación normativa completa**. El código revela qué representa y genera cada biblioteca, no necesariamente todo lo que XMind Desktop acepta o cómo renderiza cada propiedad.

También se han localizado dos referencias adicionales: **xmindmark**, un lenguaje oficial de marcado para mapas mentales en TypeScript/MIT que probablemente coincide con la pista del usuario, y **xmind-cli**, la guía oficial más reciente para agentes, cuyo repositorio distribuye un Skill MIT y enlaza el CLI como paquete npm separado.

## 2. Repositorios oficiales identificados

### 2.1 xmind-sdk-js

- Repositorio: https://github.com/xmindltd/xmind-sdk-js
- README: https://github.com/xmindltd/xmind-sdk-js/blob/master/README.md
- Código: https://github.com/xmindltd/xmind-sdk-js/tree/master/src
- Pruebas funcionales: https://github.com/xmindltd/xmind-sdk-js/blob/master/test/functional/index.test.ts
- Licencia: MIT.
- Paquete npm observado en package.json: xmind, versión 2.2.33.
- Implementación TypeScript; depende de xmind-model ^1.1.12.
- Último commit consultado: 2024-06-13 (SHA d35e820a2d09995c69bbb452d4edc42b09a13946).

El README lo presenta expresamente como SDK oficial, ligero y utilizable desde Node.js o navegador. Explica el modelo de componentes, Workbook, Sheet, Topic, Marker, Note, Theme y Zipper. También documenta creación de temas, temas hijos, notas, marcadores, etiquetas, imágenes, resúmenes, temas y validación.

**Precaución temporal:** es un SDK con dependencias y modelo de datos de generaciones anteriores (TypeScript 3.x y xmind-model 1.1.12). Aunque resulta una fuente oficial para estudiar el modelo de componentes, no se debe asumir que sus decisiones de empaquetado o todos sus campos describen sin cambios el formato de XMind Desktop actual.

### 2.2 xmind-model

- Repositorio: https://github.com/xmindltd/xmind-model
- Esquemas: https://github.com/xmindltd/xmind-model/tree/master/schemas
- Modelo de temas: https://github.com/xmindltd/xmind-model/blob/master/src/models/topic.ts
- Modelo de hoja: https://github.com/xmindltd/xmind-model/blob/master/src/models/sheet.ts
- Modelo de estilos: https://github.com/xmindltd/xmind-model/blob/master/src/models/style-component.ts
- Licencia: MIT.
- Paquete observado: xmind-model 1.1.12.
- Último commit consultado: 2020-06-12 (SHA c448b0fcfc8bee51f68124aae87a57e3947c6b44).

El repositorio se describe como el modelo central de Snowbrush. Su README dice que no se debe consumir directamente y que será sustituido por una versión TypeScript en el futuro; el package.json y los archivos fuente disponibles contienen las interfaces y clases que utiliza el SDK.

Los esquemas principales son:

- schema.json: documento raíz, un array de hojas y definiciones compartidas.
- sheet.json: hoja.
- topic.json: tema y sus colecciones de hijos.
- theme.json: perfiles visuales de tema.
- relationship.json: relación entre temas.
- boundary.json y summary.json: límites y resúmenes.
- marker.json: marcadores.
- notes.json: notas.
- image.json y numbering.json: imagen y numeración.

El esquema raíz declara JSON Schema Draft-07. Es una fuente técnica importante, pero debe tratarse como el contrato de esa versión del modelo, no como garantía de compatibilidad universal con todas las generaciones de XMind.

### 2.3 xmind-generator

- Repositorio: https://github.com/xmindltd/xmind-generator
- README/API: https://github.com/xmindltd/xmind-generator/blob/main/README.md
- Serializador: https://github.com/xmindltd/xmind-generator/blob/main/src/internal/serializer.ts
- Modelo de tema: https://github.com/xmindltd/xmind-generator/blob/main/src/internal/model/topic.ts
- Licencia: MIT (Xmind Ltd.).
- Paquete observado: xmind-generator 1.0.1.
- Implementación TypeScript; Node.js >=14.
- Último push consultado: 2024-06-14.

Este repositorio es especialmente relevante porque ofrece una segunda implementación oficial, separada del SDK anterior, con un modelo interno propio y un serializador explícito. Su README presenta una API declarativa de builders:

- Workbook y una o varias RootTopic.
- Topic y children para construir jerarquía.
- note, labels, markers e image.
- summaries y relationships.
- archive para producir el archivo XMind.

El modelo usa IDs internos generados y referencias temporales para resolver relaciones y resúmenes. El serializador transforma el modelo de construcción en el JSON del libro y empaqueta recursos.

**Limitación:** su API pública no expone un sistema general de estilos, estructura de tabla de árbol, posiciones libres, clases visuales o personalización completa de layout. Es una muestra fiable de su perfil de generación, no un esquema exhaustivo de todas las posibilidades de XMind.

## 3. Qué estructura de datos revela xmind-model

### 3.1 Documento y hoja

El esquema raíz representa el documento como un array de hojas. Cada hoja puede contener:

- id y title.
- rootTopic.
- style.
- topicPositioning y topicOverlapping.
- theme.
- relationships.
- legend y settings.

El modelo TypeScript de Sheet confirma la existencia de un tema raíz, una colección de relaciones, tema visual, leyenda y ajustes. También muestra operaciones de cambio de posicionamiento libre/fijo y solapamiento.

Esto amplía el análisis de Tema1: la hoja no es únicamente un contenedor del árbol. Puede incluir configuración de layout, tema, relaciones y otros componentes de ámbito de hoja.

### 3.2 Tema y colecciones de hijos

TopicData incluye, entre otros:

- id y title.
- style y class.
- position.
- structureClass.
- branch.
- width/customWidth según la variante de modelo.
- labels.
- numbering.
- href.
- notes e image.
- children.
- markers.
- boundaries.
- summaries.
- extensions.

La propiedad children es un objeto cuyas claves identifican tipos de relación y cuyos valores son arrays de temas. En los esquemas y el código consultados aparecen los tipos:

- attached
- detached
- summary
- callout

El modelo asigna attached como tipo por defecto al crear un tema hijo. El tipo no es un atributo decorativo: determina cómo se agrupa el tema en el árbol y cómo lo interpreta el modelo.

La diferencia entre summary y summaries es importante en esta implementación: los temas resumen pueden estar representados como hijos de tipo summary, mientras que summaries almacena la información de rango que relaciona el resumen con una sección de hijos. No deben aplanarse ambas estructuras en una única lista.

### 3.3 Clases y estructura

El modelo separa:

- class: cadena de clases/familias asociadas al componente.
- structureClass: clase de estructura del tema.
- style.properties: propiedades visuales concretas.

El código de StyleComponent divide class por espacios y consulta el tema visual para obtener valores asociados a esas familias. Esto evidencia que las clases pueden funcionar como referencias a familias de estilo del tema, mientras que el objeto style conserva propiedades locales.

Esto refuerza la decisión del proyecto de no fusionar class, structureClass y shape-class en una única propiedad semántica PMD.

### 3.4 Estilos locales y perfiles del tema

StyleData contiene un id y un objeto properties. El esquema permite propiedades adicionales de tipo string, por lo que el diccionario de propiedades es extensible.

ThemeData define perfiles como:

- map
- centralTopic
- mainTopic
- subTopic
- floatingTopic
- centralFloatingTopic
- boundary
- relationship
- summaryTopic
- summary

La implementación de StyleComponent crea un estilo local vacío cuando el componente no trae uno explícito. También proporciona getClassValue, que consulta las familias de estilo declaradas por class en el Theme de la hoja.

**Lo que sí demuestra el código:** existe un sistema de perfiles generales del tema, familias/clases de estilo y propiedades locales por componente.

**Lo que no demuestra por sí solo:** la cascada completa que utiliza cada versión de XMind Desktop al renderizar, la precedencia exacta entre todos los niveles o el significado universal de inherited. Esas reglas requieren pruebas con archivos producidos por Desktop.

### 3.5 Posicionamiento y layout

SheetData define topicPositioning como free o fixed y topicOverlapping como overlap o none. TopicData puede tener position con coordenadas x/y. El código de Sheet intenta detectar documentos antiguos con posiciones explícitas y activar el modo free cuando procede.

Esto confirma que el posicionamiento no depende solo de la jerarquía. La geometría y el modo de posicionamiento de la hoja también pueden intervenir.

No se debe extrapolar esta implementación a todos los motores/layouts actuales. El modelo es una evidencia de una generación concreta de Snowbrush/XMind.

### 3.6 Componentes auxiliares

El modelo oficial contempla entidades diferenciadas para:

- Relationship: id, title, style, class, end1Id, end2Id y controlPoints.
- Boundary: id, title, style, class y range.
- Summary: id, style, class, range y topicId.
- Marker: markerId y groupId.
- Notes: representación plain y HTML con párrafos/spans.
- Image: referencia y atributos de imagen.
- Numbering: formato, prefijo, sufijo y opciones.
- Extension: proveedor y contenido, con posibles referencias a recursos.

Esto es útil para el diseño futuro del lector XMind → IR: no debemos reducir todo a temas y texto. Conviene conservar las entidades auxiliares y los datos desconocidos.

### 3.7 Discrepancias entre esquema y código del modelo

Los esquemas deben leerse junto con las interfaces y la implementación, no de forma aislada. En los archivos consultados aparecen diferencias concretas:

- topic.json declara labels como string, mientras que los métodos de Topic devuelven y manipulan etiquetas como una colección de strings.
- topic.json declara customWidth, mientras que TopicData y las constantes del modelo utilizan width.
- Hay diferencias entre la forma declarada por algunos esquemas y la forma que el código produce/modifica.

Esto significa que el JSON Schema de xmind-model es una referencia histórica útil, pero no debe convertirse sin auditoría en nuestro validador de conformidad. Para cada propiedad hay que contrastar esquema, interfaz, código runtime, fixtures reales de Desktop y versión objetivo. La política del lector futuro debe tolerar variantes y preservar propiedades desconocidas en lugar de rechazar o eliminar datos por una discrepancia del esquema antiguo.

## 4. Cómo construye y empaqueta XMind el SDK xmind-sdk-js

### 4.1 Modelo de construcción

Workbook crea una o varias hojas. Cada Sheet tiene un rootTopic. Topic permite añadir hijos, notas, etiquetas, imágenes, marcadores y resúmenes. Los componentes se identifican mediante IDs y pueden buscarse por ID.

El README describe una abstracción de componentes: los componentes pueden tener hijos, mientras que Marker y Note se adjuntan a componentes. Las pruebas funcionales verifican la creación del árbol, la persistencia de IDs, notas, marcadores, resúmenes, imágenes, temas y validación.

### 4.2 Serialización

Workbook.toJSON() devuelve el modelo de datos y Workbook.toString() lo serializa como texto JSON. Workbook.validate() ejecuta el validador basado en los esquemas.

Zipper construye el ZIP y, en el código consultado, añade:

- content.json
- metadata.json con contenido {}
- content.xml mediante una plantilla XML
- manifest.json
- recursos bajo resources/ cuando se adjuntan imágenes

Dumper declara además las entradas de contenido, metadatos y manifiesto, y actualiza las referencias a recursos.

**Advertencia crítica:** esta implementación incluye content.xml heredado y un empaquetado diferente del perfil moderno que genera nuestro proyecto. En el Zipper inspeccionado no se escribe la entrada mimetype ni la miniatura PNG. Por ello, no debemos copiar su estructura ZIP como sustituto del perfil moderno actual. Su valor principal es el modelo de componentes y las operaciones de construcción.

## 5. Cómo genera archivos xmind-generator

### 5.1 Modelo de construcción

El generador separa builders y modelo interno:

- Workbook contiene hojas.
- Sheet contiene rootTopic y relaciones.
- Topic contiene hijos, notas, etiquetas, marcadores, imágenes y resúmenes.
- Summary se construye con referencias o índices de los hijos que abarca.
- Relationship referencia los temas de origen y destino.

Los métodos children y summaries permiten describir jerarquía y rangos de resumen. Las referencias usadas durante la construcción no se escriben necesariamente como referencias en el archivo final: se resuelven a IDs/rangos.

### 5.2 Serialización de content.json

El serializador genera un array de hojas. Para cada hoja escribe:

- id.
- class = sheet.
- title.
- rootTopic, si existe.
- relationships, si hay relaciones.

Para cada tema escribe:

- id.
- class = topic.
- title.
- notes.plain.content, si hay nota.
- labels, si hay etiquetas.
- children.attached, si hay hijos.
- image.src con prefijo xap:resources/, si hay imagen.
- markers con markerId.
- summaries con id, class, range y topicId.
- children.summary para los temas resumen.

La serialización conserva el orden de las colecciones y recorre los temas de forma recursiva. Los rangos de resumen se calculan a partir de índices de hijos; las referencias no encontradas hacen que se omita la información del resumen.

### 5.3 Contenedor ZIP generado

archive() genera un ZIP con:

- content.json.
- metadata.json con creator.name = xmind-generator y dataStructureVersion = "2".
- manifest.json con file-entries para content.json, metadata.json y recursos.
- resources/ con imágenes almacenadas usando un nombre basado en SHA-256 y extensión.

El ZIP se genera con compresión STORE. En el serializador inspeccionado no se añaden mimetype, content.xml ni miniatura.

### 5.4 Diferencias frente al perfil de nuestro adaptador y Tema1

| Aspecto | xmind-generator | XMind MD actual / Tema1 |
|---|---|---|
| content.json | Array de hojas | Array de hojas |
| Hoja | id, class, title, rootTopic y relaciones opcionales | Tema1 incluye además style, theme y extensions |
| Tema | id, class, title y propiedades opcionales | Tema1 incluye estilos locales, structureClass, markers y más propiedades |
| Hijos | attached y summary en el serializador | Tema1 observado con attached; modelo xmind-model contempla más tipos |
| Metadatos | dataStructureVersion "2" | El adaptador del proyecto declara "3" y layoutEngineVersion "5" |
| Recursos | resources/ y xap:resources/ | El perfil del proyecto actual no exporta todavía assets/imágenes |
| ZIP | content.json, metadata.json, manifest.json y recursos | mimetype, content.json, metadata.json, manifest.json y thumbnail |
| Estilos | No expone un sistema general en su API pública | Nuestro adaptador implementa un subconjunto de estilos; Tema1 contiene estilos y theme |

La tabla compara perfiles concretos, no versiones normativas de XMind. La diferencia de dataStructureVersion es una señal de que no debemos mezclar fragmentos de distintos generadores sin validar con XMind Desktop.

## 6. Consecuencias para PMD, IR y el adaptador

### 6.1 Mantener las capas neutrales

Se confirma la arquitectura:

Markdown → IA → PMD → parser/validador → IR neutral → resolución de estilos → adaptador XMind → ZIP XMind.

La IA no debe producir directamente content.json ni copiar estructuras internas de un SDK. PMD expresa semántica y estructura; el adaptador decide cómo serializarlo en el perfil XMind seleccionado.

### 6.2 No convertir las claves XMind en el catálogo semántico

La biblioteca de estilos PMD debe describir:

- Identificador semántico estable.
- Significado del rol.
- Tipo de entidad a la que se aplica.
- Estructuras compatibles.
- Reglas de selección semántica.
- Reglas estructurales complementarias.
- Defaults, excepciones y precedencia.
- Propiedades visuales neutrales.
- Mapeos específicos por perfil/versión XMind.

Las propiedades técnicas de XMind (fo:*, svg:*, shape-class, structureClass, class, etc.) pertenecen al adaptador y a la documentación de interoperabilidad, no a la interfaz de autoría habitual.

### 6.3 Preservar la información que no comprendemos

Un lector futuro debería preservar:

- IDs originales como procedencia.
- Claves desconocidas y extensiones.
- Clases y estructura originales.
- Colecciones de hijos por tipo.
- Orden de colecciones.
- Estilos locales y perfiles de tema.
- Geometría y settings de hoja.
- Recursos y referencias.
- Entidades auxiliares.

Si el IR aún no puede representar un elemento, debe conservarse en una zona de extensiones/opaque payload o registrarse como pérdida explícita. No descartarlo silenciosamente.

### 6.4 No asumir equivalencia de herencia

El código xmind-model aporta evidencia de perfiles Theme, familias class y estilos locales. No aporta una especificación completa y actual del algoritmo de herencia del motor de escritorio.

Se mantiene la decisión vigente:

- propiedad ausente;
- valor explícito;
- valor literal inherited;
- regla de herencia PMD por primer hijo como convención propia, no como comportamiento nativo demostrado.

## 7. Qué puede considerarse evidencia y qué no

| Afirmación | Estado |
|---|---|
| xmind-sdk-js es presentado por XMind Ltd. como SDK oficial y tiene licencia MIT | Verificado en README, package.json y metadatos del repositorio |
| xmind-model tiene licencia MIT y es dependencia del SDK | Verificado en package.json |
| xmind-model incluye JSON Schema Draft-07 y modelos de hojas/temas/estilos | Verificado en schemas y TypeScript |
| xmind-generator es un generador oficial de XMind Ltd. y MIT | Verificado en README, package.json y metadatos |
| xmind-generator genera content.json como array de hojas y crea metadata/manifest/recursos | Verificado en serializer.ts |
| Los perfiles Theme, class y style local participan en el modelo de estilo | Verificado en código xmind-model |
| Todos los campos y valores de estos repositorios son compatibles con cualquier XMind Desktop actual | No demostrado |
| El algoritmo completo de herencia visual de XMind está especificado en estos repositorios | No demostrado |
| La estructura ZIP de cualquiera de estos generadores debe copiarse sin cambios en nuestro adaptador | Falso; los perfiles inspeccionados difieren |
| Existe una especificación pública oficial y exhaustiva del formato moderno | No localizada en esta investigación |

## 8. Recomendaciones y siguientes pruebas

1. Mantener xmind-generator como referencia primaria de generación oficial TypeScript para el perfil básico y de recursos, y xmind-sdk-js/xmind-model como referencia histórica de modelo de componentes y estilos.
2. No añadir ninguno como dependencia runtime del proyecto Python por ahora. Utilizarlos como documentación y fixtures de referencia.
3. Crear fixtures de salida del generador oficial y abrirlos/guardarlos en XMind Desktop para la versión objetivo.
4. Comparar el ZIP antes y después del guardado en Desktop para identificar normalizaciones, entradas añadidas/eliminadas y cambios de versión.
5. Probar con fixtures aislados: estilos de tema, class, style local, attached/detached/callout/summary, posición libre/fija, relaciones, límites, imágenes, notas y marcadores.
6. Estudiar específicamente cómo Desktop exporta una tabla de árbol; los repositorios consultados no documentan suficientemente la estructura ni la semántica visual de esa característica.
7. Añadir una matriz de compatibilidad por versión de XMind Desktop y por perfil generador, sin declarar compatibilidad universal.

## 9. Referencias externas

### Repositorios oficiales

- [xmind-sdk-js](https://github.com/xmindltd/xmind-sdk-js)
- [xmind-sdk-js README](https://github.com/xmindltd/xmind-sdk-js/blob/master/README.md)
- [xmind-sdk-js functional tests](https://github.com/xmindltd/xmind-sdk-js/blob/master/test/functional/index.test.ts)
- [xmind-model](https://github.com/xmindltd/xmind-model)
- [xmind-model schemas](https://github.com/xmindltd/xmind-model/tree/master/schemas)
- [xmind-model Topic](https://github.com/xmindltd/xmind-model/blob/master/src/models/topic.ts)
- [xmind-model Sheet](https://github.com/xmindltd/xmind-model/blob/master/src/models/sheet.ts)
- [xmind-model StyleComponent](https://github.com/xmindltd/xmind-model/blob/master/src/models/style-component.ts)
- [xmind-generator](https://github.com/xmindltd/xmind-generator)
- [xmind-generator README](https://github.com/xmindltd/xmind-generator/blob/main/README.md)
- [xmind-generator serializer](https://github.com/xmindltd/xmind-generator/blob/main/src/internal/serializer.ts)

### Documentación interna relacionada

- [Formato JSON XMind](xmind-json-format.md).
- [Análisis Tema1](reference-analysis-tema1.md).
- [Intercambio Markdown XMind](xmind-markdown-behavior.md).
- [Arquitectura](architecture.md).
- [Diseño PMD](pmd-design.md).
- [Hoja de ruta](roadmap.md).


## 10. XMindMark: lenguaje oficial de marcado para mapas mentales

### 10.1 Identificación y vigencia

- Repositorio: https://github.com/xmindltd/xmindmark
- Especificación: https://github.com/xmindltd/xmindmark/blob/main/docs/specification.md
- Código del parser: https://github.com/xmindltd/xmindmark/blob/main/src/parser/mindmark.ts
- Modelo/constructor: https://github.com/xmindltd/xmindmark/blob/main/src/parser/mindmap.ts
- Conversor XMindMark → XMind: https://github.com/xmindltd/xmindmark/blob/main/src/lib/xmindmark-to-xmind.ts
- Conversor XMind → XMindMark: https://github.com/xmindltd/xmindmark/blob/main/src/lib/xmind-to-xmindmark.ts
- Licencia: MIT.
- Implementación TypeScript; package.json observado: xmindmark 0.3.2, TypeScript ^4.5.4.
- Autor declarado: XMind Ltd.
- Último push consultado: 2022-05-17.

Este repositorio encaja especialmente bien con la descripción de un proyecto TypeScript/MIT de XMind relacionado con Markdown. XMindMark se define como un lenguaje ligero para mapas mentales inspirado en Markdown. Es una referencia oficial de sintaxis y conversión, aunque antigua y de alcance limitado.

### 10.2 Gramática documentada

La especificación establece:

- La primera línea no vacía es el tema central.
- Los temas subordinados se escriben con guion o asterisco y espacio.
- La indentación expresa niveles; una tabulación equivale a cuatro espacios.
- Las relaciones se marcan mediante identificadores [n] y [^n]; opcionalmente se añade título.
- Los límites se marcan con [B], [B1], etc. y pueden recibir título en una línea posterior.
- Los resúmenes se marcan con [S], [S1], etc.; el título del resumen se declara en una línea posterior y puede tener subtemas.
- La especificación indica que los temas flotantes no están soportados.

No es CommonMark/GFM completo. Tampoco ofrece una sintaxis general para estilos por nodo, roles semánticos, celdas, tablas de árbol o reglas de herencia visual.

### 10.3 Cómo genera content.json

El parser crea una hoja con:

- id, class = sheet, title.
- rootTopic con id, class = topic, title, structureClass y titleUnedited.
- topicPositioning = fixed.
- relationships como colección de hoja.

Los temas se crean en children.attached. Para límites, el parser guarda boundaries con range por índices de hijos. Para resúmenes, crea simultáneamente un tema en children.summary y un elemento en summaries que contiene range y topicId. Las relaciones se guardan en la hoja con end1Id, end2Id y title.

El constructor aplica un Theme predefinido directamente en código. Ese Theme incluye perfiles map, centralTopic, mainTopic, subTopic, summaryTopic, calloutTopic, floatingTopic, boundary, summary, relationship, importantTopic, minorTopic y expiredTopic, con propiedades técnicas XMind. También añade una extensión provider org.xmind.ui.skeleton.structure.style que declara estructura para centralTopic y mainTopic.

Esto es una evidencia práctica de tres mecanismos diferenciados:
- estructura del mapa mediante structureClass;
- perfiles visuales mediante theme;
- extensiones mediante extensions/provider/content.

La sintaxis de XMindMark no expresa esos detalles de estilo; el conversor los incorpora por defecto.

### 10.4 Tablas y estructuras especiales

El código contiene un helper makeKeyValueTable que:

- establece structureClass = org.xmind.ui.spreadsheet;
- añade una extensión con provider org.xmind.ui.spreadsheet y metadatos de columnas;
- crea pares clave/valor como temas subordinados anidados.

Es una pista útil de cómo esta implementación construye una estructura de hoja de cálculo/matriz, pero **no es la tabla de árbol de Tema1**. No demuestra cómo generar org.xmind.ui.treetable.toptitle ni cómo se construyen las celdas treeTableCell. Tampoco forma parte de la gramática textual publicada.

Conclusión: XMindMark confirma que XMind ha usado extensiones y structureClass para construir estructuras distintas del árbol normal, pero no resuelve nuestro caso principal de tabla de árbol legislativa.

### 10.5 Contenedor ZIP y SVG

El conversor XMindMark → XMind genera un ZIP con:

- content.json, cuyo valor es un array de hojas.
- manifest.json con file-entries para content.json y metadata.json.
- metadata.json con objeto vacío.

En el código inspeccionado no se añaden mimetype ni miniatura. La compresión usada es DEFLATE nivel 6. Es otro perfil histórico de generación y no debe copiarse automáticamente al adaptador actual.

Para producir SVG, el proyecto descarga y ejecuta Snowbrush 2.47.0 desde assets.xmind.net dentro de Chromium/Puppeteer. Esto documenta que esa versión del proyecto delega el renderizado en un motor de XMind, pero no expone la implementación de Snowbrush ni define una API pública estable para reproducir su layout.

### 10.6 Conversión inversa y pérdidas

XMindMark incluye un conversor XMind → XMindMark que abre el ZIP y lee content.json. Recorre principalmente attached y summary; representa relaciones, límites y resúmenes mediante marcadores textuales.

La implementación no conserva en esa conversión toda la información de un libro XMind: no reconstruye estilos, Theme, markers, imágenes, notas, extensiones, geometría ni todas las clases de hijos. La generación textual de etiquetas aparece desactivada en el código consultado. Por tanto, es una conversión parcial y con pérdida, no un round-trip completo.

### 10.7 Relevancia para PMD

XMindMark aporta precedentes y lecciones:

1. La sintaxis de mapas puede ser mucho más simple que el JSON XMind.
2. Los marcadores textuales pueden representar relaciones, límites y resúmenes sin exponer el formato interno.
3. El conversor puede aplicar un Theme predeterminado sin que el usuario escriba propiedades visuales.
4. Las estructuras especiales necesitan datos JSON adicionales (ranges, summary topic, extensions).
5. La conversión inversa requiere declarar explícitamente qué información se pierde.

PMD debe ir más allá de XMindMark en el caso de uso del proyecto: semántica legislativa, roles, tabla de árbol, biblioteca de estilos consultable por IA, defaults, excepciones, herencia y propiedades por celda. No conviene adoptar la gramática XMindMark como base sin ampliaciones; sí debe mantenerse como referencia oficial comparativa.

## 11. XMind CLI y Skill oficial para agentes

### 11.1 Repositorio y alcance

- Repositorio: https://github.com/xmindltd/xmind-cli
- README: https://github.com/xmindltd/xmind-cli/blob/main/README.md
- Skill: https://github.com/xmindltd/xmind-cli/blob/main/skills/xmind-file/SKILL.md
- Licencia: MIT.
- El repositorio público distribuye principalmente el punto de entrada del Skill y su configuración de plugin.
- El CLI se publica por separado como paquete npm @xmindltd/xmind-cli.
- Última actualización del repositorio consultada: agosto de 2026.

No se ha inspeccionado código fuente del serializador del CLI en este repositorio. Por tanto, su README y Skill son documentación operativa oficial, no evidencia directa de la estructura interna de content.json.

### 11.2 Flujo oficial de trabajo con agentes

El README describe capacidades para:

- Generar mapas nativos desde especificaciones semánticas o Markdown.
- Leer y describir libros existentes.
- Añadir, actualizar, borrar y editar temas en lote.
- Aplicar estructuras, temas, layouts, marcadores, etiquetas, enlaces e imágenes.
- Validar archivos XMind.

El Skill separa responsabilidades: el agente aporta criterio semántico, receta y estrategia visual; el CLI ejecuta la generación, edición, adjuntos, imágenes y validación. Para obtener la gramática y recetas vigentes, indica consultar el catálogo y los recursos mediante comandos del CLI (por ejemplo, skill list y skill show markdown-grammar).

Es relevante para nuestra arquitectura IA → PMD → IR porque confirma una separación similar entre interpretación semántica y ejecución mecánica. Sin embargo, el repositorio no publica el detalle completo del compilador ni el esquema interno de generación.

### 11.3 Precauciones

- El repositorio Skill no equivale al repositorio fuente del CLI.
- No deducir el lenguaje ni la implementación interna del paquete npm a partir de este repositorio.
- No tratar las recetas dinámicas ni el JSON de generación como formato de almacenamiento XMind.
- Sus instrucciones de uso son una referencia de producto actual, pero no sustituyen los fixtures de XMind Desktop ni los esquemas históricos.

