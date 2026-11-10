# Arquitectura de XMind MD

## 1. Propósito

XMind MD permite describir mapas mentales en Markdown enriquecido y transformar esa descripción en formatos de mapa mental. El primer formato objetivo es .xmind, pero el núcleo no debe depender de XMind ni de una biblioteca de exportación concreta.

La arquitectura separa la sintaxis de entrada, el modelo semántico, la resolución de estilos y la serialización. El IR 1.0.0 es el contrato canónico entre estas capas.

## 2. Flujo de datos

~~~text
Markdown enriquecido
       |
       v
   parser.py
       |
       v
 ir_parser.py
       |
       v
    IR 1.0.0
       |
       +------> styles.py (resuelve StyleState.resolved)
       |
       +------> adapters/json_adapter.py
       |
       +------> adapters/xmind_adapter.py
                    |
                    v
                 .xmind
~~~

El parser actual conserva una API legacy por compatibilidad, pero los adaptadores JSON y XMind reciben ya el modelo canónico. La CLI JSON y el script de smoke test utilizan \`parse_file_ir()\`.

## 3. Capas y responsabilidades

### 3.1 Documento fuente

Los documentos de entrada viven normalmente en examples/ durante el desarrollo. La sintaxis actual utiliza:

- Encabezados Markdown de nivel 1 a 6 como jerarquía de temas.
- @conjunto(NOMBRE) para elegir un conjunto de estilos.
- @estilo(NOMBRE) para elegir un estilo concreto.

La gramática está descrita en grammar.md; su cobertura completa sigue pendiente.

### 3.2 Parser y puente IR

- \`src/xmind_md/parser.py\`: reconoce la sintaxis actual y conserva la API legacy.
- \`src/xmind_md/ir_parser.py\`: convierte el resultado a \`MindMap.sheet.root_topic\`, bloques estructurados, anotaciones, recursos, estilos, enlaces y entidades de hoja.

El parser no conoce el formato interno de XMind ni importa bibliotecas de exportación.

### 3.3 Modelo intermedio

Directorio: \`src/xmind_md/ir/\`.

El modelo canónico contiene \`MindMap\`, \`Sheet\`, \`Topic\`, \`ContentBlock\`, anotaciones, recursos, relaciones, límites, resúmenes y estados de estilo. La serialización JSON sigue el contrato IR 1.0.0.

El módulo \`src/xmind_md/model.py\` sigue existiendo como modelo legacy para la API anterior. No es el contrato consumido por los adaptadores ya migrados.

### 3.4 Resolución de estilos

Archivo: \`src/xmind_md/styles.py\`.

\`resolve_styles()\` despacha documentos IR 1.0.0 a \`resolve_ir_styles()\` y conserva la ruta legacy. En el IR, el conjunto puede seleccionarse en \`metadata.style_set\` o en \`Topic.style.style_set\`; se hereda por la rama y puede sustituirse en un tema descendiente. La cascada combina recursivamente, por propiedad: valores predeterminados del sistema, \`metadata.style_defaults\`, conjunto aplicable, estilo nombrado y overrides locales. También resuelve estilos de notas, relaciones, límites y resúmenes. No modifica las definiciones originales; escribe el resultado en \`style.resolved\`.

### 3.5 Adaptadores

Directorio: \`src/xmind_md/adapters/\`.

- \`json_adapter.py\`: serializa exclusivamente el documento IR mediante \`MindMap.to_dict()\`.
- \`xmind_adapter.py\`: genera ZIP + JSON moderno a partir de \`MindMap.sheet\` y de las entidades canónicas.

Ambos adaptadores importan el IR, no \`src/xmind_md/model.py\`. El adaptador XMind consume estilos ya resueltos y rechaza capacidades que todavía no puede representar. Su perfil y limitaciones están documentados en [xmind-adapter.md](xmind-adapter.md).

No se debe introducir lógica de parsing Markdown ni resolución de estilos dentro de un adaptador.

### 3.6 CLI y herramientas de desarrollo

- \`src/xmind_md/cli.py\`: construye IR mediante \`parse_file_ir()\`, resuelve estilos si se proporciona configuración externa y escribe JSON canónico.
- \`scripts/create_xmind_smoke.py\`: genera un paquete XMind de comprobación a partir de IR.

La CLI todavía no expone la exportación XMind como opción de usuario; esa integración corresponde a una tarea posterior.

### 3.7 Automatización y calidad

- \`tests/\`: pruebas unitarias y de integración.
- \`.github/workflows/ci.yml\`: instala el paquete, ejecuta pytest, genera un archivo XMind smoke y publica el artefacto.
- \`pyproject.toml\`: metadatos, dependencias y configuración de herramientas.

## 4. Contratos e invariantes

1. El parser produce un documento neutral, no un archivo XMind.
2. El IR no importa bibliotecas de exportación.
3. Los adaptadores reciben el modelo canónico IR 1.0.0.
4. El orden de temas y subtemas debe conservarse.
5. Los nombres de estilos son referencias simbólicas; las propiedades resueltas se almacenan aparte.
6. El adaptador no debe resolver estilos ni modificar el IR.
7. La salida debe ser determinista para una misma entrada y configuración, salvo metadatos de creación dependientes del momento.
8. Las capacidades no implementadas deben documentarse y rechazarse explícitamente; no deben presentarse como funcionales.
9. La generación de un ZIP válido no acredita apertura y guardado manual en XMind Desktop.

## 5. Decisiones técnicas actuales

- Python >= 3.10.
- Diseño de paquete src/.
- PyYAML como dependencia de ejecución.
- pytest y Ruff como dependencias de desarrollo.
- IR 1.0.0 como contrato canónico.
- JSON como formato de inspección del IR.
- XMind moderno basado en content.json; perfil inicial implementado, compatibilidad con XMind Desktop pendiente de verificación.
- Serialización ZIP + JSON nativa en Python; los SDK externos son referencias, no dependencias obligatorias.
- GitHub Actions para integración continua.

## 6. Extensiones previstas

1. Completar y validar la gramática Markdown.
2. Validar formalmente el JSON Schema y los ejemplos.
3. Ampliar el adaptador XMind para recursos, imágenes, boundaries, summaries, estilos y extensiones.
4. Integrar la exportación XMind en la CLI.
5. Abrir los archivos generados con XMind Desktop y comprobar su estructura y presentación.
6. Verificar la ejecución local en Windows.
7. Completar CI, Ruff y comprobaciones automáticas.
8. Auditar y publicar una versión estable.

## 7. Criterio para aceptar cambios

Un cambio de arquitectura debe incluir:

- La responsabilidad exacta del módulo afectado.
- Cambios en el modelo intermedio si se introduce un nuevo concepto.
- Pruebas positivas y negativas.
- Actualización de documentación y ejemplos.
- Confirmación explícita de qué está implementado y qué queda pendiente.
