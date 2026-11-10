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

El flujo implementado actualmente termina en el adaptador JSON. La exportación .xmind es un objetivo futuro, no una capacidad ya disponible.

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

Carga YAML y resuelve nombres simbólicos. El conjunto de estilos puede heredarse por la rama del árbol. Las propiedades resultantes deben ser neutrales: por ejemplo, font_size, font_weight o shape, no nombres de campos internos de una versión concreta de XMind.

La resolución actual no implementa combinación de estilos ni herencia individual de propiedades.

### 3.5 Adaptadores

Directorio: src/xmind_md/adapters/.

Un adaptador convierte el modelo intermedio en una representación externa. El adaptador JSON actual es útil para depuración, inspección y pruebas. Un futuro adaptador XMind debe traducir las propiedades neutrales a la estructura soportada por la versión elegida de XMind.

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
- GitHub Actions para integración continua.

## 6. Extensiones previstas

Orden recomendado:

1. Consolidar y versionar la gramática.
2. Ampliar el modelo intermedio con notas, etiquetas, marcadores, enlaces, imágenes, relaciones, boundaries y summaries.
3. Definir un esquema neutral de estilos y validarlo.
4. Incorporar pruebas de fixtures para cada característica.
5. Implementar un adaptador XMind contra una versión/formato objetivo documentado.
6. Abrir los archivos generados con XMind real y comprobar su estructura y presentación.
7. Añadir exportadores alternativos solo cuando exista una necesidad concreta.

## 7. Criterio para aceptar cambios

Un cambio de arquitectura debe incluir:

- La responsabilidad exacta del módulo afectado.
- Cambios en el modelo intermedio si se introduce un nuevo concepto.
- Pruebas positivas y negativas.
- Actualización de documentación y ejemplos.
- Confirmación explícita de qué está implementado y qué queda pendiente.
