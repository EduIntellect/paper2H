# Datasets

This project evaluates forecast skill horizon (H*) on multiscale environmental and infrastructure time series using four benchmark datasets:

- **OpenAQ PM2.5**: Ground-monitor observations of near-surface particulate matter (PM2.5, µg/m³), used to study short-term air-quality predictability.
- **PJM electricity load**: Regional system demand (MW) from the PJM interconnection, representing aggregated human-activity and weather-driven load dynamics.
- **NREL Wind Toolkit**: High-resolution meteorological/wind power proxies from mesoscale simulations, used for wind-speed and renewable-generation forecasting experiments.
- **PeMS traffic**: Freeway loop-detector measurements (flow, speed, occupancy) from California's Performance Measurement System, used to analyze transportation demand predictability.

Together, these datasets provide complementary regimes (atmospheric chemistry, power systems, wind fields, and traffic networks) for testing horizon-dependent forecast skill under persistence and simple statistical baselines.
