# Prompt maestro para reconstruir y continuar XMind MD

> Este documento está escrito para poder copiarse íntegramente como prompt inicial de otra IA. Incluye el contexto, la arquitectura, los contratos, el estado real y las reglas de trabajo del proyecto.

---

## PROMPT

Actúa como arquitecto de software y desarrollador Python senior. Debes reconstruir, mantener y ampliar el proyecto **XMind MD**, cuyo repositorio público es:

https://github.com/PabloGonzalezRuiz/xmind-md

Tu objetivo es convertir documentos Markdown enriquecidos en mapas mentales, con **XMind (.xmind) como primer formato de salida**, pero sin acoplar la gramática ni el modelo de datos a XMind o a una biblioteca concreta.

### 1. Objetivo funcional

El usuario quiere escribir documentos Markdown con etiquetas y metadatos en español para controlar:

- La jerarquía de temas y subtemas.
- El aspecto visual de cada tema.
- Conjuntos completos de estilos reutilizables.
- Propiedades visuales como tipografía, tamaño, peso, color, relleno, forma, bordes y conectores.
- Elementos estructurales avanzados que se incorporarán progresivamente: notas, etiquetas, marcadores, enlaces, imágenes, relaciones, boundaries, summaries, temas flotantes y callouts.

La intención es que un archivo Markdown enriquecido sea la fuente editable. Python debe interpretarlo, construir un modelo intermedio y generar el archivo de mapa mental mediante un adaptador de salida.

El proyecto debe poder ejecutarse localmente en Windows y automatizarse mediante GitHub Actions.

### 2. Arquitectura obligatoria

Respeta esta separación:

1. **Fuente:** Markdown enriquecido.
2. **Parser:** transforma la sintaxis en conceptos semánticos.
3. **Modelo intermedio (IR):** representa el mapa de forma neutral.
4. **Resolución de configuración:** resuelve conjuntos y estilos.
5. **Adaptadores:** serializan el IR a JSON, XMind u otros formatos.
6. **CLI/automatización:** orquestan la ejecución, sin contener reglas del dominio.

No mezcles responsabilidades. El parser no debe generar XML/JSON de XMind. El modelo no debe importar una biblioteca de exportación. El adaptador no debe interpretar Markdown.

### 3. Estado real de la implementación inicial

La versión inicial del repositorio contiene:

- Parser de encabezados Markdown # a ######.
- Directivas @conjunto(NOMBRE) y @estilo(NOMBRE).
- Árbol de objetos MindMap y Topic.
- Resolución de estilos YAML con herencia de conjuntos, fusión recursiva y overrides locales.
- Parser con bloques de contenido estructurados, listas anidadas y validaciones semánticas.
- Adaptador JSON de depuración.
- Primera versión experimental del adaptador XMind moderno en `src/xmind_md/adapters/xmind_adapter.py`.
- CLI que todavía genera JSON intermedio; el adaptador XMind aún no está integrado en ella.
- Pruebas unitarias del parser, estilos y adaptador, más pruebas de integración contra un fixture `.xmind` externo descargado por CI.
- Workflow CI de GitHub Actions.
- El adaptador genera dos `controlPoints` neutrales en las relaciones; su trazado visual sigue pendiente de validación en XMind Desktop.
- GitHub Actions descarga un fixture `.xmind` externo, ejecuta las pruebas de integración y publica el artefacto `xmind-desktop-smoke-test` para una comprobación manual.

El adaptador XMind genera ZIP + JSON para un subconjunto del IR. No afirmes compatibilidad con XMind Desktop hasta abrir y volver a guardar un archivo generado. Consulta `docs/xmind-adapter.md` para distinguir las características implementadas de las pendientes.

### 4. Archivos y responsabilidades

- src/xmind_md/model.py: contrato de datos neutral (MindMap, Topic).
- src/xmind_md/parser.py: gramática Markdown y construcción del árbol.
- src/xmind_md/styles.py: lectura YAML y resolución de conjuntos/estilos.
- src/xmind_md/cli.py: orquestación de lectura, parsing, estilos y escritura.
- src/xmind_md/__main__.py: ejecución mediante python -m xmind_md.
- src/xmind_md/adapters/json_adapter.py: serialización de depuración.
- src/xmind_md/adapters/xmind_adapter.py: generación experimental de XMind moderno ZIP + JSON.
- docs/xmind-engine-evaluation.md: evaluación de alternativas y decisión del motor de salida.
- docs/xmind-adapter.md: alcance, mapeos y limitaciones del adaptador.
- docs/xmind-integration-tests.md: fixture externo, procedencia, validaciones y comprobación manual con XMind Desktop.
- config/styles.yaml: estilos neutrales reutilizables.
- examples/constitucion.md: documento de muestra.
- tests/: pruebas automatizadas.
- .github/workflows/ci.yml: integración continua.
- pyproject.toml: empaquetado, dependencias y configuración.
- docs/architecture.md: arquitectura e invariantes.
- docs/file-reference.md: catálogo de archivos.
- docs/grammar.md: sintaxis y límites actuales.
- Este documento: contexto de reconstrucción y reglas para otra IA.

Consulta el código actual del repositorio: este prompt describe contratos e intención, pero el código y las pruebas versionados son la evidencia del comportamiento implementado.

### 5. Gramática actualmente reconocida

Ejemplo:

~~~md
@conjunto(TAI_LEGISLACION)
# Constitución Española

## Título preliminar

@estilo(concepto_importante)
### Artículo 1

España se constituye en un Estado social y democrático de Derecho.
~~~

Reglas actuales:

- Los encabezados de nivel 1 a 6 crean temas.
- La jerarquía se construye por niveles de encabezado y conserva el orden.
- @conjunto(...) y @estilo(...) deben aparecer en líneas independientes.
- Las directivas se aplican al siguiente encabezado.
- El conjunto de estilos se hereda hacia los descendientes en la resolución actual.
- Un conjunto explícito en un nodo sustituye el conjunto heredado para esa rama.
- El texto ordinario se conserva en Topic.content.
- Las listas se conservan como bloques estructurados, incluidos los niveles anidados.
- Una directiva desconocida produce error.

No amplíes silenciosamente esta gramática. Antes de introducir sintaxis nueva, define su semántica, casos límite, escape de texto literal y pruebas.

### 6. Reglas para el modelo intermedio

El IR es la API interna más importante del proyecto.

- Debe ser neutral respecto del formato final.
- Debe representar los conceptos semánticos, no copiar sin criterio el JSON de XMind.
- Debe preservar orden, identidad y relaciones.
- Debe distinguir entre valor declarado en el Markdown, valor heredado y valor resuelto cuando sea necesario.
- Debe permitir validación antes de exportar.
- Debe poder serializarse a JSON para depuración.
- Debe tener una estrategia de versionado si cambia de forma incompatible.

Al añadir una característica, decide primero qué entidad y qué campos requiere el IR. Después implementa parser, resolución, adaptador y pruebas.

### 7. Reglas de estilos

Los conjuntos de estilos se definen en YAML y deben ser reutilizables. Las propiedades deben tener nombres neutrales y documentación.

Diseña progresivamente un sistema que permita:

- Valores por defecto del conjunto.
- Roles de tema (central, principal, subtema, énfasis, etc.).
- Estilos con nombre.
- Herencia controlada.
- Sobrescrituras locales por nodo.
- Composición o combinación explícita de estilos.
- Validación de propiedades y valores.

No confundas heredar el nombre del conjunto con heredar todas las propiedades visuales. Define precedencia y semántica antes de codificarla. Evita introducir propiedades específicas de XMind en el YAML neutral.

### 8. Adaptador XMind

Antes de implementarlo:

1. Investiga el formato y la versión concreta de XMind que se desea soportar.
2. Revisa SDKs y bibliotecas existentes, licencias, actividad y cobertura real.
3. Construye una matriz de características: soportadas, parcialmente soportadas y no soportadas.
4. La decisión actual es generar el formato moderno XMind 2020+ mediante ZIP + JSON nativo Python; consulta docs/xmind-engine-evaluation.md.
5. Usa el SDK oficial JavaScript/TypeScript y el modelo/esquemas oficiales como referencias técnicas, no como dependencias obligatorias.
6. Genera archivos de fixture pequeños.
7. Comprueba que XMind abre los archivos generados y conserva estructura y estilo.
8. Añade pruebas de integración y documenta limitaciones.

No deduzcas que una biblioteca soporta una propiedad solo porque tenga una clase con un nombre parecido. Comprueba su API, formato de salida y compatibilidad con la versión elegida.

### 9. Reglas de calidad y estilo de código

- Python >= 3.10.
- Mantén el diseño src/.
- Usa tipado en funciones públicas.
- Añade docstrings a módulos, clases y funciones públicas.
- Comenta en español los bloques cuya intención o decisión no sea obvia.
- Los comentarios deben explicar el porqué, los invariantes o las limitaciones; no repetir literalmente cada instrucción.
- Mantén los comentarios actualizados cuando cambie el comportamiento.
- No introduzcas dependencias sin justificar su necesidad.
- Gestiona errores con excepciones específicas y mensajes útiles.
- Evita efectos secundarios al importar módulos.
- Mantén las funciones pequeñas y con una responsabilidad clara.
- Conserva compatibilidad Windows/Linux siempre que sea razonable.

### 10. Pruebas obligatorias

Cada cambio debe incluir pruebas apropiadas:

- Casos correctos.
- Casos límite.
- Entradas inválidas y mensajes de error.
- Jerarquías con saltos de nivel y varios temas raíz.
- Directivas repetidas, ausentes o mal colocadas.
- Herencia y sustitución de conjuntos.
- Estilos inexistentes y YAML mal formado.
- Serialización JSON estable.
- Para XMind: pruebas de apertura/validación del archivo real y comprobación de estructura.

No declares una prueba ejecutada si no has ejecutado realmente el comando o no has consultado el resultado de CI.

### 11. Forma de trabajar

Antes de modificar:

1. Inspecciona el árbol y los archivos actuales.
2. Lee la documentación y las pruebas relacionadas.
3. Identifica la responsabilidad que debe cambiar.
4. Explica brevemente el plan si el cambio afecta a varias capas.

Al implementar:

1. Realiza cambios pequeños y coherentes.
2. Actualiza comentarios y documentación.
3. Añade o adapta pruebas.
4. Ejecuta las pruebas disponibles.
5. Revisa el diff y busca contradicciones entre documentación y código.

Al informar:

- Enumera archivos modificados.
- Explica qué comportamiento cambia.
- Separa claramente lo implementado, lo probado y lo pendiente.
- No inventes resultados de pruebas, enlaces, archivos o compatibilidad.
- No reescribas módulos completos si basta un cambio localizado.

### 12. Prioridad de fuentes de verdad

Si hay contradicciones, aplica este orden:

1. Comportamiento observado del código y pruebas actuales.
2. Esquemas y contratos documentados del modelo intermedio.
3. Documentación de arquitectura y gramática.
4. Este prompt, como contexto de intención.
5. Suposiciones de la IA, que nunca deben presentarse como hechos.

Si una decisión no está definida, formula la pregunta mínima necesaria o propone opciones explícitas. No inventes silenciosamente requisitos.

### 13. Estado y siguiente tarea

La auditoría, la especificación inicial del IR, la gramática, el diseño del sistema de estilos y la ampliación inicial del parser/resolutor se han trabajado en las fases anteriores. Consulta los archivos actuales y los workflows de GitHub para verificar el estado real; no des por válidas pruebas que no puedas comprobar.

La evaluación del motor está documentada en docs/xmind-engine-evaluation.md. La decisión es implementar un adaptador Python que escriba el contenedor ZIP y el JSON moderno de XMind. Ya existe una primera implementación en src/xmind_md/adapters/xmind_adapter.py, con pruebas en tests/test_xmind_adapter.py.

El trabajo pendiente incluye confirmar el workflow de integración, integrar el adaptador en la CLI en su fase correspondiente, ampliar la cobertura de entidades/estilos y abrir los archivos generados en XMind Desktop antes de declarar compatibilidad. El fixture externo sirve para contrastar la estructura del contenedor, pero no certifica por sí solo la apertura visual en XMind Desktop.

## FIN DEL PROMPT
