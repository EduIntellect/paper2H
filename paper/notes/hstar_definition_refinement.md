Building upon the preliminary definition of the operational predictability horizon (H*) introduced in [Paper 1], this study adopts a slightly refined operational criterion suitable for cross-domain forecasting experiments.

In the original formulation, H* was defined as the supremum of the forecast horizons for which the model skill relative to a baseline remains positive. While this definition is appropriate for single-system model comparisons, our multi-domain analysis revealed that the skill function may occasionally exhibit stochastic recoveries at long horizons due to noise or smoothing effects.

To ensure a more stable estimate of the effective forecasting limit, we therefore operationalize H* as the last horizon before the first zero-crossing of the skill curve. This criterion identifies the contiguous interval in which the forecasting model consistently outperforms the baseline and avoids spurious improvements that may appear at distant horizons.

Importantly, this refinement does not alter the conceptual meaning of H* as an operational predictability horizon; rather, it provides a more robust estimator when comparing heterogeneous systems with different dynamical properties.
