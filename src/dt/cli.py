"""
Command-line entry point for local testing.
"""

import argparse
from dt.engine import DtEngine

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate simulation scenarios from an input JSON file and execute them."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input JSON file",
    )

    parser.add_argument(
        "--jar",
        required=True,
        help="Path to the simulator's jar file",
    )

    parser.add_argument(
    "--noise-csv",
    required=True,
    help="Path to the noise CSV file",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to save the result JSON files",
    )

    parser.add_argument(
        "--max-workers",
        required=True,
        type=int,
        help="Maximum number of concurrent worker processes",
    )

    parser.add_argument(
        "--timeout",
        required=True,
        type=int,
        help="Timeout (in seconds) for a single scenario execution",
    )

    parser.add_argument(
        "--keep-files",
        action="store_true",
        help="Keep simulator temporary result directory for debugging",
    )

    args = parser.parse_args()
    print("Starting Digital Twin execution..")
    engine = DtEngine(args.input, args.jar, args.output, args.noise_csv, args.max_workers, args.timeout, args.keep_files)
    engine.evaluate_file()

if __name__ == "__main__":
    main()