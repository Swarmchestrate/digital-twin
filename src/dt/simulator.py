"""
Runs scenarios as subprocesses and writes aggregated results to a JSON file.
"""

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import time

class SimulatorRunner:

    def __init__(self, result_dir: str | Path, jar_path: str | Path, max_workers: int = 1, timeout: int = 60) -> None:
        self.result_dir = Path(result_dir)
        self.jar_path = Path(jar_path)
        self.max_workers = max_workers
        self.timeout = timeout

    def run_scenarios(self, scenarios: list[dict]) -> dict:
        self.result_dir.mkdir(parents=True, exist_ok=True)

        results: list[dict] = []

        # Output file for aggregated results
        result_file = self.result_dir / "results.json"

        # Thread pool manages parallel execution of scenarios
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(
                    self._run_single_scenario,
                    scenario["scenario_id"],
                    scenario["request"],
                )
                for scenario in scenarios
            ]

            # Process results as soon as they complete
            for future in as_completed(futures):
                result = future.result()
                results.append(result)

            self._write_result_file(result_file, results)

        return {
            "scenario_count": len(results),
            "scenarios": results,
        }

    def _run_single_scenario(self, scenario_id: str, request: dict) -> dict:
        # Save input for debugging 
        input_path = self.result_dir / f"{scenario_id}_input.json"

        with input_path.open("w", encoding="utf-8") as f:
            json.dump(request, f, indent=2, ensure_ascii=False)

        # For testing with dummy worker
        # worker_path = Path(__file__).with_name("dummy_worker.py")
        # cmd = [sys.executable, str(worker_path)]
        # completed = subprocess.run(
        #    cmd,
        #    input=json.dumps(request),   # send request via stdin
        #    capture_output=True,         # capture stdout/stderr
        #    text=True,                  # use strings instead of bytes
        #)

        start = time.perf_counter()
        print(f"[{scenario_id}] started..")

        proc = subprocess.Popen(
            [
                "java",
                "-cp",
                str(self.jar_path),
                "hu.u_szeged.inf.fog.simulator.agent.demo.DigitalTwinDemo",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            )
        
        try:
            stdout, stderr = proc.communicate(
            input=json.dumps(request, ensure_ascii=False),
            timeout=self.timeout
            )
            end = time.perf_counter()
            print(f"[{scenario_id}] completed successfully in {end - start:.2f}s")

        except subprocess.TimeoutExpired:
            end = time.perf_counter()
            print(f"[{scenario_id}] timeout after {self.timeout}s")

            proc.kill() # TODO: verify on Linux, as process termination is unreliable on Windows
           
            return {
                "scenario_id": scenario_id,
                 "status": "error",
                "stdout": "",
                "stderr": f"scenario execution timed out after {self.timeout} seconds",
            }

        # Handle execution error
        if proc.returncode != 0:
            return {
                "scenario_id": scenario_id,
                "status": "error",
                "stdout": stdout,
                "stderr": stderr,
            }

        # Parse worker output (expected to be JSON)
        try:
            result = json.loads(stdout)
        except json.JSONDecodeError:
            return {
                "scenario_id": scenario_id,
                "status": "error",
                "stdout": stdout,
                "stderr": "invalid JSON from worker",
            }

        # Successful execution
        return {
            "scenario_id": scenario_id,
            "status": "ok",
            "result": result,
        }

    def _write_result_file(self, result_file: Path, results: list[dict]) -> None:
        data = {
            "scenario_count": len(results),
            "scenarios": results,
        }

        with result_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)