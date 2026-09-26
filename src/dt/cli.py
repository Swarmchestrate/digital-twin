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
        "--data-csv",
        required=True,
        help="Path to the data CSV file",
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

    parser.add_argument(
        "--seed",
        type=int,
        default=1234567890,
        help="Random seed for generated random scenarios",
    )

    sort_group = parser.add_mutually_exclusive_group(required=True)

    sort_group.add_argument(
        "--sort-min",
        metavar="FIELD",
        help="Select the scenario with the smallest value of FIELD",
    )

    sort_group.add_argument(
        "--sort-max",
        metavar="FIELD",
        help="Select the scenario with the largest value of FIELD",
    )

    args = parser.parse_args()

    sort_field = args.sort_min or args.sort_max
    sort_direction = "min" if args.sort_min else "max"

    print("Starting Digital Twin execution..")
    engine = DtEngine(args.input, args.jar, args.output, args.data_csv, args.max_workers, args.timeout, 
                      args.keep_files, args.seed, sort_field, sort_direction)
    engine.evaluate_file()

if __name__ == "__main__":
    main()