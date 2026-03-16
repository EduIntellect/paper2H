# Datasets

This project evaluates forecast skill horizon (H*) on multiscale environmental and infrastructure time series using four benchmark datasets:

- **OpenAQ PM2.5**: Ground-monitor observations of near-surface particulate matter (PM2.5, µg/m³), used to study short-term air-quality predictability.
- **PJM electricity load**: Regional system demand (MW) from the PJM interconnection, representing aggregated human-activity and weather-driven load dynamics.
- **NREL Wind Toolkit**: High-resolution meteorological/wind power proxies from mesoscale simulations, used for wind-speed and renewable-generation forecasting experiments.
- **PeMS traffic**: Freeway loop-detector measurements (flow, speed, occupancy) from California's Performance Measurement System, used to analyze transportation demand predictability.

Together, these datasets provide complementary regimes (atmospheric chemistry, power systems, wind fields, and traffic networks) for testing horizon-dependent forecast skill under persistence and simple statistical baselines.
This project evaluates predictability horizons across multiple real-world systems using public time series datasets.

Domains and datasets
Domain	Dataset	Variable	Frequency
Air quality	OpenAQ	PM2.5	hourly
Energy	PJM	electric load	hourly
Wind	NREL Wind Toolkit	wind speed	hourly
Traffic	PeMS / METR-LA	traffic flow	5-min
Dataset used in current experiment
PM2.5 dataset:

Source: Beijing PM2.5 dataset
Variable: PM2.5 concentration
Frequency: hourly
