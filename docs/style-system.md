# Sistema de estilos de XMind MD

**Versión de diseño:** 1.0-draft  
**Contrato IR objetivo:** 1.1.0  
**Estado:** resolución implementada y compatible con IR 1.0.0/1.1.0 y ruta legacy. Los roles semánticos existen en el modelo, pero su catálogo y reglas de aplicación pertenecen a la Fase 3. Las secciones de diseño general describen vocabulario neutral objetivo; el esquema YAML ejecutable y la cascada efectiva se especifican en las secciones 3.1 y 15.

## 1. Objetivo

El sistema de estilos debe permitir describir la apariencia del mapa mediante propiedades neutrales, reutilizar configuraciones completas y sobrescribir solo las propiedades necesarias.

Debe cubrir los elementos visuales que XMind permite estilizar y mantener el núcleo independiente de su formato interno:

- Mapa y hoja.
- Temas.
- Texto enriquecido dentro de los temas.
- Ramas y conectores jerárquicos.
- Relaciones.
- Límites (boundaries).
- Resúmenes (summaries).
- Callouts.
- Texto y anotaciones cuando el adaptador de destino permita darles estilo.

El diseño distingue tres conceptos:

1. **Catálogo:** propiedades normalizadas, tipos, unidades y valores permitidos.
2. **Definiciones:** estilos y conjuntos reutilizables declarados en YAML.
3. **Resolución:** cálculo de propiedades efectivas por elemento antes de exportar.

El sistema no debe confundir estilos con estructura. Por ejemplo, el plegado de una rama, el orden de los temas y la estructura del mapa son datos de disposición o comportamiento, no colores ni tipografía.

## 2. Principios

1. Las claves del catálogo son neutrales y estables.
2. Ninguna clave del núcleo debe ser un nombre XML, JSON o atributo privado de XMind.
3. Las propiedades se agrupan por elemento y categoría.
4. Se combinan propiedades individualmente mediante fusión recursiva.
5. La ausencia de una propiedad significa heredar.
6. Un valor explícito sustituye el anterior.
7. `null` solicita restablecer la propiedad a su valor predeterminado.
8. Las listas y valores escalares se sustituyen completos; no se concatenan implícitamente.
9. La selección de un conjunto se hereda por la rama de temas, pero los valores visuales de un tema no se copian automáticamente a sus hijos.
10. Cada adaptador declara qué propiedades representa, aproxima o no admite.
11. Las propiedades desconocidas producen un diagnóstico; no se descartan silenciosamente.
12. La resolución debe ser determinista.

## 3. Modelo de datos del sistema de estilos

### 3.1 Estructura de configuración

**Esquema ejecutable actual (IR 1.x):** el resolutor consume dos catálogos superiores, `style_sets` y `styles`. No consume las secciones superiores `version`, `defaults`, `elements` ni `extensions` descritas en diseños históricos.

- `style_sets`: cada nombre de conjunto contiene propiedades agrupadas directamente por tipo de elemento (`topic`, `relationship`, `boundary`, `summary`, `notes`) y, opcionalmente, un mapping `styles` con estilos nombrados del conjunto.
- `styles`: catálogo global; cada estilo agrupa sus propiedades por tipo de elemento.
- Las propiedades se expresan directamente bajo el tipo, por ejemplo `topic.text.color`.

Ejemplo tomado de la configuración vigente del repositorio:

~~~yaml
style_sets:
  BASE_ACADEMICO:
    topic:
      text:
        font_family: Arial
        font_size: 14
        color: "#263B5A"
  TAI_LEGISLACION:
    topic:
      text:
        font_family: Arial
        font_size: 14
      background:
        color: "#FFFFFF"
    styles:
      concepto_importante:
        topic:
          text:
            color: "#9C0006"
            bold: true
          border:
            color: "#C00000"
            width: 1.5

styles:
  relacion_default:
    relationship:
      line:
        color: "#607D8B"
        width: 1.5
        pattern: solid
~~~

No añadas `extends`, `elements`, `applies_to` ni `properties` al archivo ejecutable: pertenecen a un esquema de diseño anterior y no son interpretados por el resolutor.

### 3.2 Elementos estilizados

| Tipo | Qué representa |
|---|---|
| `map` | Fondo y presentación global de la hoja |
| `topic` | Forma, relleno, borde y texto del tema |
| `branch` | Línea de conexión jerárquica entre padre e hijo |
| `relationship` | Línea independiente entre dos temas y su etiqueta |
| `boundary` | Marco que agrupa visualmente temas |
| `summary` | Trazo o llave que resume uno o varios temas |
| `summary_topic` | Apariencia del tema que contiene el texto del resumen |
| `callout` | Elemento de llamada asociado a un tema |

Un tema puede tener un perfil de rol: `root`, `main` o `subtopic`. El rol es una clasificación semántica neutral; no debe confundirse con el nivel de encabezado Markdown. El usuario podrá sobrescribirlo explícitamente cuando la inferencia no sea adecuada.

Los estilos de `notes` y de bloques de contenido se consideran una extensión del catálogo. No se asumirá que XMind los representa visualmente de la misma manera que los temas.

## 4. Catálogo de propiedades neutrales

Las siguientes propiedades constituyen el catálogo inicial recomendado. No todas tienen garantía de representación idéntica en todos los formatos de salida.

### 4.1 Tipografía y texto

| Propiedad | Tipo | Significado |
|---|---|---|
| `typography.font_family` | string | Familia tipográfica |
| `typography.font_size` | number | Tamaño en puntos |
| `typography.font_weight` | enum/number | `normal`, `bold` o peso numérico |
| `typography.font_style` | enum | `normal` o `italic` |
| `typography.text_align` | enum | `left`, `center`, `right`, `justify` |
| `typography.vertical_align` | enum | `top`, `middle`, `bottom` |
| `text.color` | color | Color del texto |
| `text.decoration` | enum/list | `none`, `underline`, `line_through`, combinaciones admitidas |
| `text.wrap` | boolean | Permitir ajuste de línea |
| `text.line_height` | number | Factor de interlineado |

Los fragmentos enriquecidos (`runs`) pueden sobrescribir tipografía, color, decoración y enlace en un tramo concreto. Una propiedad de un fragmento afecta solo a ese tramo.

### 4.2 Forma y relleno

| Propiedad | Tipo | Significado |
|---|---|---|
| `shape.type` | string/enum | Forma del elemento |
| `shape.fill.color` | color | Color de relleno |
| `shape.fill.opacity` | number | Opacidad entre 0 y 1 |
| `shape.fill.image` | asset reference | Imagen de fondo, si el destino la admite |
| `shape.corner_radius` | number | Radio de esquina, cuando proceda |

El catálogo neutral no debe enumerar como universales las 31 formas de una versión concreta de XMind. Utiliza nombres semánticos estables y permite extensiones para formas propietarias.

### 4.3 Borde

| Propiedad | Tipo | Significado |
|---|---|---|
| `border.color` | color | Color del borde |
| `border.width` | number | Grosor en puntos |
| `border.pattern` | enum | `solid`, `dash`, `dot`, `dash_dot` |
| `border.opacity` | number | Opacidad entre 0 y 1 |

### 4.4 Ramas y líneas

| Propiedad | Tipo | Significado |
|---|---|---|
| `line.shape` | enum/string | Geometría de línea o conexión |
| `line.color` | color | Color |
| `line.width` | number | Grosor en puntos |
| `line.pattern` | enum | Patrón continuo o discontinuo |
| `line.start_arrow` | string/enum | Terminación inicial |
| `line.end_arrow` | string/enum | Terminación final |
| `line.taper` | enum/boolean | Variación de grosor, si se admite |
| `line.color_source` | enum | `explicit`, `source_topic`, `target_topic`, `theme` |

Las propiedades de flechas se aplican a relaciones; no se supondrá que las ramas jerárquicas admiten las mismas terminaciones.

### 4.5 Espaciado y dimensiones

| Propiedad | Tipo | Significado |
|---|---|---|
| `spacing.padding` | number/object | Relleno interior en puntos |
| `spacing.margin` | number/object | Separación exterior en puntos |
| `spacing.gap` | number | Separación entre elementos |
| `dimensions.width` | number | Anchura explícita |
| `dimensions.min_width` | number | Anchura mínima |
| `dimensions.max_width` | number | Anchura máxima |
| `dimensions.height` | number | Altura explícita |

Estas propiedades pueden depender de la estructura de mapa y de las capacidades del adaptador. No se debe prometer posicionamiento absoluto cuando el formato de salida lo calcule automáticamente.

### 4.6 Fondo y efectos

| Propiedad | Tipo | Significado |
|---|---|---|
| `background.color` | color | Fondo del mapa o superficie |
| `background.image` | asset reference | Imagen de fondo |
| `background.opacity` | number | Opacidad |
| `effects.shadow` | object/boolean | Sombra, si está soportada |

Los efectos se consideran capacidades opcionales. Si un adaptador no los admite, debe emitir una advertencia de pérdida.

### 4.7 Propiedades de presentación no estilísticas

Se mantienen fuera del catálogo visual:

- Plegado de ramas.
- Orden de temas.
- Orientación y estructura de la hoja.
- Anchura personalizada cuando sea un atributo estructural del tema.
- Numeración automática y su alcance.
- Posición manual.
- Visibilidad funcional.

Pueden pertenecer a `layout`, `numbering` o a otras entidades del IR. El sistema de estilos no debe apropiarse de ellas por comodidad.

## 5. Unidades y formatos

Para evitar ambigüedades:

- Colores: hexadecimal `#RRGGBB` o `#RRGGBBAA`; el formato canónico de serialización será hexadecimal.
- Opacidad: número entre 0 y 1.
- Tamaños de fuente y grosores de línea: puntos (pt), expresados como número sin sufijo.
- Márgenes y rellenos: puntos.
- Anchuras y alturas: puntos cuando sean dimensiones físicas; la semántica concreta se documenta en la propiedad.
- Porcentajes: números entre 0 y 100 solo en propiedades declaradas como porcentaje.
- Fechas y referencias a assets no forman parte del catálogo visual.

No se aceptarán cadenas como `"14px"` para una propiedad que ya tiene unidad definida. La validación debe detectar tipos y rangos incorrectos.

## 6. Conjuntos de estilos y perfiles

Un conjunto agrupa propiedades neutrales por tipo de elemento. El conjunto efectivo se hereda por la jerarquía de temas; un tema descendiente puede seleccionar otro conjunto para su rama.

La estructura real no utiliza `elements`, perfiles `roles` ni `extends`. Los estilos nombrados de un conjunto se declaran bajo su clave `styles`:

~~~yaml
style_sets:
  BASE_ACADEMICO:
    topic:
      text:
        font_size: 14
        color: "#263B5A"
  TAI_LEGISLACION:
    topic:
      text:
        font_size: 14
    styles:
      concepto_importante:
        topic:
          text:
            color: "#9C0006"
            bold: true
~~~

El conjunto seleccionado en el tema se guarda como estado de estilo y se transmite a los descendientes, salvo que uno seleccione otro. Las propiedades de estilo no se copian automáticamente desde el padre al hijo; se hereda el contexto del conjunto.

## 7. Estilos con nombre

Un estilo con nombre agrupa propiedades por tipo de elemento. Puede declararse en el catálogo global `styles` o dentro de `style_sets.NOMBRE.styles`.

~~~yaml
styles:
  relacion_default:
    relationship:
      line:
        color: "#607D8B"
        width: 1.5
        pattern: solid
~~~

El resolutor actual no utiliza `applies_to` ni `properties`. El tipo destinatario se expresa como clave del mapping (`topic`, `relationship`, `boundary`, `summary` o `notes`). Las propiedades admitidas se validan después según el elemento y el adaptador de salida.

## 8. Cascada y precedencia

Para IR 1.x, `resolve_ir_styles()` aplica por propiedad esta precedencia, de menor a mayor:

1. Defaults del sistema suministrados al resolutor.
2. `MindMap.metadata.style_defaults`.
3. Propiedades del conjunto efectivo.
4. Estilo nombrado.
5. Overrides locales del elemento.

Las definiciones de estilos/conjuntos embebidas en el documento prevalecen sobre las externas cuando comparten nombre. El conjunto se hereda por la jerarquía de temas; un descendiente puede seleccionar otro. Los valores visuales del tema padre no se copian automáticamente a sus hijos.

El resolutor fusiona mappings recursivamente y no modifica los catálogos originales. El resultado queda en `StyleState.resolved`.

### 8.1 Reglas de fusión

- Mapping + mapping: fusión recursiva por clave.
- Escalar + escalar: el valor más específico reemplaza al anterior.
- Lista + lista: la lista más específica reemplaza a la anterior.
- Propiedad ausente: conserva el valor anterior.
- `null`: restablece al valor predeterminado del sistema para esa propiedad.
- Tipo incompatible: error de validación.

La resolución debe conservar, para diagnóstico, la procedencia de cada valor: predeterminado, mapa, conjunto, perfil, estilo o modificación local.

## 9. Sintaxis en Markdown e IR

La gramática definida en `docs/grammar.md` utiliza:

~~~md
:::xmind
style_set: TAI_LEGISLACION
style: concepto_importante
style_overrides:
  text:
    color: "#9C0006"
  typography:
    font_weight: bold
:::
### Concepto clave
~~~

Correspondencia con el IR:

| Fuente | IR |
|---|---|
| `style_set` | Contexto de conjunto seleccionado |
| `style` | `style.ref` |
| `style_overrides` | `style.overrides` |
| Resultado de la cascada | `style.resolved` |

El parser conserva referencias y modificaciones locales. El módulo de estilos realiza la resolución. El adaptador recibe las propiedades efectivas y los datos de procedencia necesarios para advertir de pérdidas.

## 10. Nombres técnicos y etiquetas en español

Las claves canónicas del catálogo se mantienen en inglés técnico y en `snake_case` para ofrecer estabilidad a Python, JSON y futuros adaptadores.

La interfaz de autoría y la documentación pueden mostrar etiquetas en español. Se recomienda mantener un diccionario independiente de alias y etiquetas:

| Etiqueta española | Clave canónica |
|---|---|
| Color del texto | `text.color` |
| Familia tipográfica | `typography.font_family` |
| Tamaño de fuente | `typography.font_size` |
| Grosor de fuente | `typography.font_weight` |
| Color de relleno | `shape.fill.color` |
| Tipo de forma | `shape.type` |
| Color del borde | `border.color` |
| Grosor del borde | `border.width` |
| Color de línea | `line.color` |
| Grosor de línea | `line.width` |
| Relleno interior | `spacing.padding` |
| Sombra | `effects.shadow` |

Los alias españoles no deben crear propiedades duplicadas en el IR. Se traducen a la clave canónica antes de la validación y resolución. Las colisiones entre alias deben ser errores.

## 11. Capacidades y adaptadores

Cada adaptador debe publicar un catálogo de capacidades por elemento y propiedad, con uno de estos estados:

| Estado | Significado |
|---|---|
| `native` | Representación directa |
| `mapped` | Conversión documentada a una propiedad equivalente |
| `approximate` | Representación aproximada |
| `unsupported` | No se puede representar |

El adaptador XMind debe validar estas capacidades contra la versión de XMind y el formato de archivo elegidos. No se debe deducir compatibilidad únicamente porque una propiedad exista en el IR o en un ejemplo de tema del SDK.

La documentación oficial de XMind describe controles visuales para Topic, Relationship, Boundary, Summary y Callout. También documenta opciones específicas de líneas, extremos de flecha, formas, texto y numeración. Véanse las fuentes al final.

## 12. Validación

La implementación valida que las fuentes YAML sean mappings, que las definiciones tengan estructura reconocible, que las referencias a estilos puedan resolverse tras combinar los catálogos embebidos y externos, y que los tipos de valores sean válidos para las propiedades implementadas.

No debe darse por implementada la validación genérica de todas las propiedades conceptuales descritas en este documento. El adaptador XMind aplica una lista blanca adicional: rechaza propiedades desconocidas, valores `null` no materializables y estados de estilo no resueltos. Consulta la matriz vigente en [xmind-adapter.md](xmind-adapter.md).

## 13. Pruebas de aceptación

La lista siguiente es una hoja de criterios de diseño para la evolución del sistema; no implica que todas estas capacidades formen parte del resolutor actual. En particular, herencia `extends`, perfiles de rol, alias localizados y modos strict/compatible no deben anunciarse como funciones implementadas salvo que se incorporen y prueben expresamente.

El sistema de estilos estará listo cuando disponga de pruebas que demuestren:

1. Fusión recursiva de mappings.
2. Sustitución completa de listas.
3. Restablecimiento mediante `null`.
4. Herencia de un conjunto por descendientes.
5. Sustitución de conjunto en una rama sin afectar a hermanos.
6. Herencia de conjuntos mediante `extends`.
7. Detección de ciclos.
8. Aplicación de perfiles `root`, `main` y `subtopic`.
9. Resolución de estilos globales y locales con el mismo nombre.
10. Precedencia de modificaciones locales.
11. Aislamiento de estilos de fragmentos enriquecidos.
12. Validación de tipo de elemento (`applies_to`).
13. Validación de unidades, colores y rangos.
14. Diagnóstico de propiedades no soportadas por el adaptador.
15. Resultado determinista para la misma entrada.

## 14. Fuentes técnicas

- Guía oficial de estilos de XMind: https://xmind.com/user-guide/style-new
- Guía oficial de relaciones: https://xmind.com/user-guide/relationship-new
- Guía oficial de límites: https://xmind.com/user-guide/boundary-new
- Modelo público de XMind: https://github.com/xmindltd/xmind-model
- SDK JavaScript y temas de ejemplo: https://github.com/xmindltd/xmind-sdk-js

Estas fuentes permiten inventariar capacidades y vocabulario, pero no sustituyen las pruebas de exportación y apertura en la versión de XMind que se elija como objetivo.


## 15. Estado real de implementación

La resolución de estilos ya está implementada en `src/xmind_md/styles.py`. Para IR 1.x, `resolve_ir_styles()` aplica por propiedad esta precedencia:

1. Defaults del sistema proporcionados a la función.
2. `MindMap.metadata.style_defaults`.
3. Conjunto efectivo de estilos.
4. Estilo nombrado.
5. Overrides locales del elemento.

El conjunto se hereda por la jerarquía de temas; un descendiente puede seleccionar otro conjunto. Las definiciones declaradas en el documento prevalecen sobre las definiciones externas con el mismo nombre. La fusión de mappings es recursiva, no muta los catálogos originales y almacena el resultado en `StyleState.resolved`.

Se resuelven estilos de temas, notas, relaciones, boundaries y summaries. La ruta legacy se mantiene por compatibilidad.

**Alcance y límites:**

- La resolución neutral no valida que cada propiedad pueda representarse en todos los adaptadores.
- El adaptador XMind aplica una lista blanca propia de propiedades y rechaza propiedades desconocidas, valores `null` no materializables y estilos no resueltos.
- La cobertura de exportación XMind es deliberadamente menor que la capacidad de representación del IR.
- No debe interpretarse la lista de capacidades de XMind como un catálogo universal de estilos disponible para cualquier destino.

La matriz de traducción vigente se mantiene en [xmind-adapter.md](xmind-adapter.md). Las pruebas de precedencia, herencia, fusión y errores están en `tests/test_styles.py` y en las pruebas IR correspondientes.


## 16. Evolución prevista: catálogo semántico y reglas para PMD

Esta sección describe el diseño objetivo, **no funciones implementadas en el resolutor IR 1.x**. La ejecución actual sigue siendo la descrita en las secciones 3.1, 8 y 15.

Los estilos deberán residir en una biblioteca reutilizable separada del contenido. Cada entrada tendrá identificador estable, descripción semántica, destinatarios, propiedades visuales, restricciones y ejemplos. El catálogo estructurado debe poder ser leído por el motor y suministrado a la IA; la documentación descriptiva debe ser coherente con él. YAML/JSON y Markdown son candidatos, pero el esquema final está pendiente.

Las reglas de aplicación combinarán:
- **Semánticas:** significado/rol (artículo, apartado, excepción, definición, cabecera, celda).
- **Estructurales:** tipo de estructura, padre, posición entre hermanos, nivel o tipo de celda.

La semántica será el criterio principal y la estructura será complementaria. Los conflictos deberán resolverse explícitamente y de forma determinista.

Se conserva el principio de herencia por referencia al primer hijo: puede establecer el formato predeterminado para sus hermanos; los hijos pueden declarar excepciones; la regla se aplica recursivamente. Queda pendiente precisar fallback si el primer hijo carece de estilo, fusión por propiedad y precedencia frente a reglas semánticas y overrides.

La IA debe seleccionar roles y referencias existentes; el motor valida y resuelve. No confundir este diseño con la cascada actual de conjuntos por rama. Ver [pmd-design.md](pmd-design.md) y [roadmap.md](roadmap.md).


## 17. Distinciones derivadas de la referencia Tema1

El análisis de [Tema1](reference-analysis-tema1.md) confirma que el diseño PMD debe distinguir al menos estas fuentes de presentación:

1. **Perfil general del tema XMind:** valores de `theme` para mapa, tema central, temas principales/secundarios y otros elementos.
2. **Estilo explícito del elemento:** objeto `style` asociado al tema concreto.
3. **Propiedad ausente:** no se ha declarado un valor en ese objeto.
4. **Valor explícito especial `inherited`:** la propiedad está presente y solicita herencia según la semántica del formato de origen.
5. **Regla de autoría PMD:** estilo semántico, regla contextual o herencia por referencia al primer hijo.

Estas fuentes no son intercambiables. En particular, la regla PMD de tomar el formato del primer hijo como referencia de sus hermanos no describe el comportamiento nativo demostrado por Tema1: las celdas `Cabecera` y `cuerpo` contienen estilos propios y distintos. La regla PMD es una comodidad declarativa futura para reducir anotaciones, no una afirmación sobre cómo XMind creó esa referencia.

El catálogo PMD deberá almacenar propiedades neutrales y metadatos de uso para IA. Los valores técnicos como `fo:font-size`, `svg:fill`, `shape-class` o `org.xmind.internal.topicShape.treeTableCell` pertenecen a la traducción del formato XMind, no al vocabulario semántico que la IA debe escribir.

La procedencia de cada propiedad efectiva debe poder explicarse: perfil/base, regla semántica, regla estructural, herencia, estilo explícito o excepción local. La cascada de estilos IR 1.x descrita en la sección 8 ya está implementada. Lo pendiente para la Fase 3 es definir cómo se integra esa cascada con las reglas semánticas y estructurales de PMD, la herencia por referencia al primer hijo, los valores por defecto y las excepciones, así como la procedencia por propiedad.
