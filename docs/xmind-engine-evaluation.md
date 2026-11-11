# Evaluación y decisión del motor XMind

**Fecha:** 2026-11-10  
**Fase:** decisión técnica y adaptador implementados; evaluación de capacidades y mantenimiento documental  
**Estado:** decisión de arquitectura aplicada en una primera versión del adaptador; pruebas CI y compatibilidad real con XMind Desktop pendientes de confirmación

## 1. Objetivo y criterios

Seleccionar una estrategia para generar archivos `.xmind` desde el IR de XMind MD.

Criterios, por orden de importancia:

1. Compatibilidad con el formato moderno de XMind (XMind 2020 y posteriores).
2. Control preciso de propiedades visuales y estructurales: temas, texto enriquecido, relaciones, límites, resúmenes, marcadores, imágenes y temas de mapa.
3. Correspondencia directa con el IR neutral y sus extensiones.
4. Ejecución principal en Python y compatibilidad con Windows y GitHub Actions.
5. Dependencias reducidas, mantenimiento razonable y pruebas reproducibles.
6. Posibilidad de inspeccionar y validar el archivo generado sin depender de la interfaz gráfica.

El proyecto no necesita abrir ni editar mapas XMind existentes como función principal. Su objetivo inicial es producirlos a partir de Markdown.

## 2. Formato de destino

El objetivo inicial será el formato moderno basado en JSON utilizado por XMind 2020+.

La estructura del archivo es un contenedor ZIP. Sus partes principales son:

- `content.json`: hojas, temas, relaciones y propiedades de contenido.
- `metadata.json`: metadatos y versiones de estructura.
- `manifest.json`: registro de archivos del paquete.
- `mimetype`: tipo MIME del documento.
- `Thumbnails/`: miniatura, cuando se incluya.
- `resources/`: imágenes y otros recursos binarios, cuando se incluyan.

El SDK oficial de JavaScript genera `content.json`, `metadata.json`, `manifest.json` y un `content.xml` auxiliar. La implementación Python reciente `xmindpy` documenta además `mimetype` y una miniatura. La combinación exacta de entradas y sus requisitos debe verificarse con archivos reales guardados por la versión de XMind que usemos como referencia.

No se implementará inicialmente el formato XML legado de XMind 8. Si se necesitara, será un adaptador separado.

## 3. Alternativas evaluadas

### 3.1 SDK oficial Python: `xmind-sdk-python`

**Resultado: descartado como motor de salida.**

- Es el SDK oficial histórico para Python.
- El repositorio está archivado.
- Su último envío de código es de 2018.
- Está asociado al modelo XML anterior al formato moderno basado en JSON.

No satisface el requisito de generar directamente el formato moderno. No debe añadirse como dependencia del proyecto.

Repositorio: https://github.com/xmindltd/xmind-sdk-python

### 3.2 SDK oficial JavaScript/TypeScript: `xmind` (`xmindltd/xmind-sdk-js`)

**Resultado: referencia técnica importante; no se adopta como dependencia de ejecución.**

Ventajas:

- Es el SDK oficial de XMind y tiene licencia MIT.
- Funciona en Node.js y Windows.
- Genera archivos `.xmind` sin abrir la aplicación.
- Ofrece operaciones para crear hojas, temas, notas, etiquetas, marcadores, imágenes y resúmenes.
- Incluye validación del modelo.
- Su modelo TypeScript declara propiedades para estilos de tema, relaciones, límites, resúmenes, imágenes y extensiones.
- El objeto de estilo permite expresar un tipo y un conjunto de propiedades.

Limitaciones:

- Introduce Node.js y un segundo ecosistema de dependencias en un proyecto cuyo núcleo es Python.
- La API de alto nivel no cubre con la misma comodidad todas las entidades del modelo; algunas capacidades requerirían trabajar directamente con el modelo interno.
- Los temas incorporados expuestos por su clase `Theme` son un conjunto reducido; no sustituyen nuestro sistema neutral de estilos.
- La documentación de alto nivel se concentra en temas, notas, marcadores, imágenes y resúmenes.
- La versión publicada más reciente identificada es 2.2.33, del 29-09-2023; el último envío de código identificado en el repositorio es de 2024. No debe confundirse que siga disponible con que tenga desarrollo frecuente.
- La carga de archivos existentes fue retirada en la versión 2.2.0; no es una solución general para leer y modificar cualquier archivo.

Uso previsto en XMind MD:

- Referencia de estructuras y convenciones del formato.
- Fuente para contrastar nombres de propiedades y modelos.
- Posible herramienta auxiliar en pruebas de interoperabilidad, si resulta conveniente.
- No será una dependencia necesaria para ejecutar el exportador.

Repositorio: https://github.com/xmindltd/xmind-sdk-js

### 3.3 Biblioteca Python comunitaria: `xmindpy`

**Resultado: candidata útil para contrastes y pruebas; no se adopta como dependencia principal.**

Ventajas:

- Es Python nativo y apunta al formato JSON de XMind 2020+.
- Tiene licencia MIT declarada.
- Puede crear, cargar y guardar libros de trabajo.
- Conserva campos JSON desconocidos al volver a guardar un archivo.
- Tiene pruebas automatizadas y workflow de CI.

Limitaciones y riesgos:

- La versión consultada es 0.1.0, con lanzamiento inicial el 10-09-2026.
- Es un proyecto muy reciente y con una base de usuarios todavía pequeña.
- Su API tipada cubre principalmente hojas, temas, hijos, notas, etiquetas, marcadores, enlaces y un identificador de estilo.
- Relaciones se exponen como diccionarios; límites, resúmenes, callouts, temas y estilos avanzados no disponen de una API de construcción equivalente a la amplitud del IR.
- La preservación de campos desconocidos es valiosa al leer y volver a guardar, pero no equivale a una implementación semántica de esas características.
- No resuelve por sí misma la traducción del sistema de estilos neutral de XMind MD a las propiedades internas de XMind.

Uso previsto:

- Consultar su estructura de paquete y su estrategia de serialización.
- Comparar archivos de prueba generados.
- No acoplar el IR a sus clases ni a su API.

Repositorio: https://github.com/innotools/xmindpy

### 3.4 Escritura nativa Python del contenedor y del JSON

**Resultado: alternativa seleccionada.**

La salida se implementará en Python utilizando inicialmente la biblioteca estándar:

- `zipfile` para crear el contenedor.
- `json` para serializar `content.json`, metadatos y manifiesto.
- `pathlib` para gestionar rutas.
- Validación estructural y semántica antes de empaquetar.

Ventajas:

- No requiere Node.js ni una dependencia externa de generación.
- Permite traducir directamente cada entidad del IR.
- Permite conservar control explícito sobre estilos, extensiones y propiedades aún no cubiertas por una biblioteca.
- Mantiene el adaptador aislado y sustituible.
- Facilita pruebas unitarias de JSON y ZIP, y pruebas de integración con XMind.

Costes y riesgos:

- XMind MD será responsable de la serialización y de las reglas de compatibilidad.
- El formato no debe tratarse como una especificación completamente estable ni como un contrato que se pueda inferir solo de nombres de propiedades.
- Será necesario contrastar la salida con muestras creadas por XMind y abrirla en la aplicación.
- Las propiedades no reconocidas por la versión objetivo deben conservarse o rechazarse de forma explícita; no se deben emitir silenciosamente.

## 4. Comparación resumida

| Criterio | SDK Python oficial antiguo | SDK JS oficial | xmindpy | Python nativo |
|---|---|---|---|---|
| Formato moderno JSON | No es su objetivo | Sí | Sí | Sí, a implementar |
| Ejecución desde Python | Sí | Requiere Node.js | Sí | Sí |
| API avanzada de estilos | Modelo antiguo | Modelo de estilo disponible; API parcial | Muy limitada | Control directo |
| Relaciones / límites / resúmenes | Modelo antiguo | Modelos declarados; cobertura desigual | Parcial / datos sin abstracción completa | Control directo |
| Dependencias de ejecución | Paquete antiguo | Node.js y npm | Ninguna declarada | Biblioteca estándar |
| Madurez observada | Archivado | SDK oficial, pero actividad reciente limitada | Proyecto nuevo | Depende de nuestras pruebas |
| Decisión | Descartar | Referencia | Referencia | **Seleccionar** |

## 5. Modelo de estilos de XMind

La documentación actual de XMind indica que se pueden aplicar estilos a:

- Temas.
- Relaciones.
- Límites.
- Resúmenes.
- Callouts.

Las propiedades visuales incluyen, entre otras, forma, relleno, borde, tipografía, color de texto, grosor y patrón de línea, extremos y disposición.

El modelo del SDK oficial representa los estilos mediante objetos con identificador, tipo y propiedades. Los nombres de propiedades visibles en los temas oficiales incluyen convenciones como:

- `fo:font-family`
- `fo:font-size`
- `fo:font-weight`
- `fo:color`
- `svg:fill`
- `shape-class`
- `line-color`
- `line-width`
- `line-pattern`

Estas claves son específicas del formato de salida. No deben filtrarse al parser ni al IR neutral. La traducción se hará dentro del adaptador mediante un catálogo versionado de propiedades.

La documentación y los esquemas del paquete `xmind-model` se utilizarán como material de referencia, no como dependencia de ejecución. Se han observado discrepancias entre sus interfaces TypeScript y algunos esquemas JSON (por ejemplo, el nombre de un extremo de relación y campos de estilo de entidades); por tanto, no se usarán esos esquemas como única fuente de verdad.

## 6. Decisión técnica

Se adopta la siguiente arquitectura:

```text
Markdown
   |
   v
Parser Python
   |
   v
IR neutral
   |
   v
Resolutor de estilos
   |
   v
XMindAdapter (Python)
   |-- traducción de entidades
   |-- traducción de estilos
   |-- validación del modelo XMind
   |-- serialización JSON
   |-- empaquetado ZIP
   v
archivo .xmind (formato moderno)
```

Reglas:

1. El adaptador se implementará en Python.
2. No se añadirá `xmindpy` ni el SDK JavaScript como dependencia obligatoria.
3. El adaptador no modificará el IR.
4. Las claves y valores internos de XMind se mantendrán exclusivamente en el adaptador y sus catálogos.
5. El primer destino será XMind 2020+ con `content.json`.
6. El proyecto no generará temas flotantes: todo tema emitido deberá pertenecer al árbol, conforme a la decisión del IR.
7. Las entidades no soportadas se rechazarán con un diagnóstico claro o se conservarán en una extensión expresamente definida; nunca se descartarán silenciosamente.
8. La compatibilidad se declarará por característica y versión objetivo, no como compatibilidad total genérica.

## 7. Plan de verificación del adaptador

La primera implementación del paso 7 ya contiene:

1. Una hoja y un tema raíz.
2. Temas hijos anidados e IDs UUID5 deterministas derivados de los IDs del IR.
3. Notas, etiquetas y marcadores.
4. Un subconjunto de estilos de tema.
5. Escritura ZIP con `mimetype`, `content.json`, `metadata.json`, `manifest.json` y miniatura.
6. Relaciones con extremos traducidos a los IDs de salida (mapeo provisional: falta `controlPoints`, que exige el esquema oficial).
7. Pruebas unitarias para JSON, ZIP, IDs, relaciones, estilos y rechazo de características no soportadas.

**Pendiente de confirmar:** resultado de GitHub Actions tras estos cambios. También está pendiente abrir un archivo generado en XMind Desktop y volver a guardarlo para comprobar interoperabilidad real.

**Fuera del alcance de esta primera versión:** recursos/imágenes, boundaries, summaries, temas detached, callouts, extensiones, notas HTML enriquecidas, varios enlaces por tema y propiedades de estilo no incluidas en el catálogo inicial. El detalle está en [xmind-adapter.md](xmind-adapter.md).

La prueba con XMind real es condición necesaria. Que el ZIP sea válido o que el JSON pase pruebas estructurales no demuestra que XMind acepte o represente correctamente el archivo.

## 8. Fuentes técnicas

- SDK oficial Python (archivado): https://github.com/xmindltd/xmind-sdk-python
- SDK oficial JavaScript/TypeScript: https://github.com/xmindltd/xmind-sdk-js
- Versiones del SDK oficial JS: https://github.com/xmindltd/xmind-sdk-js/releases
- Modelo y esquemas de referencia: https://github.com/xmindltd/xmind-model
- Biblioteca Python comunitaria: https://github.com/innotools/xmindpy
- Guía oficial de estilos: https://xmind.com/user-guide/style-new
- Guía oficial de relaciones: https://xmind.com/user-guide/relationship-new
- Guía oficial de importación: https://xmind.com/user-guide/import-new

## 9. Resultado del paso

**Decisión tomada:** escritura nativa Python del formato moderno ZIP + JSON, usando el SDK y el modelo oficial como referencias técnicas.

**Implementado inicialmente:** adaptador Python, generación del paquete ZIP + JSON, árbol jerárquico, IDs estables, notas, etiquetas, marcadores y subconjunto de estilos. Las relaciones tienen un mapeo inicial de extremos, pero todavía no incorporan `controlPoints` y no deben considerarse interoperables. Se han añadido pruebas automatizadas para el adaptador; el resultado CI de esta iteración debe consultarse antes de declarar las pruebas superadas.

**Pendiente:** integración en CLI, recursos/imágenes, boundaries, summaries, callouts, extensiones, mayor cobertura de estilos y, especialmente, apertura y guardado de un archivo generado en XMind Desktop. No se declara compatibilidad completa con XMind hasta superar esa prueba.
# Evaluación y decisión del motor XMind

**Fecha:** 2026-11-10  
**Fase:** paso 6 de la hoja de ruta  
**Estado:** decisión aplicada; CI operativa y fixture manual abierto/guardado/reabierto en XMind Desktop 26.05.01107

## 1. Objetivo y criterios

Seleccionar una estrategia para generar archivos `.xmind` desde el IR de XMind MD.

Criterios, por orden de importancia:

1. Compatibilidad con el formato moderno de XMind (XMind 2020 y posteriores).
2. Control preciso de propiedades visuales y estructurales: temas, texto enriquecido, relaciones, límites, resúmenes, marcadores, imágenes y temas de mapa.
3. Correspondencia directa con el IR neutral y sus extensiones.
4. Ejecución principal en Python y compatibilidad con Windows y GitHub Actions.
5. Dependencias reducidas, mantenimiento razonable y pruebas reproducibles.
6. Posibilidad de inspeccionar y validar el archivo generado sin depender de la interfaz gráfica.

El proyecto no necesita abrir ni editar mapas XMind existentes como función principal. Su objetivo inicial es producirlos a partir de Markdown.

## 2. Formato de destino

El objetivo inicial será el formato moderno basado en JSON utilizado por XMind 2020+.

La estructura del archivo es un contenedor ZIP. Sus partes principales son:

- `content.json`: hojas, temas, relaciones y propiedades de contenido.
- `metadata.json`: metadatos y versiones de estructura.
- `manifest.json`: registro de archivos del paquete.
- `mimetype`: tipo MIME del documento.
- `Thumbnails/`: miniatura, cuando se incluya.
- `resources/`: imágenes y otros recursos binarios, cuando se incluyan.

El SDK oficial de JavaScript genera `content.json`, `metadata.json`, `manifest.json` y un `content.xml` auxiliar. La implementación Python reciente `xmindpy` documenta además `mimetype` y una miniatura. La combinación exacta de entradas y sus requisitos debe verificarse con archivos reales guardados por la versión de XMind que usemos como referencia.

No se implementará inicialmente el formato XML legado de XMind 8. Si se necesitara, será un adaptador separado.

## 3. Alternativas evaluadas

### 3.1 SDK oficial Python: `xmind-sdk-python`

**Resultado: descartado como motor de salida.**

- Es el SDK oficial histórico para Python.
- El repositorio está archivado.
- Su último envío de código es de 2018.
- Está asociado al modelo XML anterior al formato moderno basado en JSON.

No satisface el requisito de generar directamente el formato moderno. No debe añadirse como dependencia del proyecto.

Repositorio: https://github.com/xmindltd/xmind-sdk-python

### 3.2 SDK oficial JavaScript/TypeScript: `xmind` (`xmindltd/xmind-sdk-js`)

**Resultado: referencia técnica importante; no se adopta como dependencia de ejecución.**

Ventajas:

- Es el SDK oficial de XMind y tiene licencia MIT.
- Funciona en Node.js y Windows.
- Genera archivos `.xmind` sin abrir la aplicación.
- Ofrece operaciones para crear hojas, temas, notas, etiquetas, marcadores, imágenes y resúmenes.
- Incluye validación del modelo.
- Su modelo TypeScript declara propiedades para estilos de tema, relaciones, límites, resúmenes, imágenes y extensiones.
- El objeto de estilo permite expresar un tipo y un conjunto de propiedades.

Limitaciones:

- Introduce Node.js y un segundo ecosistema de dependencias en un proyecto cuyo núcleo es Python.
- La API de alto nivel no cubre con la misma comodidad todas las entidades del modelo; algunas capacidades requerirían trabajar directamente con el modelo interno.
- Los temas incorporados expuestos por su clase `Theme` son un conjunto reducido; no sustituyen nuestro sistema neutral de estilos.
- La documentación de alto nivel se concentra en temas, notas, marcadores, imágenes y resúmenes.
- La versión publicada más reciente identificada es 2.2.33, del 29-09-2023; el último envío de código identificado en el repositorio es de 2024. No debe confundirse que siga disponible con que tenga desarrollo frecuente.
- La carga de archivos existentes fue retirada en la versión 2.2.0; no es una solución general para leer y modificar cualquier archivo.

Uso previsto en XMind MD:

- Referencia de estructuras y convenciones del formato.
- Fuente para contrastar nombres de propiedades y modelos.
- Posible herramienta auxiliar en pruebas de interoperabilidad, si resulta conveniente.
- No será una dependencia necesaria para ejecutar el exportador.

Repositorio: https://github.com/xmindltd/xmind-sdk-js

### 3.3 Biblioteca Python comunitaria: `xmindpy`

**Resultado: candidata útil para contrastes y pruebas; no se adopta como dependencia principal.**

Ventajas:

- Es Python nativo y apunta al formato JSON de XMind 2020+.
- Tiene licencia MIT declarada.
- Puede crear, cargar y guardar libros de trabajo.
- Conserva campos JSON desconocidos al volver a guardar un archivo.
- Tiene pruebas automatizadas y workflow de CI.

Limitaciones y riesgos:

- La versión consultada es 0.1.0, con lanzamiento inicial el 10-09-2026.
- Es un proyecto muy reciente y con una base de usuarios todavía pequeña.
- Su API tipada cubre principalmente hojas, temas, hijos, notas, etiquetas, marcadores, enlaces y un identificador de estilo.
- Relaciones se exponen como diccionarios; límites, resúmenes, callouts, temas y estilos avanzados no disponen de una API de construcción equivalente a la amplitud del IR.
- La preservación de campos desconocidos es valiosa al leer y volver a guardar, pero no equivale a una implementación semántica de esas características.
- No resuelve por sí misma la traducción del sistema de estilos neutral de XMind MD a las propiedades internas de XMind.

Uso previsto:

- Consultar su estructura de paquete y su estrategia de serialización.
- Comparar archivos de prueba generados.
- No acoplar el IR a sus clases ni a su API.

Repositorio: https://github.com/innotools/xmindpy

### 3.4 Escritura nativa Python del contenedor y del JSON

**Resultado: alternativa seleccionada.**

La salida se implementará en Python utilizando inicialmente la biblioteca estándar:

- `zipfile` para crear el contenedor.
- `json` para serializar `content.json`, metadatos y manifiesto.
- `pathlib` para gestionar rutas.
- Validación estructural y semántica antes de empaquetar.

Ventajas:

- No requiere Node.js ni una dependencia externa de generación.
- Permite traducir directamente cada entidad del IR.
- Permite conservar control explícito sobre estilos, extensiones y propiedades aún no cubiertas por una biblioteca.
- Mantiene el adaptador aislado y sustituible.
- Facilita pruebas unitarias de JSON y ZIP, y pruebas de integración con XMind.

Costes y riesgos:

- XMind MD será responsable de la serialización y de las reglas de compatibilidad.
- El formato no debe tratarse como una especificación completamente estable ni como un contrato que se pueda inferir solo de nombres de propiedades.
- Será necesario contrastar la salida con muestras creadas por XMind y abrirla en la aplicación.
- Las propiedades no reconocidas por la versión objetivo deben conservarse o rechazarse de forma explícita; no se deben emitir silenciosamente.

## 4. Comparación resumida

| Criterio | SDK Python oficial antiguo | SDK JS oficial | xmindpy | Python nativo |
|---|---|---|---|---|
| Formato moderno JSON | No es su objetivo | Sí | Sí | Sí, a implementar |
| Ejecución desde Python | Sí | Requiere Node.js | Sí | Sí |
| API avanzada de estilos | Modelo antiguo | Modelo de estilo disponible; API parcial | Muy limitada | Control directo |
| Relaciones / límites / resúmenes | Modelo antiguo | Modelos declarados; cobertura desigual | Parcial / datos sin abstracción completa | Control directo |
| Dependencias de ejecución | Paquete antiguo | Node.js y npm | Ninguna declarada | Biblioteca estándar |
| Madurez observada | Archivado | SDK oficial, pero actividad reciente limitada | Proyecto nuevo | Depende de nuestras pruebas |
| Decisión | Descartar | Referencia | Referencia | **Seleccionar** |

## 5. Modelo de estilos de XMind

La documentación actual de XMind indica que se pueden aplicar estilos a:

- Temas.
- Relaciones.
- Límites.
- Resúmenes.
- Callouts.

Las propiedades visuales incluyen, entre otras, forma, relleno, borde, tipografía, color de texto, grosor y patrón de línea, extremos y disposición.

El modelo del SDK oficial representa los estilos mediante objetos con identificador, tipo y propiedades. Los nombres de propiedades visibles en los temas oficiales incluyen convenciones como:

- `fo:font-family`
- `fo:font-size`
- `fo:font-weight`
- `fo:color`
- `svg:fill`
- `shape-class`
- `line-color`
- `line-width`
- `line-pattern`

Estas claves son específicas del formato de salida. No deben filtrarse al parser ni al IR neutral. La traducción se hará dentro del adaptador mediante un catálogo versionado de propiedades.

La documentación y los esquemas del paquete `xmind-model` se utilizarán como material de referencia, no como dependencia de ejecución. Se han observado discrepancias entre sus interfaces TypeScript y algunos esquemas JSON (por ejemplo, el nombre de un extremo de relación y campos de estilo de entidades); por tanto, no se usarán esos esquemas como única fuente de verdad.

## 6. Decisión técnica

Se adopta la siguiente arquitectura:

```text
Markdown
   |
   v
Parser Python
   |
   v
IR neutral
   |
   v
Resolutor de estilos
   |
   v
XMindAdapter (Python)
   |-- traducción de entidades
   |-- traducción de estilos
   |-- validación del modelo XMind
   |-- serialización JSON
   |-- empaquetado ZIP
   v
archivo .xmind (formato moderno)
```

Reglas:

1. El adaptador se implementará en Python.
2. No se añadirá `xmindpy` ni el SDK JavaScript como dependencia obligatoria.
3. El adaptador no modificará el IR.
4. Las claves y valores internos de XMind se mantendrán exclusivamente en el adaptador y sus catálogos.
5. El primer destino será XMind 2020+ con `content.json`.
6. El proyecto no generará temas flotantes: todo tema emitido deberá pertenecer al árbol, conforme a la decisión del IR.
7. Las entidades no soportadas se rechazarán con un diagnóstico claro o se conservarán en una extensión expresamente definida; nunca se descartarán silenciosamente.
8. La compatibilidad se declarará por característica y versión objetivo, no como compatibilidad total genérica.

## 7. Plan de verificación del adaptador

La primera implementación del paso 7 ya contiene:

1. Una hoja y un tema raíz.
2. Temas hijos anidados e IDs UUID5 deterministas derivados de los IDs del IR.
3. Notas, etiquetas y marcadores.
4. Un subconjunto de estilos de tema.
5. Escritura ZIP con `mimetype`, `content.json`, `metadata.json`, `manifest.json` y miniatura.
6. Relaciones con extremos traducidos a los IDs de salida (mapeo provisional: falta `controlPoints`, que exige el esquema oficial).
7. Pruebas unitarias para JSON, ZIP, IDs, relaciones, estilos y rechazo de características no soportadas.

**Pendiente de confirmar:** resultado de GitHub Actions tras estos cambios. También está pendiente abrir un archivo generado en XMind Desktop y volver a guardarlo para comprobar interoperabilidad real.

**Fuera del alcance de esta primera versión:** recursos/imágenes, boundaries, summaries, temas detached, callouts, extensiones, notas HTML enriquecidas, varios enlaces por tema y propiedades de estilo no incluidas en el catálogo inicial. El detalle está en [xmind-adapter.md](xmind-adapter.md).

La prueba con XMind real es condición necesaria. Que el ZIP sea válido o que el JSON pase pruebas estructurales no demuestra que XMind acepte o represente correctamente el archivo.

## 8. Fuentes técnicas

- SDK oficial Python (archivado): https://github.com/xmindltd/xmind-sdk-python
- SDK oficial JavaScript/TypeScript: https://github.com/xmindltd/xmind-sdk-js
- Versiones del SDK oficial JS: https://github.com/xmindltd/xmind-sdk-js/releases
- Modelo y esquemas de referencia: https://github.com/xmindltd/xmind-model
- Biblioteca Python comunitaria: https://github.com/innotools/xmindpy
- Guía oficial de estilos: https://xmind.com/user-guide/style-new
- Guía oficial de relaciones: https://xmind.com/user-guide/relationship-new
- Guía oficial de importación: https://xmind.com/user-guide/import-new

## 9. Resultado del paso

**Decisión tomada:** escritura nativa Python del formato moderno ZIP + JSON, usando el SDK y el modelo oficial como referencias técnicas.

**Implementado inicialmente:** adaptador Python, generación del paquete ZIP + JSON, árbol jerárquico, IDs estables, notas, etiquetas, marcadores y subconjunto de estilos. Las relaciones tienen un mapeo inicial de extremos, pero todavía no incorporan `controlPoints` y no deben considerarse interoperables. Se han añadido pruebas automatizadas para el adaptador; el resultado CI de esta iteración debe consultarse antes de declarar las pruebas superadas.

**Pendiente:** integración en CLI, recursos/imágenes, boundaries, summaries, callouts, extensiones, mayor cobertura de estilos y, especialmente, apertura y guardado de un archivo generado en XMind Desktop. No se declara compatibilidad completa con XMind hasta superar esa prueba.


## 10. Estado actual de la decisión (2026-11-11)

La estrategia seleccionada está implementada: serialización nativa Python del contenedor ZIP y JSON moderno, sin SDK de exportación obligatorio.

El adaptador está conectado a la CLI y recibe IR 1.0.0 con estilos resueltos. La CI de Ubuntu ha ejecutado instalación, Ruff, 131 pruebas, descarga del fixture externo, generación del smoke test y publicación del artefacto. El fixture propio también fue comprobado manualmente en XMind Desktop 26.05.01107 para Windows.

La decisión de arquitectura se considera validada para el perfil y las capacidades que están cubiertas por el código y las pruebas. No implica soporte completo del formato XMind. Recursos/imágenes, boundaries, summaries, tareas, extensiones y varias propiedades avanzadas siguen fuera del perfil exportable; consultar [xmind-adapter.md](xmind-adapter.md).

La CI se mantiene en Ubuntu. No se requiere runner Windows para generar el archivo; la compatibilidad de apertura se contrasta mediante la prueba manual documentada.
