# Auditoría del pipeline — paper2H

## Script principal de evaluación

- **Ruta:** `src/rolling_origin_evaluator.py`
- **Función de rolling-origin:** `run_evaluation(series, models, horizons, lags, stride, min_train, max_train, max_origins, domain) → pd.DataFrame`
- **Función de cálculo de Skill(h):** inline en cada script de experimento — `1 - mae_model / mae_baseline`
- **Función de cálculo de H*:** `src/compute_hstar.py` → `compute_hstar(skill_series, horizons)`
- **DM tests:** `src/dm_tests.py` → `dm_test(errs_model, errs_baseline, h)` + `benjamini_hochberg(pvals)`

## Cómo se añade un modelo nuevo

Los modelos se definen como factories en: **`src/models_tabular.py`**

Interfaz requerida: **sklearn-compatible** — cualquier objeto con métodos `.fit(X, y)` y `.predict(X)`.

El evaluador hace `clone(estimator).fit(X_tr, y_tr)` en cada (horizon, origin), por lo que el modelo debe ser cloneable con `sklearn.base.clone`. Todos los estimadores sklearn y los pipelines sklearn lo cumplen. Un wrapper personalizado debe heredar de `BaseEstimator`.

Parámetros de lag/features:
- Las features son el vector de lags en el momento del origen: `X[origin] = [series[origin - lag] for lag in lags]`
- `lag=0` → el valor en t₀ (el último dato conocido, que también es el baseline de persistencia)
- El evaluador construye la lag matrix una sola vez y la reutiliza para todos los modelos → añadir un modelo no ralentiza la construcción de features

Para añadir KNN/MLP/TCN basta con:
1. Añadir factories `make_knn()`, `make_mlp()`, `make_tcn()` en `src/models_tabular.py`
2. Añadir las entradas correspondientes al dict `MODELS` en el script de experimento

## Datasets presentes en `data/`

- [x] PM2.5 Beijing → `pm25_series.csv` (columna `PM25`, 41 757 filas hourly)
- [x] Electric Load UCI → `uci_electricity_daily_aggregate.csv` en `results/` (**no en data/**); el raw está en `data/LD2011_2014.txt` y `data/electricityloaddiagrams20112014.zip`
- [x] Wind NREL → `wind_hourly_clean.csv` (columna `value`, 8 760 filas)
- [x] Traffic METR-LA → `traffic_hourly_clean.csv` (columna `value`, 2 856 filas); raw en `data/metr-la.h5`
- [x] PM10 Madrid → `pm10_elx_daily.csv` (columna `pm10`, 2 922 filas)
- [x] PM10 Barcelona → `pm10_bcn_daily.csv` (columna `pm10`, 2 827 filas)

## Datasets que FALTAN en data/

**Ninguno.** Todos los dominios tienen el CSV limpio listo para el evaluador.

Nota: `load_predictions_all.csv` en `results/` usa el agregado diario de UCI ya procesado. El script de experimento lo lee de `results/uci_electricity_daily_aggregate.csv`, no de `data/`. Esto es consistente con el pipeline actual.

## Formato de resultados

- **Formato:** CSV
- **Ruta de predictions:** `results/{domain}_predictions_all.csv`
- **Ruta de skill:** `results/{domain}_skill_all.csv`
- **Columnas de predictions_all.csv:**
  `domain, model, horizon, origin_idx, origin_timestamp, y_true, y_pred, y_pred_baseline, abs_error_model, abs_error_baseline`
- **Columnas de skill_all.csv:**
  `domain, model, horizon, n_origins, mae_model, mae_baseline, skill`
- **Tablas agregadas:** `results/hstar_all_domains.csv`, `results/dm_tests_all.csv`, `results/hstar_summary.csv`, `results/unified_results_table.csv`

## Configuración por dominio (lags, stride, límites)

| Domain | Horizons | Lags | Stride | min_train | max_train | max_origins | Script |
|--------|----------|------|--------|-----------|-----------|-------------|--------|
| pm25 | 1–48 | [0,1,2,3,6,12,24,48] | 24 | 200 | 720 | 365 | `experiments/run_all_domains.py` |
| load | 1–7 | [0,1,2,3,7,14] | 1 | 365 | None | None | `experiments/run_all_domains.py` |
| wind | 1–48 | [0,1,2,3,6,12,24,48] | 24 | 200 | 720 | 365 | `experiments/run_all_domains.py` |
| traffic | 1–72 | [0,1,2,3,6,12,24,48] | 24 | 200 | 720 | 180 | `experiments/run_all_domains.py` |
| pm10 | 1–7 | [0,1,2,3,7,14] | 1 | 365 | None | None | `experiments/run_pm10.py` |
| pm10_bcn | 1–7 | [0,1,2,3,7,14] | 1 | 365 | None | None | `experiments/run_pm10_bcn.py` |

## Dependencias instaladas

- scikit-learn 1.8.0 ✓
- lightgbm 4.6.0 ✓
- numpy, pandas, matplotlib ✓
- **torch: NO instalado** → debe instalarse para TCN (CPU build)

## Firma de fit/predict requerida

```python
# Mínimo viable — sklearn-compatible:
from sklearn.base import BaseEstimator, RegressorMixin

class MyModel(BaseEstimator, RegressorMixin):
    def fit(self, X: np.ndarray, y: np.ndarray) -> "MyModel": ...
    def predict(self, X: np.ndarray) -> np.ndarray: ...
```

`X` tiene shape `(n_samples, n_lags)` donde `n_lags = len(lags)` del dominio.
`y` es 1-D de longitud `n_samples`.
`predict` se llama con `X` de shape `(1, n_lags)` en cada origen.
