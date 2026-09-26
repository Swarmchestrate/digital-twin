# Fuelics Parking Digital Twin Example

This example demonstrates the Fuelics parking-monitoring Digital Twin.

The Digital Twin takes:
- a Digital Twin input JSON describing the infrastructure, parking sensors, application components and requested reconfigurations;
- a CSV dataset containing timestamped parking events for the configured sensors.

From this input, the Python library generates multiple simulation scenarios, executes them with DISSECT-CF-Fog, and produces a recommendation based on the configured optimization metric.

The Digital Twin produces:

- `recommendation.json` – final Digital Twin recommendation, including the best scenario and its sensor assignment;
- `raw_results.json` – collected raw results of the executed scenarios;
- scenario-specific JSON files and simulator output directories when intermediate files are kept.

## Generated scenarios

For a Fuelics parking request, the Digital Twin creates four scenarios:

| Scenario | Description |
|---|---|
| `nbiot-only` | Baseline scenario where every parking sensor uses `NBIOT_PUSH`. |
| `current` | Uses the current sensor modes from the input JSON without applying requested operations. |
| `candidate` | Applies the sensor-mode reconfigurations from `operations`. |
| `random` | Generates a complete random assignment of `NBIOT_PUSH` / `BLE_POLL` modes. |

Each scenario is converted into a scenario-specific input JSON and executed independently by DISSECT-CF-Fog.

## Input JSON

### Metadata

| Field | Description |
|---|---|
| `request_id` | Identifier of the Digital Twin request. |
| `application_type` | Must be `FuelicsParking`. |
| `prediction_horizon_min` | Simulation horizon in minutes. The CSV dataset must cover at least this period. |
| `scaling_cooldown_ms` | Scaling/reconfiguration cooldown used by the parking simulation. |
| `ble_polling_interval_ms` | BLE polling interval in milliseconds. |

### Resources

`resources` contains the platform and gateway nodes.

| Field | Description |
|---|---|
| `node_id` | Unique resource identifier. |
| `node_type` | `cloud` for the platform or `edge` for a gateway. |
| `cpu_cores` | Available CPU cores. |
| `memory_mb` | Available memory in MB. |
| `storage_gb` | Available storage in GB. |
| `min_power_w` | Minimum power consumption. |
| `idle_power_w` | Idle power consumption. |
| `max_power_w` | Maximum power consumption. |
| `network_latency_ms` | Network latency associated with the resource. |
| `network_bandwidth_bytes_per_ms` | Network bandwidth in bytes/ms. |

### Application

| Field | Description |
|---|---|
| `application_id` | Unique identifier of the parking application. |
| `components` | List of parking sensors and application service components. |

### Parking sensor components

Parking sensors are defined under `application.components`.

| Field | Description |
|---|---|
| `component_id` | Unique sensor ID. Must match a sensor column in the CSV dataset. |
| `assigned_resource` | Gateway assigned to the sensor. |
| `properties.component_type` | Must be `parking-sensor`. |
| `properties.battery_level` | Initial battery level. |
| `properties.mode` | Initial mode: `NBIOT_PUSH` or `BLE_POLL`. |
| `properties.nbiot_network_latency_ms` | NB-IoT latency. |
| `properties.nbiot_network_bandwidth_bytes_per_ms` | NB-IoT bandwidth. |
| `properties.ble_network_latency_ms` | BLE latency. |
| `properties.ble_network_bandwidth_bytes_per_ms` | BLE bandwidth. |

### Application services

The application may also contain service components such as the BLE reconfiguration services, NB-IoT reconfiguration service and platform service.

| Field | Description |
|---|---|
| `component_id` | Unique component identifier. |
| `assigned_resource` | Resource where the component is deployed. |
| `cpu_request_cores` | Requested CPU cores. |
| `memory_request_mb` | Requested memory. |
| `properties.component_type` | Application component type. Supported values used by the parking model are `ble_reconfiguration`, `nbiot_reconfiguration` and `server`. |
| `properties.image_size_bytes` | Container image size. |

### Operations

`operations` describes the requested parking-sensor configuration.

| Field | Description |
|---|---|
| `type` | `sensor_mode_reconfiguration`. |
| `component_id` | Parking sensor to reconfigure. |
| `target_mode` | Desired mode: `NBIOT_PUSH` or `BLE_POLL`. |

## Parking dataset

The CSV must contain:

| Column | Description |
|---|---|
| `timestamp` | Timestamp of the sample. |
| `<sensor-id>` | `1` indicates that a parking event occurred at that timestamp. An empty field means that no parking event occurred. |

Each parking sensor defined in the input JSON must have a matching CSV column.

The dataset must cover at least the configured `prediction_horizon_min`.

Example:

```csv
timestamp,parking-sensor1,parking-sensor2,parking-sensor3
2026-01-01T00:00:00,,,1
2026-01-01T00:01:00,1,,
```
