"""
Runs scenarios as subprocesses and writes aggregated results to a JSON file.
"""

import json
import subprocess
#import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import time

class SimulatorRunner:

    def __init__(self, result_dir: str | Path, jar_path: str | Path, noise_csv_path: str | Path, max_workers: int = 1, timeout: int = 60) -> None:
        self.result_dir = Path(result_dir)
        self.jar_path = Path(jar_path)
        self.noise_csv_path = Path(noise_csv_path)
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

    def _run_single_scenario(self, request: dict) -> dict:
        request_id = request["metadata"]["request_id"]

        # Save input for debugging
        input_path = self.result_dir / f"{request_id}_input.json"

        with input_path.open("w", encoding="utf-8") as f:
            json.dump(request, f, indent=2, ensure_ascii=False)

        start = time.perf_counter()
        print(f"[{request_id}] started..")

        proc = subprocess.Popen(
            [
                "java",
                "-cp",
                str(self.jar_path),
                "hu.u_szeged.inf.fog.simulator.agent.demo.DigitalTwinDemo",
                str(input_path),
                str(self.noise_csv_path),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        result = {
            "request_id": request_id,
            "status": "ok",
            "returncode": None,
            "stdout": "",
            "stderr": "",
        }

        try:
            stdout, stderr = proc.communicate(timeout=self.timeout)

            result["returncode"] = proc.returncode
            result["stdout"] = stdout
            result["stderr"] = stderr

            end = time.perf_counter()
            print(f"[{request_id}] finished in {end - start:.2f}s")

            if proc.returncode != 0:
                result["status"] = "error"

        except subprocess.TimeoutExpired:
            end = time.perf_counter()
            print(f"[{request_id}] timeout after {self.timeout}s")

            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                proc.kill()

            result["status"] = "timeout"
            result["stderr"] = (
                f"scenario execution timed out after {self.timeout} seconds"
            )

        return result

    def _write_result_file(self, result_file: Path, results: list[dict]) -> None:
        data = {
            "scenario_count": len(results),
            "scenarios": results,
        }

        with result_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)