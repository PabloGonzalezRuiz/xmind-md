# Arquitectura de XMind MD

## 1. Propósito

XMind MD permite describir mapas mentales en Markdown enriquecido y transformar esa descripción en formatos de mapa mental. El primer formato objetivo es .xmind, pero el núcleo no debe depender de XMind ni de una biblioteca de exportación concreta.

La arquitectura separa la sintaxis de entrada, el modelo semántico y la serialización. Esta separación permite cambiar la biblioteca de exportación sin reescribir el parser ni los documentos fuente.

## 2. Flujo de datos

~~~text
Markdown enriquecido
       |
       v
     parser.py
       |
       v
     model.py  -----> modelo intermedio (MindMap / Topic)
       |                         |
       v                         v
   styles.py               adaptadores/
       |                         |
       +-------------------------+
                                 |
                     JSON / XMind / otros
~~~

El proyecto dispone de dos salidas: JSON de inspección y una primera versión del adaptador .xmind. Este último genera ZIP + JSON para un subconjunto documentado del IR; su compatibilidad con XMind Desktop todavía no está verificada.

## 3. Capas y responsabilidades

### 3.1 Documento fuente

Los documentos de entrada viven normalmente en examples/ durante el desarrollo. La sintaxis actual utiliza:

- Encabezados Markdown de nivel 1 a 6 como jerarquía de temas.
- @conjunto(NOMBRE) para elegir un conjunto de estilos.
- @estilo(NOMBRE) para elegir un estilo concreto.

La gramática está descrita en grammar.md.

### 3.2 Parser

Archivo: src/xmind_md/parser.py.

Responsabilidades:

- Reconocer encabezados y directivas.
- Construir la jerarquía de temas conservando el orden.
- Asociar las directivas al siguiente encabezado.
- Guardar el texto no estructural como contenido del tema.
- Producir errores explícitos cuando la entrada no cumple la gramática.

No debe conocer la estructura interna de un archivo XMind ni importar bibliotecas de exportación.

### 3.3 Modelo intermedio

Archivo: src/xmind_md/model.py.

Clases:

- MindMap: documento y conjunto de temas raíz.
- Topic: título, nivel, hijos, contenido y referencias/propiedades de estilo.

El modelo es el contrato entre parser, resolución de estilos y adaptadores. Las ampliaciones futuras (notas, enlaces, imágenes, marcadores, relaciones, límites, resúmenes y temas flotantes) deben representarse aquí de forma neutral.

### 3.4 Resolución de estilos

Archivo: src/xmind_md/styles.py.

Carga YAML y resuelve nombres simbólicos. `resolve_styles()` conserva la ruta legacy y despacha los documentos IR 1.0.0 a `resolve_ir_styles()`. En el IR, el conjunto puede seleccionarse en `metadata.style_set` o en `Topic.style.style_set`; se hereda por la rama y puede sustituirse en un tema descendiente. La cascada combina recursivamente, por propiedad: valores predeterminados del sistema, `metadata.style_defaults`, conjunto aplicable, estilo nombrado y overrides locales. También resuelve estilos de notas, relaciones, límites y resúmenes. No modifica las definiciones originales; escribe el resultado en `style.resolved`. Las propiedades resultantes deben ser neutrales: por ejemplo, font_size, font_weight o shape, no nombres de campos internos de una versión concreta de XMind.

### 3.5 Adaptadores

Directorio: src/xmind_md/adapters/.

Un adaptador convierte el modelo intermedio en una representación externa. El adaptador JSON es útil para depuración, inspección y pruebas. El adaptador XMind inicial (`adapters/xmind_adapter.py`) genera el formato moderno ZIP + JSON en Python. Traduce temas, relaciones, notas, etiquetas, marcadores, un enlace por tema y un subconjunto de estilos. Rechaza explícitamente recursos, boundaries, summaries, extensiones, temas detached y propiedades de estilo no reconocidas. El contrato y las limitaciones están descritos en xmind-adapter.md; la decisión de motor, en xmind-engine-evaluation.md.

No se debe introducir lógica de parsing Markdown en un adaptador.

### 3.6 CLI

Archivo: src/xmind_md/cli.py.

Orquesta las fases: lectura, parsing, resolución opcional de estilos y escritura JSON. Debe seguir siendo una capa fina: la lógica de negocio pertenece a los módulos especializados.

### 3.7 Automatización y calidad

- tests/: pruebas unitarias.
- .github/workflows/ci.yml: instala el paquete y ejecuta pytest.
- pyproject.toml: metadatos, dependencias y configuración de herramientas.

## 4. Contratos e invariantes

1. El parser produce un MindMap, no un archivo XMind.
2. El modelo intermedio no importa bibliotecas de exportación.
3. El orden de temas y subtemas debe conservarse.
4. Los metadatos se asocian al siguiente encabezado.
5. Un conjunto explícito reemplaza el conjunto heredado en esa rama.
6. Los nombres de estilos son referencias simbólicas; las propiedades resueltas se almacenan aparte.
7. Cada adaptador recibe el modelo intermedio y no debe modificar la gramática.
8. La salida debe ser determinista para una misma entrada y configuración.
9. Las capacidades no implementadas deben documentarse como pendientes, nunca presentarse como funcionales.

## 5. Decisiones técnicas actuales

- Python >= 3.10.
- Diseño de paquete src/.
- PyYAML como dependencia de ejecución.
- pytest y Ruff como dependencias de desarrollo.
- JSON como formato de inspección del modelo.
- Formato de salida: XMind moderno basado en content.json; adaptador inicial implementado, compatibilidad con la aplicación pendiente de verificación.
- Motor seleccionado: serialización ZIP + JSON nativa en Python; los SDK externos son referencias, no dependencias obligatorias.
- GitHub Actions para integración continua.

## 6. Extensiones previstas

Orden recomendado:

1. Consolidar y versionar la gramática.
2. Ampliar el modelo intermedio con notas, etiquetas, marcadores, enlaces, imágenes, relaciones, boundaries y summaries.
3. Definir un esquema neutral de estilos y validarlo.
4. Incorporar pruebas de fixtures para cada característica.
5. Ampliar el adaptador XMind Python para cubrir recursos, boundaries, summaries, estilos y extensiones de forma incremental.
6. Abrir los archivos generados con XMind Desktop y comprobar su estructura y presentación; mantener esta verificación separada de las pruebas ZIP/JSON.
7. Añadir fixtures reales de archivos guardados desde XMind y pruebas de integración.
8. Integrar el adaptador en la CLI cuando el contrato de exportación esté estabilizado.
9. Añadir exportadores alternativos solo cuando exista una necesidad concreta.

## 7. Criterio para aceptar cambios

Un cambio de arquitectura debe incluir:

- La responsabilidad exacta del módulo afectado.
- Cambios en el modelo intermedio si se introduce un nuevo concepto.
- Pruebas positivas y negativas.
- Actualización de documentación y ejemplos.
- Confirmación explícita de qué está implementado y qué queda pendiente.
