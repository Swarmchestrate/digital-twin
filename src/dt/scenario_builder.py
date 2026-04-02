"""
Build simulation inputs for each scenario.

"""

import copy

class ScenarioBuilder:
    """Builds one executable scenario per reconfiguration request."""

    def build(self, request: dict) -> list[dict]:
        scenarios: list[dict] = []
        reconfig_requests = request.get("reconfiguration_requests", [])

        print(f"Preparing {len(reconfig_requests)} scenarios..")

        for index, item in enumerate(reconfig_requests):
            scenario_id = item.get("scenario_id", f"scenario_{index}")

            scenario_request = copy.deepcopy(request)

            # Replace only the scenario-specific part
            scenario_request.pop("reconfiguration_requests", None)
            scenario_request["scenario_id"] = scenario_id
            scenario_request["actions"] = item.get("actions", [])

            scenarios.append(
                {
                    "scenario_id": scenario_id,
                    "request": scenario_request,
                }
            )

        return scenarios