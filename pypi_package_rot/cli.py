"""CLI for the PyPI package rot."""

from argparse import Namespace, ArgumentParser
from tqdm.auto import tqdm
from pypi_package_rot.api import retrieve_all_package_names, Project
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


def main():
    """CLI for the PyPI package rot."""
    parser = ArgumentParser(description="CLI for the PyPI package rot.")

    subparsers = parser.add_subparsers(dest="subcommand")
    perpetual_scraper_parser(subparsers.add_parser("perpetual_scraper"))

    args = parser.parse_args()

    args.func(args)
