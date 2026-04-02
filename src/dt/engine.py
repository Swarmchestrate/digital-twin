"""
Main entry point for the digital twin logic.
"""

import json
import os
from pathlib import Path
from dt.scenario_builder import ScenarioBuilder
from dt.simulator import SimulatorRunner

class DtEngine:

    def __init__(self, input_path: str | Path, jar: str | Path, output_path: str | Path, max_workers: int, timeout: int) -> None:
        if max_workers < 1 or max_workers > os.cpu_count():
            max_workers = max(1, min(max_workers, os.cpu_count()))
            
        self.scenario_builder = ScenarioBuilder()
        self.simulator_runner = SimulatorRunner(output_path, jar, max_workers, timeout)
        self.input_path = input_path

    def evaluate(self, request: dict) -> dict:
        """
        Build executable scenarios from the input request
        and pass them to the simulator layer.
        """
        
        print("Validating the input JSON request..")
        self.validate_request(request)

        print("Building scenarios...")
        scenarios = self.scenario_builder.build(request)
        return self.simulator_runner.run_scenarios(scenarios)

    def evaluate_file(self) -> dict:
        """
        Load the input request from a JSON file.
        """
        with Path(self.input_path).open("r", encoding="utf-8") as f:
            request = json.load(f)

        return self.evaluate(request)
    
    def validate_request(self, request: dict) -> None:
        """
        Placeholder for input validation.
        Later this will validate the request structure and required fields.
        """
    
    pass