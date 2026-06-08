# q1_execution_plan.md

# paper2H: plan de cierre Q1

## Veredicto

Este paper debe cerrarse como paper metodologico general, no como benchmark amplio ni como paper de calidad del aire. Su valor esta en formalizar H* como descriptor operativo baseline-relative para comparar utilidad predictiva multi-horizonte en dominios heterogeneos.

Prioridad: cerrar antes que nuevos experimentos de la linea H*.

Fuente canonica del manuscrito: Overleaf.

Repo de soporte: `/Users/federicogarciacrespi/Public/paper2H`.

## Pregunta y claim

Pregunta:

> Puede H* describir la utilidad operacional baseline-relative de modelos multi-horizonte en dominios heterogeneos bajo un protocolo temporal leakage-free?

Claim principal:

> La utilidad predictiva multi-horizonte no queda bien resumida por metricas agregadas ni por unos pocos lead times fijos. Una lectura horizon-wise de Skill(h), junto con H*(relax), H*(strict), intervalos positivos y fragmentacion, permite comparar la persistencia, continuidad y alcance de la utilidad operacional entre dominios.

## Papel dentro de la linea

Este paper es la referencia conceptual de H*.

No debe mezclarse con:

- variance retention / Skill_VP;
- ghost skill;
- DPR/KGE/DILATE;
- papers PM10 enviados;
- paper TAC Madrid-Irlanda.

Puede compartir protocolo:

- rolling-origin;
- train-only preprocessing;
- persistence baseline;
- Skill(h);
- DM/BH cuando aplique.

## Decisiones editoriales

### Target principal

Opcion ambiciosa:

- `International Journal of Forecasting`

Razon:

- paper metodologico de evaluacion forecast;
- cross-domain;
- foco en baseline-relative usefulness y horizon descriptors.

Riesgo:

- IJF exigira claridad formal, comparabilidad y una narrativa muy limpia.

### Targets alternativos

- `Environmental Modelling & Software`: si se enfatiza framework reproducible y dominios ambientales.
- `Expert Systems with Applications`: si se enfatiza benchmarking ML y utilidad operativa.
- `Data Mining and Knowledge Discovery`: solo si el framing data-mining/methodological evaluation queda muy fuerte.

## Cierre por fases

### Fase 1: sincronizacion Overleaf-repo

Objetivo:

Evitar que repo y manuscrito visible diverjan.

Acciones:

1. Exportar desde Overleaf la version canonica del `.tex`, `.bib`, figuras y tablas.
2. Guardar en el repo una copia estable bajo `paper/`.
3. Registrar en `docs/q1_closeout_decisions.md` la fecha/hash o version Overleaf.
4. No editar el `.tex` local antiguo si no coincide con Overleaf: reemplazarlo de forma controlada tras backup.

Criterio de cierre:

- el PDF visible puede generarse desde los archivos versionados o, como minimo, el repo documenta exactamente que Overleaf es la fuente canonica y que archivos exportar.

### Fase 2: congelar la tabla cross-domain

Objetivo:

Que la comparacion de seis dominios no parezca arbitraria.

Dominios a congelar:

- PM2.5;
- electric load;
- wind;
- traffic;
- PM10 Madrid;
- PM10 Barcelona.

Acciones:

1. Crear una tabla final de dominios con:
   - dataset;
   - periodo;
   - frecuencia;
   - horizonte maximo;
   - numero de origenes;
   - baseline;
   - modelos evaluados;
   - metrica primaria.
2. Justificar diferencias de frecuencia y horizonte como propiedad del dominio, no como inconsistencia.
3. Incluir una frase clara: el paper compara perfiles de utilidad baseline-relative, no capacidad absoluta entre dominios.

Criterio de cierre:

- cualquier reviewer puede entender por que esos dominios son comparables bajo el protocolo.

### Fase 3: auditar resultados y trazabilidad

Objetivo:

Cada tabla/figura debe tener fuente clara.

Acciones:

1. Mapear cada figura y tabla del manuscrito a:
   - CSV fuente;
   - script productor;
   - carpeta de output.
2. Separar outputs canónicos de outputs exploratorios.
3. Mover artefactos no usados a una carpeta `archive/` o documentar que son exploratorios antes de commit.
4. Revisar artefactos no trackeados:
   - `traffic_moving_average_*`;
   - `rmse_sensitivity_check`;
   - `overleaf_export`.

Criterio de cierre:

- lista `docs/figure_table_traceability.md` o equivalente con todas las fuentes.

### Fase 4: reforzar narrativa Q1

Objetivo:

Evitar desk reject por "too broad" o "only benchmark".

Cambios narrativos imprescindibles:

1. Introduccion:
   - problema: fixed-horizon summaries ocultan utilidad operacional;
   - gap: falta descriptor de alcance y continuidad baseline-relative;
   - solucion: H*(relax), H*(strict), intervalos y fragmentacion.
2. Related work:
   - forecast evaluation;
   - forecast skill;
   - predictability limits / Lorenz;
   - rolling-origin;
   - operational evaluation.
3. Methods:
   - definir H* como evaluacion, no como propiedad absoluta del sistema;
   - recalcar dependencia de baseline, metrica, dominio y protocolo.
4. Discussion:
   - baseline competitiveness;
   - por que strict y relax responden preguntas diferentes;
   - por que fragmentacion importa.

Criterio de cierre:

- el paper se lee como contribucion metodologica de evaluacion, no como coleccion de datasets.

### Fase 5: robustez y sensibilidad

Objetivo:

Prevenir objeciones sobre dependencia de metrica/modelo.

Acciones:

1. Mantener sensibilidad MAE/RMSE si ya esta madura.
2. Mantener modelos extra solo si son protocol-matched y no expanden artificialmente el paper.
3. Reportar DM/BH solo donde este bien definido.
4. No abrir nuevas familias de modelos.

Criterio de cierre:

- robustez apoya el claim metodologico sin cambiar el foco.

### Fase 6: reproducibilidad minima

Objetivo:

Que el repo sostenga el paper.

Acciones:

1. Completar `requirements.txt`.
2. Crear o actualizar `RUN_ORDER.md` si falta.
3. Documentar datos pesados externos:
   - `LD2011_2014.txt`;
   - `pems-bay.h5`;
   - `metr-la.h5`.
4. Confirmar que no hay rutas absolutas activas.
5. Definir outputs canónicos.

Criterio de cierre:

- un lector sabe que scripts producen los resultados principales, aunque no se empaqueten datos pesados.

### Fase 7: submission package

Acciones:

1. Generar PDF final desde Overleaf.
2. Exportar source package.
3. Revisar referencias.
4. Revisar captions para que expliquen H*(relax), H*(strict) y fragmentacion.
5. Preparar cover letter centrada en la contribucion metodologica.

## Cambios imprescindibles antes de submit

- Sincronizar Overleaf y repo.
- Congelar tabla de seis dominios.
- Documentar trazabilidad figura/tabla.
- Reforzar que H* depende de baseline/metrica/protocolo.
- Separar PM10 Madrid/Barcelona como evidencia de generalidad, no como paper PM.

## Mejoras de alto impacto

- Figura conceptual de Skill(h) -> H*(relax)/H*(strict) -> fragmentacion.
- Tabla clara de perfiles por dominio.
- Sensibilidad MAE/RMSE en suplemento.
- Discusion fuerte sobre baseline competitiveness.

## No hacer

- No meter variance retention ni Skill_VP.
- No ampliar con mas dominios.
- No abrir probabilistic forecasting.
- No mezclar con resultados TAC o Madrid/Valencia.
- No convertirlo en paper ambiental.

## Proximo paso tecnico

Auditar el repo contra el PDF/Overleaf y crear:

- `docs/figure_table_traceability.md`
- `RUN_ORDER.md` si no existe
- `docs/data_external.md`
