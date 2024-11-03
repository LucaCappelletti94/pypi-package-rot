"""CLI for the PyPI package rot."""

from argparse import Namespace, ArgumentParser
from typing import Any, Dict, List
from time import time
from tqdm.auto import tqdm
import compress_json
import pandas as pd
from rich.console import Console
from rich.table import Table
from humanize import precisedelta
from pypi_package_rot.api import (
    retrieve_all_package_names,
    Project,
    get_available_projects,
    get_number_of_available_projects,
)


from pypi_package_rot.__version__ import __version__


def perpetual_scraper(namespace: Namespace):
    """Mines features from PyPI packages."""
    user_agent = f"pypi_package_rot/{__version__} ({namespace.email})"

    while True:
        package_names = retrieve_all_package_names(user_agent)
        for package_name in tqdm(
            package_names,
            desc="Mining features",
            unit="package",
            leave=False,
            dynamic_ncols=True,
        ):
            _ = Project.from_project_name(package_name, user_agent)


def perpetual_scraper_parser(parser: ArgumentParser):
    """Add arguments to the perpetual feature miner parser."""
    parser.add_argument(
        "--email",
        type=str,
        required=True,
        help="Email to be included in the user agent.",
    )
    parser.set_defaults(func=perpetual_scraper)


def perpetual_builder(namespace: Namespace):
    """Builds a dataset from the available projects."""
    user_agent = f"pypi_package_rot/{__version__} ({namespace.email})"
    while True:
        last_outputted: float = time()
        project_features: List[Dict[str, Any]] = []
        operation_start_time: float = time()
        time_remaining: float = 0
        number_of_cached_projects: int = 0
        metadata: Dict[str, Any] = {
            "Projects to parse": get_number_of_available_projects(),
            "Parsed projects": 0,
            "Dead projects": 0,
            "Seemingly dead projects": 0,
            "Yankable dead projects": 0,
        }

        # We display the table using rich
        console = Console()
        last_printed = time()

        for project in get_available_projects():
            start = time()
            if not namespace.full:
                project_features.append(project.to_anonymized_dict(user_agent))
            else:
                project_features.append(project.to_dict(user_agent))
            metadata["Parsed projects"] += 1
            if project.is_dead():
                metadata["Dead projects"] += 1
            if project.seems_dead(user_agent):
                metadata["Seemingly dead projects"] += 1
            if project.should_be_terminated(user_agent):
                metadata["Yankable dead projects"] += 1

            time_required = time() - start

            if time_required < 0.1:
                number_of_cached_projects += 1

            time_elapsed = time() - operation_start_time
            if metadata["Parsed projects"] - number_of_cached_projects > 0:
                time_remaining = (
                    time_elapsed
                    / (metadata["Parsed projects"] - number_of_cached_projects)
                    * (metadata["Projects to parse"] - metadata["Parsed projects"])
                )

            metadata["Time elapsed"] = precisedelta(int(time_elapsed))
            metadata["Time remaining"] = precisedelta(int(time_remaining))

            if namespace.verbose and time() - last_printed > 1:
                # We display the table using rich
                last_printed = time()
                table = Table(title="Project metadata")
                table.add_column("Metadata")
                table.add_column("Value")
                for key, value in metadata.items():
                    table.add_row(key, str(value))

                console.clear()
                console.print(table)

            if time() - last_outputted > 60:
                if namespace.output.endswith(".json"):
                    compress_json.dump(project_features, namespace.output)
                elif namespace.output.endswith(".csv"):
                    df = pd.DataFrame(project_features)
                    df.to_csv(f"{namespace.output}.partial.csv", index=False)
                else:
                    raise ValueError("Output file must be either CSV or JSON.")
                last_outputted = time()

        df.to_csv(namespace.output, index=False)


def perpetual_builder_parser(parser: ArgumentParser):
    """Add arguments to the dataset builder parser."""
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Path to the output CSV or JSON file.",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Whether to output the full dataset or just the partial one.",
    )
    parser.add_argument(
        "--email",
        type=str,
        required=True,
        help="Email to be included in the user agent.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Prints loading progress.",
    )
    parser.set_defaults(func=perpetual_builder)


def main():
    """CLI for the PyPI package rot."""
    parser = ArgumentParser(description="CLI for the PyPI package rot.")

    subparsers = parser.add_subparsers(dest="subcommand")
    perpetual_scraper_parser(subparsers.add_parser("perpetual_scraper"))
    perpetual_builder_parser(subparsers.add_parser("perpetual_builder"))

    args = parser.parse_args()

    args.func(args)
