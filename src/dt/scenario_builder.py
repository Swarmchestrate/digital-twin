"""
Build simulation inputs for each scenario.
"""

import copy
import random

class ScenarioBuilder:
    """Builds executable scenarios from a digital twin request."""

    def __init__(self, random_seed: int = 1234567890) -> None:
        self.random_seed = random_seed

    def build(self, request: dict) -> list[dict]:
        application_type = request["metadata"]["application_type"]

        if application_type == "InnoRenew":
            return self._build_innorenew_scenarios(request)

        if application_type == "FuelicsParking":
            return self._build_parking_scenarios(request)

        raise ValueError(f"Unsupported application type: {application_type}")

    def _build_innorenew_scenarios(self, request: dict) -> list[dict]:
        original_request_id = request["metadata"]["request_id"]

        candidate_scenario = copy.deepcopy(request)
        candidate_scenario["metadata"]["request_id"] = (
            f"{original_request_id}-candidate"
        )

        current_scenario = copy.deepcopy(request)
        current_scenario["metadata"]["request_id"] = (
            f"{original_request_id}-current"
        )
        current_scenario["operations"] = []

        rng = random.Random(self.random_seed)

        random_scenario = copy.deepcopy(candidate_scenario)
        random_scenario["metadata"]["request_id"] = (
            candidate_scenario["metadata"]["request_id"].rsplit("-", 1)[0] + "-random"
        )

        random_operations = []

        for component in random_scenario["application"]["components"]:
            if component.get("properties", {}).get("component_type") != "noise-sensor":
                continue

            random_operations.append({
                "type": "classifier_reconfiguration",
                "component_id": component["component_id"],
                "classifier": rng.choice([True, False]),
            })

        random_scenario["operations"] = random_operations

        return [
            {
                "name": "candidate",
                "request": candidate_scenario,
            },
            {
                "name": "current",
                "request": current_scenario,
            },
            {
                "name": "random",
                "request": random_scenario,
            },
    ]

    def _build_parking_scenarios(self, request: dict) -> list[dict]:
        original_request_id = request["metadata"]["request_id"]

        current_scenario = copy.deepcopy(request)
        current_scenario["metadata"]["request_id"] = f"{original_request_id}-current"
        current_scenario["operations"] = []

        candidate_scenario = copy.deepcopy(request)
        candidate_scenario["metadata"]["request_id"] = f"{original_request_id}-candidate"

        nbiot_only_scenario = copy.deepcopy(request)
        nbiot_only_scenario["metadata"]["request_id"] = f"{original_request_id}-nbiot-only"
        nbiot_only_scenario["operations"] = []

        for component in nbiot_only_scenario["application"]["components"]:
            if component.get("properties", {}).get("component_type") == "parking-sensor":
                component["properties"]["mode"] = "NBIOT_PUSH"

        rng = random.Random(self.random_seed)

        random_scenario = copy.deepcopy(candidate_scenario)
        random_scenario["metadata"]["request_id"] = (
            candidate_scenario["metadata"]["request_id"].rsplit("-", 1)[0] + "-random"
        )

        random_operations = []

        for component in random_scenario["application"]["components"]:
            if component.get("properties", {}).get("component_type") != "parking-sensor":
                continue

            random_operations.append({
                "type": "sensor_mode_reconfiguration",
                "component_id": component["component_id"],
                "target_mode": rng.choice(["NBIOT_PUSH", "BLE_POLL"]),
            })

        random_scenario["operations"] = random_operations

        return [
            {
                "name": "current",
                "request": current_scenario,
            },
            {
                "name": "candidate",
                "request": candidate_scenario,
            },
            {
                "name": "nbiot-only",
                "request": nbiot_only_scenario,
            },
            {
                "name": "random",
                "request": random_scenario,
            },
        ]