# Guía de estilo del reporte

Reglas de redacción para todo lo que vive en `reports/secciones/*.tex`. No
sustituye al `CLAUDE.md` de la raíz (que cubre estructura de archivos,
bibliografía y flujo de git) — esto es específicamente sobre **cómo se
escribe** el texto una vez que ya se sabe dónde va.

Se aplica al escribir contenido nuevo, no solo al revisar lo existente: el
objetivo es no tener que hacer una pasada de estilo después de cada etapa.

## Registro

- Lenguaje formal, objetivo, en tercera persona o voz impersonal
  ("se determina", "se observa"), no en primera persona narrativa
  ("determinamos", "vemos que").
- "Nosotros" / "nuestro" se acepta únicamente para referirse al equipo como
  autores de una decisión metodológica explícita (p. ej. "el equipo optó
  por..."), nunca como muletilla narrativa por defecto.
- Nada de coloquialismos, calcos del inglés ni intensificadores vacíos:
  "juega un rol" → "influye en"; "tan solo cinco estaciones" → "cinco
  estaciones"; "gran movimiento industrial" → "elevada actividad industrial".
- Nada de hedging informal ("podríamos considerar", "algo importante a tomar
  en cuenta"). Una afirmación se hace o se cita, no se sugiere a medias.
- Cero lenguaje emocional o de opinión ("increíble", "preocupante",
  "lamentablemente"). Los datos hablan por sí solos.

## Concisión y densidad

- Sin párrafos de calentamiento tipo ensayo ("en los últimos años se ha
  convertido en un tema de alta importancia..."). Ir directo al hecho.
- Una idea por oración. Si una oración necesita dos "y" para completarse,
  probablemente son dos oraciones.
- **No repetir contenido entre secciones.** Si un dato, cita o tabla ya
  aparece en otra sección, se referencia con `\cref`/`\Cref`, no se vuelve a
  explicar. Esto ya causó reescritura de la normativa NOM (citada en tres
  lugares con tres niveles de detalle) y de la descripción de SIMA (repetida
  casi igual en introducción y en su propia sección).
- **Filtro de alcance para ingeniería de datos:** antes de documentar un
  detalle de limpieza/ETL (banderas de calidad, valores centinela, huecos de
  rejilla temporal, inconsistencias de un documento de rangos), preguntar
  "¿esto es necesario para interpretar el análisis estadístico multivariado,
  o es proceso interno que no cambia ningún resultado?". Si es lo segundo,
  se reduce a una frase o se omite. El detalle exhaustivo (tablas con cada
  código de bandera, cada anomalía fila por fila) no pertenece al cuerpo del
  artículo.

## Números

- **Medidas van en dígitos aunque sean menores a diez** (unidades físicas,
  duraciones): "8 horas", no "ocho horas"; "1 hora, 8 horas, 24 horas" en la
  misma enumeración, nunca mezclado con palabras.
- **Cantidades menores a diez que no son medidas van en palabra**: "tres
  preguntas", "dos alternativas", "cinco estaciones" (como conteo, no como
  magnitud física).
- **Todo número ≥10 va en dígito**, sea medida o no: "15 niveles", "11
  variables", "23 unidades".
- **Excepción de comparación**: si en la misma oración se comparan o
  enumeran números menores y mayores a diez de la misma categoría, todos van
  en dígito para que se lean como una serie ("de las 13 estaciones que
  operaban, 7 registran...", no "trece estaciones... siete registran").
- **Decimales, no fracciones**: "0.5 %", nunca "la mitad" o "un tercio",
  salvo que la fracción sea el concepto mismo (raro en este reporte).

## Coherencia y precisión de citas

- Cada cita debe ser inequívoca. No dejar atribuciones ambiguas como "en el
  artículo de X o en Y et al. (...)" — si no se sabe con certeza de cuál
  fuente viene una afirmación, no se cita esa fuente, y no se menciona una
  fuente que no está en `references.bib`.
- Usar `\parencite`/`\textcite` de biblatex (estilo del documento). Nunca
  `\cite` a secas (es la sintaxis de natbib, incompatible con la clase).
- No describir una tabla o figura que ya no existe ("la tabla muestra
  que...") sin verificar que sigue en el documento tras un recorte. Si el
  dato vive solo en prosa, se dice así, sin fingir que hay una tabla detrás.

## Tablas y flotantes

- Los `table*` (ancho completo, a dos columnas) llevan `[t]` — es una regla
  dura de LaTeX en modo a dos columnas, no una preferencia. No forzar con
  `[H]` del paquete `float`: rompe el balance de columnas y dejaba huecos en
  blanco antes de corregirlo.
- Una tabla que se **discute activamente en el texto** (se interpreta línea
  por línea, se cita su valor en la prosa) se queda en el cuerpo, cerca de
  donde se cita.
- Una tabla **exhaustiva de referencia** (catálogo completo, matriz completa
  de resultados) que no se lee línea por línea en la prosa es candidata a
  apéndice, no al cuerpo principal.
- Cuando una figura comunica lo mismo que una tabla de números (loadings,
  correlaciones, dispersión de conglomerados), preferir la figura: es más
  densa por espacio ocupado.

## Estructura general

- Sin tabla de contenido (`\tableofcontents`): el documento imita un
  artículo de revista corto, no un reporte técnico largo o una tesis. La
  numeración de secciones y `\cref` ya cumplen la función de navegación.
- El resumen (`abstract`) es un solo párrafo, sin citas, sin fórmulas, sin
  referencias a secciones, y debe entenderse sin haber leído el resto del
  documento: problema → datos → método → resultado.

## Para revisiones automáticas (Claude)

Al revisar o escribir texto en `reports/secciones/*.tex`, aplicar esta guía
además de las convenciones de `CLAUDE.md`. Ante cambios de contenido grandes
(fusionar secciones, cortar detalle de ETL), proponer primero y esperar
confirmación antes de editar — no aplicar recortes de alcance de forma
unilateral.
