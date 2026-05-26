"""Fixed model factories for tabular rolling-origin experiments."""
from __future__ import annotations


def make_lightgbm():
    from lightgbm import LGBMRegressor
    return LGBMRegressor(
        n_estimators=50, learning_rate=0.1,
        num_leaves=31, random_state=42, verbose=-1
    )


def make_ridge():
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import Ridge
    return make_pipeline(StandardScaler(), Ridge(alpha=1.0))


def make_extratrees():
    from sklearn.ensemble import ExtraTreesRegressor
    # n_estimators=50 chosen for computational feasibility on rolling-origin loops
    # (100 trees quadrupled runtime on 16-core laptop due to thermal throttling)
    return ExtraTreesRegressor(
        n_estimators=50, random_state=42, n_jobs=-1
    )


def make_knn():
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.neighbors import KNeighborsRegressor
    # StandardScaler required: KNN is Euclidean-distance-based
    return make_pipeline(
        StandardScaler(),
        KNeighborsRegressor(n_neighbors=5, weights="uniform", metric="euclidean"),
    )


def make_mlp():
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.neural_network import MLPRegressor
    # StandardScaler required before MLP
    return make_pipeline(
        StandardScaler(),
        MLPRegressor(
            hidden_layer_sizes=(64, 32),
            activation="relu",
            solver="adam",
            max_iter=500,
            early_stopping=True,
            validation_fraction=0.1,
            random_state=42,
            n_iter_no_change=10,
        ),
    )


def make_tcn():
    from tcn_model import TCNRegressor
    return TCNRegressor(
        channels=(32, 32, 32),
        kernel_size=3,
        dilations=(1, 2, 4),
        lr=0.001,
        epochs=100,
        batch_size=64,
        patience=10,
        random_state=42,
    )
