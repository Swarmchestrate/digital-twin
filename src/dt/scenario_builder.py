"""
Build simulation inputs for each scenario.
"""

import copy


class ScenarioBuilder:
    """Builds executable scenarios from a digital twin request."""

    def build(self, request: dict) -> list[dict]:
        application_type = request["metadata"]["application_type"]

        if application_type == "InnoRenew":
            return self._build_innorenew_scenarios(request)

        if application_type == "FuelicsParking":
            return self._build_parking_scenarios(request)

        raise ValueError(f"Unsupported application type: {application_type}")

    def _build_innorenew_scenarios(self, request: dict) -> list[dict]:
        original_request_id = request["metadata"]["request_id"]

        original_scenario = copy.deepcopy(request)
        original_scenario["metadata"]["request_id"] = f"{original_request_id}-1"

        baseline_scenario = copy.deepcopy(request)
        baseline_scenario["metadata"]["request_id"] = f"{original_request_id}-2"
        baseline_scenario["operations"] = []

        return [
            {
                "name": "candidate",
                "request": original_scenario,
            },
            {
                "name": "baseline",
                "request": baseline_scenario,
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
            properties = component.get("properties", {})

            if properties.get("component_type") == "parking-sensor":
                properties["mode"] = "NBIOT_PUSH"

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
        ]