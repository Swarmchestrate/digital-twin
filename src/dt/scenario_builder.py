"""
Build simulation inputs for each scenario.

"""

import copy

class ScenarioBuilder:
    """Builds one executable scenario per reconfiguration request."""

    def build(self, request: dict) -> list[dict]:
        original_request_id = request["metadata"]["request_id"]

        original_scenario = copy.deepcopy(request)
        original_scenario["metadata"]["request_id"] = f"{original_request_id}-1"

        baseline_scenario = copy.deepcopy(request)
        baseline_scenario["metadata"]["request_id"] = f"{original_request_id}-2"
        baseline_scenario["operations"] = []

        return [
            {
                "request": original_scenario,
            },
            {
                "request": baseline_scenario,
            },
        ]