# InnoRenew Noise Monitoring Digital Twin Example

This example demonstrates the InnoRenew noise-monitoring Digital Twin.

The Digital Twin takes:
- a Digital Twin input JSON describing the infrastructure, noise sensors, application components and requested classifier reconfigurations;
- a CSV dataset containing timestamped sound-level measurements for the configured sensors.

From this input, the Python library generates multiple simulation scenarios, executes them with DISSECT-CF-Fog, and produces a recommendation based on the configured optimization metric.

The Digital Twin produces:

- `recommendation.json` – final Digital Twin recommendation, including the best scenario and its sensor assignment;
- `raw_results.json` – collected raw results of the executed scenarios;
- scenario-specific JSON files and simulator output directories when intermediate files are kept.

## Generated scenarios

For an InnoRenew request, the Digital Twin creates three scenarios:

| Scenario | Description |
|---|---|
| `current` | Uses the current classifier configuration from the input JSON without applying requested operations. |
| `candidate` | Applies the classifier reconfigurations from `operations`. |
| `random` | Generates a complete random classifier assignment for all noise sensors. |

Each scenario is converted into a scenario-specific input JSON and executed independently by DISSECT-CF-Fog.

## Input JSON

### Metadata

| Field | Description |
|---|---|
| `request_id` | Identifier of the Digital Twin request. |
| `application_type` | Must be `InnoRenew`. |
| `prediction_horizon_min` | Simulation horizon in minutes. The CSV dataset must cover at least this period. |
| `scaling_cooldown_ms` | Scaling/reconfiguration cooldown in milliseconds. |
| `sound_level_threshold` | Sound-level threshold used by the noise-monitoring logic. |
| `cpu_temperature_threshold` | CPU temperature threshold used by the scaling logic. |
| `min_cpu_temperature` | Minimum CPU temperature used by the simulation. |
| `max_cpu_temperature` | Maximum CPU temperature used by the simulation. |
| `min_container_count` | Minimum number of classifier containers. |
| `cpu_load_scale_up` | CPU-load threshold for scaling up. |
| `cpu_load_scale_down` | CPU-load threshold for scaling down. |

### Resources

`resources` contains the edge and cloud nodes used by the application.

| Field | Description |
|---|---|
| `node_id` | Unique resource identifier. |
| `node_type` | `edge` for sensor-side nodes or `cloud` for the remote server. |
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
| `application_id` | Unique identifier of the noise-monitoring application. |
| `components` | List of noise sensors and application service components. |

### Noise sensor components

Noise sensors are defined under `application.components`.

| Field | Description |
|---|---|
| `component_id` | Unique sensor ID. Must match a sensor column in the CSV dataset. |
| `assigned_resource` | Resource where the sensor component is deployed. |
| `cpu_request_cores` | Requested CPU cores. |
| `memory_request_mb` | Requested memory. |
| `properties.component_type` | Must be `noise-sensor`. |
| `properties.image_size_bytes` | Container image size. |
| `properties.cpu_temperature` | Initial CPU temperature of the sensor. |
| `properties.classifier` | Initial classifier state: `true` or `false`. |
| `properties.queue_length` | Number of initially queued sound files. |
| `properties.inside` | Indicates whether the sensor is located indoors. |
| `properties.sun` | Indicates whether the sensor is exposed to direct sunlight. |

### Application services

The application may also contain service components such as the remote server.

| Field | Description |
|---|---|
| `component_id` | Unique component identifier. |
| `assigned_resource` | Resource where the component is deployed. |
| `cpu_request_cores` | Requested CPU cores. |
| `memory_request_mb` | Requested memory. |
| `properties.component_type` | Application component type. Supported values used by the noise model are `noise-sensor` and `server`. |
| `properties.image_size_bytes` | Container image size. |

### Operations

`operations` describes the requested classifier configuration.

| Field | Description |
|---|---|
| `type` | `classifier_reconfiguration`. |
| `component_id` | Noise sensor to reconfigure. |
| `classifier` | Desired classifier state: `true` to enable it or `false` to disable it. |

## Noise dataset

The CSV must contain:

| Column | Description |
|---|---|
| `timestamp` | Timestamp of the sound-level sample. |
| `<sensor-id>` | Sound-level value measured by the corresponding noise sensor. |

Each noise sensor defined in the input JSON must have a matching CSV column.

The dataset must cover at least the configured `prediction_horizon_min`.

Example:

```csv
timestamp,noise-sensor1,noise-sensor2,noise-sensor3
2026-04-02T14:25:13.996,69,59,115
2026-04-02T14:25:23.996,88,58,85
```
