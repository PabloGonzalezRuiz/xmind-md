# Guía de estilos y temas personalizados

**Versión de referencia:** XMind MD 0.1.0 Alpha  
**Contrato:** IR 1.0.0

Esta guía enseña a utilizar los estilos que ya implementa XMind MD y a crear catálogos YAML propios. Separa deliberadamente las capacidades del motor de resolución de las propiedades que el adaptador XMind puede exportar.

> **Importante:** que una propiedad pueda almacenarse y resolverse en el IR no garantiza que pueda representarse en un archivo `.xmind`. Antes de utilizar una propiedad, consulta la [matriz de capacidades del adaptador XMind](../xmind-adapter.md).

## 1. Conceptos básicos

XMind MD utiliza cuatro mecanismos:

| Concepto | Función |
|---|---|
| Conjunto (`style_set`) | Agrupa propiedades base y estilos con nombre. Puede heredarse a lo largo de una rama de temas. |
| Estilo con nombre (`style` / `ref`) | Aplica una definición reutilizable a un elemento concreto. |
| Modificaciones locales (`style_overrides`) | Sobrescriben propiedades para un elemento concreto. |
| Estilo resuelto (`resolved`) | Resultado calculado por el motor antes de exportar. No se escribe manualmente en Markdown. |

El catálogo de estilos puede estar integrado en el documento Markdown o cargarse desde un archivo YAML externo.

## 2. Crear el primer catálogo YAML

Crea un archivo, por ejemplo `mis-estilos.yaml`:

```yaml
style_sets:
  MI_TEMA:
    topic:
      text:
        font_family: Arial
        font_size: 14
        color: "#263B5A"
      background:
        color: "#FFFFFF"
    styles:
      importante:
        topic:
          text:
            color: "#9C0006"
            bold: true
          border:
            color: "#C00000"
            width: 1.5

styles:
  relacion:
    relationship:
      line:
        color: "#607D8B"
        width: 1.5
        pattern: solid
```

La estructura ejecutable tiene dos claves superiores:

- `style_sets`: conjuntos. Cada conjunto puede definir propiedades para `topic`, `relationship`, `boundary`, `summary` y `notes`, y puede incluir un subcatálogo `styles`.
- `styles`: estilos globales con nombre, agrupados por tipo de elemento.

Las propiedades se escriben directamente bajo el tipo de elemento. Por ejemplo, `topic.text.color`.

No utilices `extends`, `elements`, `applies_to` ni `properties` como estructura del catálogo: pertenecen a propuestas de diseño anteriores y el resolutor actual no las interpreta.

## 3. Aplicar un conjunto y un estilo en Markdown

El conjunto predeterminado del documento se selecciona en el front matter:

```markdown
---
title: Mi mapa
style_set: MI_TEMA
---

# Mi mapa

:::xmind
style: importante
:::
## Concepto importante
```

El conjunto se aplica al tema raíz y se hereda por sus descendientes. El estilo `importante` se aplica al tema inmediatamente posterior a la directiva.

También se puede seleccionar un conjunto para una rama concreta:

```markdown
# Mi mapa

:::xmind
style_set: MI_TEMA
:::
## Rama con MI_TEMA
### Este tema hereda el conjunto
```

Un descendiente puede seleccionar otro conjunto. Ese cambio se propaga a sus propios descendientes, pero no afecta a ramas hermanas.

## 4. Sobrescribir propiedades localmente

Utiliza `style_overrides` para cambiar solo lo necesario:

```markdown
:::xmind
style_overrides:
  text:
    color: "#0000FF"
    italic: true
:::
### Tema con texto azul y cursiva
```

Los overrides se fusionan recursivamente con el resto de las definiciones. No eliminan las propiedades que no mencionan.

## 5. Dónde se pueden definir los estilos

### 5.1. Dentro del propio Markdown

El front matter puede contener `styles` y `style_sets`. Es útil para documentos autocontenidos y ejemplos pequeños.

```yaml
---
title: Mapa de ejemplo
style_sets:
  BASE:
    topic:
      text:
        color: "#263B5A"
styles:
  alerta:
    topic:
      text:
        color: "#C00000"
---
```

### 5.2. En un archivo YAML externo

Los catálogos externos facilitan reutilizar la misma identidad visual en varios documentos. Se pasan a la CLI con `--styles`:

```bash
xmind-md mapa.md --styles mis-estilos.yaml --output mapa.xmind
```

Si un estilo o conjunto aparece tanto en el documento como en el catálogo externo, **la definición del documento prevalece** para ese mismo nombre.

## 6. Precedencia: cómo se calcula el resultado

Para IR 1.0.0, la resolución combina las fuentes en este orden, de menor a mayor prioridad:

1. Defaults del sistema suministrados al resolutor.
2. `metadata.style_defaults` del documento.
3. Propiedades del conjunto efectivo.
4. Estilo con nombre.
5. `style_overrides` locales.

La fusión de mappings es recursiva. Por ejemplo, si el conjunto define tamaño y color de texto, y el estilo con nombre cambia solo el color, el tamaño se conserva.

El conjunto efectivo se hereda por la jerarquía. Las propiedades visuales del tema padre **no** se copian automáticamente a los hijos: lo que se hereda es la selección del conjunto.

Los valores `null` pueden conservarse en el resultado de la resolución, pero el adaptador XMind actual rechaza propiedades nulas. No los utilices como mecanismo de reinicio en documentos destinados a exportarse a XMind.

## 7. Propiedades exportables a XMind en 0.1.0

La siguiente tabla resume las propiedades que el adaptador actual puede materializar:

| Clave neutral | Uso |
|---|---|
| `shape` | Forma del tema |
| `text.font_family` | Familia tipográfica |
| `text.font_size` | Tamaño de fuente |
| `text.font_weight` | Peso tipográfico |
| `text.bold` | Negrita |
| `text.italic` | Cursiva |
| `text.color` | Color del texto |
| `text.decoration` | Decoración del texto |
| `background.color` / `background.fill` | Relleno/fondo |
| `border.color` | Color del borde |
| `border.width` | Grosor del borde |
| `border.pattern` | Patrón del borde |
| `line.color` | Color de línea |
| `line.width` | Grosor de línea |
| `line.pattern` | Patrón de línea |

En relaciones, el perfil admite las propiedades `line.color`, `line.width` y `line.pattern`. No todas las propiedades de la tabla son aplicables a todos los tipos de elemento.

Las claves desconocidas, propiedades no admitidas y estilos sin resolver provocan un error explícito en la exportación: no se descartan silenciosamente.

Consulta [Adaptador XMind: propiedades y limitaciones](../xmind-adapter.md#propiedades-de-estilo-admitidas) para el mapeo exacto y las restricciones.

## 8. Ejemplo completo mínimo

Guarda este documento como `mi-mapa.md`:

```markdown
---
title: Mi primer tema personalizado
style_set: AULA
---

# Mi primer tema

:::xmind
style: clave
:::
## Idea principal

### Explicación

:::xmind
style_overrides:
  text:
    color: "#008000"
:::
### Matiz en verde
```

Y este catálogo como `aula.yaml`:

```yaml
style_sets:
  AULA:
    topic:
      text:
        font_family: Arial
        font_size: 14
        color: "#263B5A"
    styles:
      clave:
        topic:
          text:
            color: "#C00000"
            bold: true
          border:
            color: "#C00000"
            width: 1.5
```

Genera el archivo:

```bash
xmind-md mi-mapa.md --styles aula.yaml --output mi-mapa.xmind
```

Abre `mi-mapa.xmind` en XMind para comprobar visualmente el resultado. Si una propiedad no es admitida por el perfil de exportación, la CLI informará del error.

## 9. Ejemplo real incluido en el repositorio

El repositorio contiene un catálogo reutilizable en `config/styles.yaml` y un documento de demostración en `examples/constitucion.md`.

En ellos puedes estudiar:

- El conjunto `TAI_LEGISLACION`.
- El estilo nombrado `concepto_importante`.
- El estilo de relación `relacion_default`.
- Estilos de límites y resúmenes.

**Advertencia:** `examples/constitucion.md` sirve para demostrar el parser, el IR y los catálogos. No es un ejemplo exportable íntegramente a XMind 0.1.0: incluye recursos, tareas, límites y resúmenes que el adaptador actual no exporta.

## 10. Diagnóstico de errores frecuentes

| Problema | Causa probable / solución |
|---|---|
| Conjunto inexistente | Comprueba el nombre de `style_set` y que esté declarado en el documento o catálogo externo. |
| Estilo no definido | Comprueba `style`, el catálogo global `styles` y el subcatálogo `styles` del conjunto. |
| YAML inválido | Revisa indentación, tipos y claves duplicadas. |
| Propiedad desconocida al exportar | Comprueba que la clave esté admitida por el adaptador XMind. |
| Estilo sin resolver | La exportación requiere que el motor haya resuelto previamente las referencias y overrides. |
| El mapa no refleja un cambio | Comprueba qué fuente tiene prioridad y si el nombre está duplicado en el documento y en el YAML externo. |

## 11. Límites y funcionalidades futuras

En 0.1.0 Alpha:

- No se implementan herencia de definiciones mediante `extends`, perfiles `root/main/subtopic` ni alias de propiedades en español.
- El motor resuelve estilos para temas, notas, relaciones, límites y resúmenes en el IR; esto no significa que el adaptador XMind exporte visualmente todos esos elementos.
- Los catálogos y nombres de estilos se materializan en propiedades resueltas; no se conservan como catálogos reutilizables dentro del archivo XMind.
- El adaptador rechaza propiedades no admitidas, valores nulos y estilos sin resolver.

La especificación técnica del sistema está en [Sistema de estilos](../style-system.md). Para conocer el contrato del modelo intermedio, consulta [Especificación IR 1.0.0](../ir-specification.md).

## 12. Recorrido recomendado de aprendizaje

1. Ejecuta el ejemplo de esta guía sin modificarlo.
2. Cambia un color o tamaño en `aula.yaml` y vuelve a generar el mapa.
3. Añade un estilo nombrado nuevo y asígnalo a otro tema.
4. Define un segundo conjunto y aplícalo a una rama.
5. Añade un override local y observa qué propiedades conserva.
6. Prueba una propiedad no admitida para comprobar cómo informa el adaptador.

Este recorrido permite aprender el comportamiento real del motor antes de estudiar ampliaciones del catálogo o cambios en el código.
