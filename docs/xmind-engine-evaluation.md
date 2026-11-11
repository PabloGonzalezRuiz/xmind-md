# Evaluación y decisión del motor XMind

**Fecha:** 2026-11-10  
**Fase:** decisión técnica y adaptador implementados; evaluación de capacidades y mantenimiento documental  
**Estado:** decisión de arquitectura aplicada y validada para el perfil documentado; esta nota conserva el razonamiento histórico. El estado funcional vigente está en `xmind-adapter.md` y `development-status.md`.

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

## 7. Estado del adaptador y verificación

La implementación actual está integrada en la CLI y cuenta con pruebas unitarias, de integración estructural y smoke de distribución. La CI valida la generación ZIP + JSON y la instalación funcional desde wheel/sdist; esto no equivale a compatibilidad visual completa con XMind Desktop.

Capacidades exportadas: temas `attached`, `detached` (con coordenadas `layout.position.x/y`) y `callout`; notas de texto; etiquetas; marcadores; enlaces web, internos a temas y `file://`; relaciones; y subconjunto de estilos de tema/relación.

No se exportan recursos/imágenes, tareas, boundaries, summaries, extensiones, Topic.kind `summary`, notas con estilo ni propiedades/layout fuera de la lista blanca. Los bloques paragraph/list/table/code/quote/divider se aplanan a texto de nota y pierden parte de su estructura y formato inline. Las imágenes inline se rechazan explícitamente.

El fixture `tests/fixtures/xmind/xmind-md-smoke-test.xmind` se abrió, guardó y reabrió manualmente en XMind Desktop 26.05.01107 para Windows. El smoke actualizado con estilos pasa CI, pero no se ha inspeccionado manualmente de nuevo en Desktop.

La matriz exhaustiva y vigente es [xmind-adapter.md](xmind-adapter.md).

## 8. Fuentes técnicas

- SDK oficial Python (archivado): https://github.com/xmindltd/xmind-sdk-python
- SDK oficial JavaScript/TypeScript: https://github.com/xmindltd/xmind-sdk-js
- Versiones del SDK oficial JS: https://github.com/xmindltd/xmind-sdk-js/releases
- Modelo y esquemas de referencia: https://github.com/xmindltd/xmind-model
- Biblioteca Python comunitaria: https://github.com/innotools/xmindpy
- Guía oficial de estilos: https://xmind.com/user-guide/style-new
- Guía oficial de relaciones: https://xmind.com/user-guide/relationship-new
- Guía oficial de importación: https://xmind.com/user-guide/import-new

## 9. Resultado de la decisión

**Decisión:** serialización nativa Python del contenedor ZIP y JSON moderno, con SDK/modelo oficial como referencias técnicas y sin SDK externo obligatorio en tiempo de ejecución.

**Estado:** adaptador integrado en CLI, con validación explícita de capacidades y pruebas para entidades soportadas/rechazadas. Relaciones incluyen `controlPoints`; no deben confundirse las pruebas estructurales con interoperabilidad visual universal.

**Limitación:** la cobertura es parcial. La matriz de [xmind-adapter.md](xmind-adapter.md) prevalece sobre cualquier descripción histórica de este documento.

## 10. Estado actual de la decisión (2026-11-11)

La estrategia seleccionada está implementada: serialización nativa Python del contenedor ZIP y JSON moderno, sin SDK de exportación obligatorio.

El adaptador está conectado a la CLI y recibe IR 1.0.0 con estilos resueltos. La CI [43009510391](https://github.com/PabloGonzalezRuiz/xmind-md/actions/runs/43009510391) ejecutó Ruff y 161 pruebas por versión en Python 3.10/3.11/3.12, generación de smoke, build de wheel/sdist e instalación y conversiones CLI desde ambas distribuciones. El fixture propio también fue comprobado manualmente en XMind Desktop 26.05.01107 para Windows.

La decisión de arquitectura se considera validada para el perfil y las capacidades que están cubiertas por el código y las pruebas. No implica soporte completo del formato XMind. Recursos/imágenes, boundaries, summaries, tareas, extensiones y varias propiedades avanzadas siguen fuera del perfil exportable; consultar [xmind-adapter.md](xmind-adapter.md).

La CI se mantiene en Ubuntu. No se requiere runner Windows para generar el archivo; la compatibilidad de apertura se contrasta mediante la prueba manual documentada.
