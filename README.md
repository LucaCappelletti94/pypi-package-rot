# PyPI package rot

[![PyPI](https://badge.fury.io/py/pypi-package-rot.svg)](https://badge.fury.io/py/pypi-package-rot)
[![Downloads](https://pepy.tech/badge/pypi-package-rot)](https://pepy.tech/badge/pypi-package-rot)
![Scraped packages](https://img.shields.io/badge/Scraped%20packages-293972%20of%20582938-blue)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/LucaCappelletti94/pypi-package-rot/blob/master/LICENSE)
[![CI](https://github.com/LucaCappelletti94/pypi-package-rot/actions/workflows/python.yml/badge.svg)](https://github.com/LucaCappelletti94/pypi-package-rot/actions)

Investigating the state of package rot on PyPI.

## Introduction

The objective of this dataset is to provide a screenshot of the state of PyPI packages, so to facilitate investigations on the state of the Python ecosystem. While its first intended goal is to facilitate the identification of package rot, it can be used for other purposes as well.

**At this time, we are building the dataset still and we are about 240k packages of 600k. We expect to have the dataset ready by the end of 2024.**

## Installing

As usual, you can install the package with pip:

```bash
pip install pypi-package-rot
```

## CLI

The package provides the following CLI utilities to allow you to replicate the dataset. Do keep in mind that this operation will take a long time, as it involves scraping informations from websites that allow about 1 request per second.

### Perpetual scraper

This command will scrape PyPI packages and store their metadata in the cache directory. Since the API RATE allows only about 1 request per second, it will take a long time (currently about 8 days) to retrieve all the packages. This utility will run in perpetuity, running and retrieving new packages continuously.

The email is needed to build an adequate user-agent string for the requests, so that PyPI can contact you if you are abusing the API.

```bash
pypi_package_rot perpetual_scraper --email "your@email.com"
```

### Build the dataset

After having downloaded for a while the metadata of the packages, you can build the summarized anonymized dataset with the following command:

```bash
pypi_package_rot perpetual_builder --verbose --output "pypi.rot.v1.summarized.csv"  --email "your@email.com"
```

Alternatively, to include all informations, you can use the following command:

```bash
pypi_package_rot perpetual_builder --verbose --full --output "pypi.rot.v1.full.json"  --email "your@email.com"
```

Part of the procedure included testing whether the URLs in the metadata are still valid. This is done by sending a HEAD request to the URL and checking the status code. Such operations may take a long time (about one month at the time of writing). As per the previous command, the email is needed to build an adequate user-agent string for the requests, so that websites can contact you if you are abusing their services.

## Contributing

Do you have some ideas to improve this dataset or associated analysis? Feel free to open an issue or a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
