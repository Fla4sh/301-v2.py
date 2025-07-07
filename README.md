# URL Redirect Inspector

A high-performance, concurrent URL redirect checker and analyzer designed for security researchers and web developers.

```
╔═══════════════════════════════════════════╗
║         URL Redirect Inspector            ║
║    Check and categorize URL redirects     ║
╚═══════════════════════════════════════════╝
```

## Introduction

URL Redirect Inspector is a powerful tool that analyzes HTTP redirects in bulk, helping you identify potential security risks, SEO issues, and broken redirects. It efficiently processes large lists of URLs concurrently, categorizing redirects based on their behavior and domain changes.

## Features

- **High-Performance Concurrency**: Utilizes Python's ThreadPoolExecutor for parallel URL processing
- **Intelligent Categorization**: Automatically classifies redirects into:
  - Cross-domain redirects (potential open redirects)
  - Same-domain redirects
  - Invalid or failed URLs
- **Detailed Reporting**: Generates clean, human-readable output files for each category
- **Progress Tracking**: Features a real-time progress bar using tqdm
- **Configurable Settings**: Customize thread count, redirect limits, timeouts, and output files
- **Modern HTTP Handling**: Uses requests.Session for efficient connection reuse
- **Robust Error Handling**: Gracefully handles network issues, malformed URLs, and timeout errors

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Fla4sh/301-v2.py.git
cd 301-v2.py
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Command

```bash
python 301-v2.py urls.txt
```

### Command-Line Arguments

| Argument | Shorthand | Description | Default |
|----------|-----------|-------------|----------|
| input_file | (none) | Path to input file containing URLs (one per line) | (Required) |
| --output | -o | Output file for new domain redirects | redirected_domains.txt |
| --same-domain-output | -s | Output file for same domain redirects | same_domain_redirects.txt |
| --invalid-output | -x | Output file for invalid or failed URLs | invalid_or_failed.txt |
| --valid-output | -v | Output file for cross-domain redirects (potential open redirects) | valid_redirects.txt |
| --threads | -t | Number of worker threads | 20 |
| --redirects | -r | Maximum number of redirects to follow | 10 |
| --timeout | (none) | Request timeout in seconds | 10 |

### Examples

1. Basic usage with default settings:
```bash
python 301-v2.py urls.txt
```

2. Process URLs with 50 threads and custom output files:
```bash
python 301-v2.py urls.txt -t 50 -o new_domains.txt -s same_domain.txt -x errors.txt
```

3. Increase timeout and redirect limit:
```bash
python 301-v2.py urls.txt --timeout 30 --redirects 15
```

### Input File Format

Create a text file with one URL per line:
```text
https://example.com
https://github.com
https://httpbin.org/redirect/2
```

### Output Format

1. Cross-domain redirects (valid_redirects.txt):
```text
FROM: https://t.co/example
  TO: https://example.com/page (1 redirects)
  Initial Domain: t.co
  Final Domain:   example.com
```

2. Same-domain redirects (same_domain_redirects.txt):
```text
FROM: https://example.com/old
  TO: https://example.com/new (1 redirects)
  Domain: example.com
```

3. Invalid or failed URLs (invalid_or_failed.txt):
```text
URL: https://invalid.example.com
  STATUS: REQUEST_ERROR
  REASON: Connection error
```

## Error Handling

The tool handles various error cases:
- Network connectivity issues
- DNS resolution failures
- Timeout errors
- Too many redirects
- Invalid URLs
- Malformed input files

## Security Considerations

- The tool identifies potential open redirects by tracking cross-domain redirects
- Same-domain redirects are tracked separately and not considered security risks
- Uses a modern User-Agent string to avoid being blocked
- Respects redirect limits to prevent infinite loops

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
