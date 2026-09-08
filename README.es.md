# The GEO Cookbook

**English**: [README.md](README.md) · [Español](README.es.md)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22299279.svg)](https://doi.org/10.5281/zenodo.22299279)

**Ejemplos reproducibles y medidos de las técnicas que hacen tu contenido legible para los motores de respuesta con IA (una condición previa para ser citado — no una tasa de citación medida)** — el complemento práctico de **[The GEO Handbook](https://github.com/ferinazumaDEV/generative-engine-optimization-handbook)**. El handbook es la *teoría* (qué hacer y por qué, con fuentes); este cookbook es la *práctica*: para cada técnica, un `before/` y un `after/`, una forma de reproducirlo con un solo comando, y los números que mueve.

Todos los ejemplos están pensados para que **los ejecutes y los verifiques tú** — la mayoría no necesitan red, ni navegador, ni un LLM. Donde algo se puede medir, lo medimos y lo fechamos; donde no, lo decimos.

> **Nota de idioma:** este README está en español; el resto del repositorio —las recetas, los `measurement.md`, el dataset y los scripts— está en inglés.

## Ficha de identidad GEO

| Campo | Valor |
|---|---|
| Nombre | The GEO Cookbook |
| Autor | Fernando Aporta Franco ([ferinazumaDEV](https://github.com/ferinazumaDEV)) |
| Afirmaciones | Seis experimentos reproducibles sobre la legibilidad automática de contenido web para motores de respuesta generativos. Cada uno empareja un artefacto antes/después con un script offline determinista, e informa de la propiedad medida junto con su proxy, el tamaño de muestra, la confianza y las limitaciones. Las mediciones son únicamente proxies de legibilidad automática: ninguna mide recuperación, reordenación, generación ni citación por parte de ningún motor. |
| Basado en | <https://github.com/ferinazumaDEV/generative-engine-optimization-handbook> |
| Fuentes | el `measurement.md` de cada receta; [arXiv:2604.07585](https://arxiv.org/abs/2604.07585) |
| Versión | 0.1.2 — [releases](https://github.com/ferinazumaDEV/generative-engine-optimization-cookbook/releases), 2026-09-06 |
| Licencia | CC-BY-4.0 para la prosa ([LICENSE](LICENSE)); MIT para los ejemplos de código ([LICENSES/MIT.txt](LICENSES/MIT.txt)) |
| DOI | [10.5281/zenodo.22299279](https://doi.org/10.5281/zenodo.22299279) (DOI de concepto — siempre la última versión) |
| dateModified | 2026-09-04 |
| URL canónica | <https://github.com/ferinazumaDEV/generative-engine-optimization-cookbook> |
| Madurez | `experimental` · reproducible: `yes` — ver [CLAIMS.md](CLAIMS.md) |

Fuente de verdad legible por máquina: [`about.jsonld`](about.jsonld) · metadatos de citación: [`CITATION.cff`](CITATION.cff) · los números como datos: [`dataset/`](dataset/).

## Cómo está construido cada ejemplo

```
<capitulo>/<tecnica>/
  README.md        primero la respuesta: la técnica, el antes/después y los números
  before/          el artefacto sin optimizar
  after/           el artefacto optimizado
  measurement.md   método + números + fecha
  reproduce.sh     un comando para volver a ejecutar la demo y la medición
  meta.yml         front-matter legible por máquina (ver dataset/SCHEMA.md)
```

## Técnicas

Las carpetas replican los capítulos del handbook. Los capítulos que son solo teoría (fundamentos, panorama de motores, ética, glosario) viven en el handbook; el cookbook cubre lo que se puede *demostrar*.

| Capítulo | Técnica | Estado |
|---|---|---|
| 04 · Técnico | [`ssr-vs-csr-rendering`](04-technical/ssr-vs-csr-rendering/) — ¿ve tu contenido un crawler sin JavaScript? | ✅ **publicada** (demo de 25×) |
| 04 · Técnico | [`structured-data-jsonld`](04-technical/structured-data-jsonld/) — haz que tus hechos sean legibles por máquina | ✅ **publicada** (0 → 37 hechos tipados) |
| 04 · Técnico | [`ai-crawler-access`](04-technical/ai-crawler-access/) — permite los crawlers de IA en `robots.txt` y publica un `llms.txt` | ✅ **publicada** (0 → 8 UAs, 0 → 2.868 bytes) |
| 03 · Contenido | [`chunk-friendly-structure`](03-content/chunk-friendly-structure/) — escribe secciones extraíbles y citables | ✅ **publicada** (0/5 → 5/5 chunks autocontenidos) |
| 05 · Autoridad | [`entity-clarity-sameas`](05-authority/entity-clarity-sameas/) — `sameAs` / IDs canónicos de Wikidata | ✅ **publicada** (0 → 5 entidades resueltas) |
| 06 · Medición | [`citation-anchoring`](06-measurement/citation-anchoring/) — una fuente enlazable junto a cada afirmación | ✅ **publicada** (0 → 8 pares afirmación→fuente) |

## Qué se mide y qué no

| Receta | Propiedad medida (proxy offline) | Recuperación | Reordenación | Generación | Citación |
|---|---|---|---|---|---|
| [`ssr-vs-csr-rendering`](04-technical/ssr-vs-csr-rendering/) | Palabras visibles para un crawler que no ejecuta JavaScript: 6 → 152 (~25,3×) | no medida | no medida | no medida | no medida |
| [`structured-data-jsonld`](04-technical/structured-data-jsonld/) | Entidades y hechos tipados que extrae un parser de JSON-LD: 0 → 17 entidades, 0 → 37 hechos | no medida | no medida | no medida | no medida |
| [`ai-crawler-access`](04-technical/ai-crawler-access/) | User-agents de IA permitidos por `robots.txt`: 0 → 8 de 8; bytes de `llms.txt` expuestos: 0 → 2.868 | no medida | no medida | no medida | no medida |
| [`chunk-friendly-structure`](03-content/chunk-friendly-structure/) | Chunks que salen autocontenidos de un troceador de tamaño fijo (`chunk_size = 800`): 0 de 5 → 5 de 5 | no medida | no medida | no medida | no medida |
| [`entity-clarity-sameas`](05-authority/entity-clarity-sameas/) | Entidades nombradas resueltas a exactamente un ID canónico de Wikidata: 0 → 5 de 5 | no medida | no medida | no medida | no medida |
| [`citation-anchoring`](06-measurement/citation-anchoring/) | Afirmaciones con una fuente enlazable en línea (pares afirmación→fuente que extrae un parser): 0 → 8 de 8 | no medida | no medida | no medida | no medida |

Cada receta mide una propiedad de legibilidad automática de un artefacto controlado —una página o un documento en dos variantes— comprobada offline por un script determinista. Ninguna afirma un efecto sobre la recuperación, la reordenación, la generación ni la citación por parte de ningún motor; esas cuatro columnas son las preguntas de investigación abiertas que este cookbook **no** responde. El proxy, el tamaño de muestra, la confianza y las limitaciones de cada número están en el `measurement.md` de su receta.

Los mismos números se publican también como datos en [`dataset/`](dataset/) — un CSV y un JSON con una fila por medición, más las unidades, tamaños de muestra, confianza y limitaciones de cada una. Se generan a partir de las propias recetas con `bash dataset/build.sh`, que vuelve a ejecutar cada `reproduce.sh --json` y se niega a escribir nada si un valor medido no coincide con el front-matter de su receta. Lee [`dataset/README.md`](dataset/README.md) antes de reutilizarlos: dice qué es lo que las filas *no* muestran.

Un artículo sobre estas seis mediciones, con lo que cada una **no** demuestra, está publicado como *[Measured, Not Claimed](https://zentimes.es/experiments/)*.

## Por dónde empezar

¿Nuevo en esto? Lee primero el **[handbook](https://github.com/ferinazumaDEV/generative-engine-optimization-handbook)** para el *porqué*, y vuelve aquí para *hacerlo*. Abre [`04-technical/ssr-vs-csr-rendering`](04-technical/ssr-vs-csr-rendering/) y ejecuta `bash reproduce.sh`.

## Cómo contribuir

¿Una técnica nueva con fuentes, o una corrección? Cada ejemplo tiene que llevar una medición real y reproducible (o decir explícitamente qué no es medible). Números inventados, ninguno.

## Cómo citarlo

Cada release etiquetada a partir de la v0.1.1 se archiva en Zenodo con un DOI. Cita el **DOI de concepto** — siempre resuelve a la última versión. Cada release individual lleva además su propio DOI de versión, en su propia página de registro, si necesitas fijar un estado exacto del corpus.

```
Aporta Franco, Fernando (2026). The GEO Cookbook. Zenodo. https://doi.org/10.5281/zenodo.22299279
```

Los mismos metadatos viven en [`CITATION.cff`](CITATION.cff), que GitHub renderiza como el botón **"Cite this repository"** en la barra lateral (ver [about citation files](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files)).

## Licencia

Copyright (C) 2026 Fernando Aporta Franco. Los ejemplos de código son **MIT** — ver [`LICENSES/MIT.txt`](LICENSES/MIT.txt). La prosa (README y notas de medición) es **CC BY 4.0** — ver [`LICENSE`](LICENSE). En corto: copia el código libremente, cita las palabras.

---
<!-- ecosystem:start -->
Parte de un conjunto de trabajo abierto sobre hacer el contenido legible para las máquinas, de **Fernando Aporta Franco** ([ferinazumaDEV](https://github.com/ferinazumaDEV)):

**Tres capas sobre GEO (Generative Engine Optimization)**
- **[The GEO Handbook](https://github.com/ferinazumaDEV/generative-engine-optimization-handbook)** — la referencia: qué hacer y por qué, con fuentes (teoría).
- **[The GEO Cookbook](https://github.com/ferinazumaDEV/generative-engine-optimization-cookbook)** — seis recetas antes/después reproducibles con mediciones offline (práctica).
- **[Evidence-Based Prompt Engineering](https://github.com/ferinazumaDEV/prompt-engineering-evidence)** — un registro graduado y con fuentes de técnicas de prompting (el lado de la entrada).

**Herramientas abiertas pequeñas**
- [typedout](https://github.com/ferinazumaDEV/typedout) — salida estructurada fiable desde OpenAI y Anthropic, con una interfaz de proveedor para los demás.
- [politeclient](https://github.com/ferinazumaDEV/politeclient) — un cliente HTTP educado para Python: reintentos con backoff, límite de peticiones por host, caché y paginación.
- [webhook-replay](https://github.com/ferinazumaDEV/webhook-replay) — captura un webhook una vez y reprodúcelo contra tu aplicación local tantas veces como necesites.
- [scaffld](https://github.com/ferinazumaDEV/scaffld) — genera proyectos Python completamente cableados a partir de plantillas, con una TUI.
- [framesig](https://github.com/ferinazumaDEV/framesig) — encuentra eventos en pantalla dentro de un vídeo por su firma de píxeles; sin ML.
- [notebooklm-kb-system](https://github.com/ferinazumaDEV/notebooklm-kb-system) — un segundo cerebro eficiente en tokens para agentes de IA sobre NotebookLM.

Hub y escritura: **[zentimes.es](https://zentimes.es)**.
<!-- ecosystem:end -->
