# 301-v2.py

This script is designed to check whether a list of URLs redirect to a different domain or stay on the same domain. The script uses the Python requests module to check the status of the URLs and the tldextract module to extract the registered domain names from the URLs.

# Getting started

To use this script, you must have Python 3 installed on your machine. You can download Python from the official website [here](https://www.python.org/downloads/).

To install the required dependencies, you can run the following command:

```
pip install requests tldextract
```

# Usage

To use the script, run the following command in your terminal or command prompt:
```
python3 script.py input_file.txt -o output_file.txt -t 10 -r 5 -x invalid_domains.txt
```

# Results

The 'valid_domains.txt' file contains a list of all URLs that redirected to a different domain. For each URL, the file contains the following information:

- The URL that was checked
- The number of redirects that occurred
- The initial domain of the URL
- The final domain of the URL

# Limitations

- The script only checks the first (5) [you can edit it] redirects of each URL.
- The script does not follow redirects that use the meta tag or JavaScript.
- The script may produce inaccurate results for URLs that redirect to a subdomain of the same domain.

# Contributing

If you find any issues with this script or would like to suggest a feature, please create an issue or pull request on GitHub.
