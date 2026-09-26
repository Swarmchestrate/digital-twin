"""
Main entry point for the digital twin logic.
"""

import json
import os
from pathlib import Path
from dt.scenario_builder import ScenarioBuilder
from dt.simulator import SimulatorRunner
import csv
from datetime import datetime

class DtEngine:

    def __init__(self, input_path: str | Path, jar: str | Path, output_path: str | Path, data_csv_path: str | Path, 
                 max_workers: int, timeout: int, keep_files: bool = False, seed: int = 1234567890, 
                 sort_field: str | None = None, sort_direction: str | None = None) -> None:
        cpu_count = os.cpu_count() or 1

        if max_workers < 1 or max_workers > cpu_count:
            max_workers = max(1, min(max_workers, cpu_count))

        if timeout <= 0:
            raise ValueError("timeout must be greater than 0")

        self.input_path = Path(input_path)
        self.data_csv_path = Path(data_csv_path)
            
        self.scenario_builder = ScenarioBuilder(seed)
        self.simulator_runner = SimulatorRunner(output_path, jar, data_csv_path, max_workers, timeout, keep_files)
        self.output_path = Path(output_path)
        self.sort_field = sort_field
        self.sort_direction = sort_direction

    def evaluate(self, request: dict) -> dict:
        """
        Build executable scenarios from the input request
        and pass them to the simulator layer.
        """
        
        print("Validating the input JSON request..")
        self.validate_request(request)

        print("Building scenarios..")
        scenarios = self.scenario_builder.build(request)
        raw_results = self.simulator_runner.run_scenarios(scenarios)

        recommendation = self._build_recommendation(raw_results)

        if request["metadata"]["application_type"] == "FuelicsParking":
            nbiot_value = recommendation["scenario_values"].get("nbiot-only")
            best_value = recommendation.get("best_value")

            if (
                nbiot_value is not None
                and best_value is not None
                and nbiot_value != 0
                and self.sort_field == "battery-consumed_percent"
                and self.sort_direction == "min"
            ):
                recommendation["comparison_to_nbiot_only_percent"] = (
                    (nbiot_value - best_value) / nbiot_value * 100.0
                )
                
        recommendation_file = self.output_path / "recommendation.json"
        with recommendation_file.open("w", encoding="utf-8") as f:
            json.dump(recommendation, f, indent=2, ensure_ascii=False)

        return recommendation

    def evaluate_file(self) -> dict:
        """
        Load the input request from a JSON file.
        """
        with Path(self.input_path).open("r", encoding="utf-8") as f:
            request = json.load(f)

        return self.evaluate(request)

    def _find_field(self, data: dict, field: str):
        if field in data:
            return data[field]

        for value in data.values():
            if isinstance(value, dict):
                try:
                    return self._find_field(value, field)
                except KeyError:
                    pass

        raise KeyError(f"Field '{field}' not found in simulator results")

    def _build_recommendation(self, raw_results: dict) -> dict:
        evaluated = []
        failed_scenarios = []

        for scenario in raw_results["scenarios"]:
            if scenario.get("returncode") != 0:
                failed_scenarios.append({
                    "scenario": scenario.get("scenario"),
                    "returncode": scenario.get("returncode"),
                    "stderr": scenario.get("stderr"),
                })
                continue

            metrics = scenario.get("metrics")
            if not isinstance(metrics, dict):
                failed_scenarios.append({
                    "scenario": scenario.get("scenario"),
                    "error": "Missing or invalid metrics",
                })
                continue

            try:
                value = self._find_field(metrics, self.sort_field)
            except KeyError:
                failed_scenarios.append({
                    "scenario": scenario.get("scenario"),
                    "error": f"Field '{self.sort_field}' not found in simulator results",
                })
                continue

            if not isinstance(value, (int, float)) or isinstance(value, bool):
                failed_scenarios.append({
                    "scenario": scenario.get("scenario"),
                    "error": f"Field '{self.sort_field}' must contain a numeric value",
                })
                continue

            evaluated.append({
                "scenario": scenario["scenario"],
                "value": value,
                "assignment": metrics.get("assignment"),
            })

        if not evaluated:
            return {
                "sort": {
                    "field": self.sort_field,
                    "direction": self.sort_direction,
                },
                "candidate_is_best": False,
                "best_scenario": None,
                "best_value": None,
                "best_assignment": None,
                "scenario_values": {},
                "failed_scenarios": failed_scenarios,
            }

        selector = min if self.sort_direction == "min" else max
        best_value = selector(item["value"] for item in evaluated)

        best_candidates = [
            item for item in evaluated
            if item["value"] == best_value
        ]

        priority = ["candidate", "current", "nbiot-only", "random"]

        best = min(
            best_candidates,
            key=lambda item: priority.index(item["scenario"])
        )

        return {
            "sort": {
                "field": self.sort_field,
                "direction": self.sort_direction,
            },
            "candidate_is_best": any(
                item["scenario"] == "candidate"
                for item in best_candidates
            ),
            "best_scenario": best["scenario"],
            "best_value": best["value"],
            "best_assignment": best["assignment"],
            "scenario_values": {
                item["scenario"]: item["value"]
                for item in evaluated
            },
            "failed_scenarios": failed_scenarios,
        }

    def validate_request(self, request: dict) -> None:
        if not isinstance(request, dict):
            raise ValueError("Input request must be a JSON object")

        metadata = request.get("metadata")
        if not isinstance(metadata, dict):
            raise ValueError("Missing or invalid metadata")

        application_type = metadata.get("application_type")
        if application_type not in {"InnoRenew", "FuelicsParking"}:
            raise ValueError(f"Unsupported application_type: {application_type}")

        prediction_horizon = metadata.get("prediction_horizon_min")
        if not isinstance(prediction_horizon, (int, float)) or prediction_horizon <= 0:
            raise ValueError("prediction_horizon_min must be greater than 0")

        resources = request.get("resources")
        if not isinstance(resources, list) or not resources:
            raise ValueError("resources must be a non-empty list")

        application = request.get("application")
        if not isinstance(application, dict):
            raise ValueError("Missing or invalid application")

        components = application.get("components")
        if not isinstance(components, list) or not components:
            raise ValueError("application.components must be a non-empty list")

        self._validate_prediction_horizon(prediction_horizon)

        self._validate_csv_sensor_columns(
            request["application"]["components"]
        )

    def _validate_csv_sensor_columns(self, components: list[dict]) -> None:

        with self.data_csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)

            if not reader.fieldnames:
                raise ValueError("Data CSV has no header")

            csv_columns = set(reader.fieldnames)

        sensor_ids = {
            component["component_id"]
            for component in components
                if component.get("properties", {}).get("component_type")
                in {"noise-sensor", "parking-sensor"}
        }

        missing = sensor_ids - csv_columns

        if missing:
            raise ValueError(
                "Missing sensor columns in CSV: "
                + ", ".join(sorted(missing))
            )

    def _validate_prediction_horizon(self, prediction_horizon_min: float) -> None:

        with self.data_csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)

            first_timestamp = None
            last_timestamp = None

            for row in reader:
                timestamp = row.get("timestamp")

                if not timestamp:
                    continue

                parsed = datetime.fromisoformat(timestamp)

                if first_timestamp is None:
                    first_timestamp = parsed

                last_timestamp = parsed

        if first_timestamp is None or last_timestamp is None:
            raise ValueError("CSV contains no valid timestamp data")

        available_minutes = (last_timestamp - first_timestamp).total_seconds() / 60.0

        if available_minutes < prediction_horizon_min:
            raise ValueError(
                f"CSV does not cover prediction horizon: "
                f"required={prediction_horizon_min} min, "
                f"available={available_minutes:.2f} min"
            )