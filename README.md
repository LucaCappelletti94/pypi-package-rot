# PyPI package rot

Investigating the state of package rot on PyPI

## CLI

### Perpetual scraper

This command will scrape PyPI packages and store their metadata in the cache directory. Since the API RATE allows only about 1 request per second, it will take a long time (currently about 8 days) to retrieve all the packages. This utility will run in perpetuity, running and retrieving new packages continuously.

The email is needed to build an adequate user-agent string for the requests, so that PyPI can contact you if you are abusing the API.

```bash
pypi_package_rot perpetual_scraper --email "your@email.com"
```
