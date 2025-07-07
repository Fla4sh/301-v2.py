#!/usr/bin/env python3

"""URL Redirect Inspector - A concurrent URL redirect checker.

This script analyzes HTTP redirects for a list of URLs, categorizing them based on
their redirect behavior and domain changes. It uses thread pools for concurrent processing
and provides detailed output in human-readable format.

Author: Fla4sh
Version: 2.0.0
"""

import argparse
import concurrent.futures
import logging
import requests
import tldextract
from tqdm import tqdm
from typing import Dict, List, Optional, Tuple, Any

# ASCII Art Banner
BANNER = """
╔═══════════════════════════════════════════╗
║         URL Redirect Inspector            ║
║    Check and categorize URL redirects     ║
╚═══════════════════════════════════════════╝
"""

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class RedirectInspector:
    """A class that inspects URL redirects and categorizes them based on domain changes.
    
    This class handles the core functionality of checking URLs for redirects, analyzing
    their behavior, and categorizing the results. It maintains a session for efficient
    connection reuse and provides detailed information about redirect chains.
    """
    
    def __init__(self, max_redirects: int = 10, timeout: int = 10):
        """Initialize the RedirectInspector with custom settings.
        
        Args:
            max_redirects (int): Maximum number of redirects to follow before giving up
            timeout (int): Number of seconds to wait for a response before timing out
        """
        self.session = requests.Session()
        # Use a modern User-Agent to avoid being blocked by servers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.max_redirects = max_redirects
        self.timeout = timeout

    def get_domain(self, url: str) -> str:
        """Extract the top domain under public suffix from a URL.
        
        This method uses tldextract to reliably parse domains from URLs, handling
        various edge cases like multi-level TLDs (e.g., co.uk) correctly.
        
        Args:
            url (str): The URL to extract the domain from
            
        Returns:
            str: The top domain under the public suffix (e.g., 'example' from 'example.com')
        """
        return tldextract.extract(url).top_domain_under_public_suffix

    def check_url(self, url: str) -> Dict[str, Any]:
        """Check a single URL for redirects and categorize the result.
        
        This method follows redirects for a given URL and categorizes the result based on
        whether the redirect chain stays within the same domain or crosses to a new domain.
        It also handles various error cases gracefully.
        
        Args:
            url (str): The URL to check for redirects
            
        Returns:
            Dict[str, Any]: A dictionary containing the redirect analysis results with keys:
                - category: 'no_redirect', 'same_domain', 'new_domain', or 'invalid'
                - url: The original URL
                - final_url: The destination URL (for successful redirects)
                - redirect_count: Number of redirects followed
                - domain/initial_domain/final_domain: Domain information
                - error/reason: Error details (for invalid results)
        """

        try:
            initial_domain = self.get_domain(url)
            response = self.session.get(
                url,
                allow_redirects=True,
                timeout=self.timeout
            )
            final_url = response.url
            final_domain = self.get_domain(final_url)
            redirect_count = len(response.history)

            if redirect_count == 0:
                return {
                    'category': 'no_redirect',
                    'url': url
                }
            elif initial_domain == final_domain:
                return {
                    'category': 'same_domain',
                    'initial_url': url,
                    'final_url': final_url,
                    'redirect_count': redirect_count,
                    'domain': initial_domain
                }
            else:
                return {
                    'category': 'new_domain',
                    'initial_url': url,
                    'final_url': final_url,
                    'redirect_count': redirect_count,
                    'initial_domain': initial_domain,
                    'final_domain': final_domain
                }

        except requests.exceptions.TooManyRedirects:
            return {
                'category': 'invalid',
                'url': url,
                'error': 'TOO_MANY_REDIRECTS',
                'reason': 'Exceeded maximum number of redirects'
            }
        except requests.exceptions.RequestException as e:
            return {
                'category': 'invalid',
                'url': url,
                'error': 'REQUEST_ERROR',
                'reason': str(e)
            }

def write_results(results: List[Dict[str, Any]], output_file: str, same_domain_file: str, invalid_file: str, valid_file: str) -> None:
    """Write categorized results to their respective output files.
    
    This function takes the analyzed URL results and writes them to separate files based on
    their categories. The output is formatted in a human-readable way with clear indentation
    and descriptive labels.
    
    Args:
        results (List[Dict[str, Any]]): List of URL analysis results from RedirectInspector
        output_file (str): Path to file for new domain redirects
        same_domain_file (str): Path to file for same-domain redirects
        invalid_file (str): Path to file for invalid or failed URLs
        valid_file (str): Path to file for cross-domain redirects (potential open redirects)
    
    The function creates four different output files:
    1. New domain redirects: Shows URLs that redirect to a different domain
    2. Same domain redirects: Shows URLs that redirect within the same domain
    3. Invalid/failed URLs: Shows URLs that couldn't be processed
    4. Valid redirects: Shows potential open redirects (cross-domain)
    """
    new_domain_results = [r for r in results if r['category'] == 'new_domain']
    same_domain_results = [r for r in results if r['category'] == 'same_domain']
    invalid_results = [r for r in results if r['category'] == 'invalid']
    valid_results = [r for r in results if r['category'] == 'new_domain']

    if new_domain_results:
        with open(output_file, 'w') as f:
            for result in new_domain_results:
                f.write(f"FROM: {result['initial_url']}\n")
                f.write(f"  TO: {result['final_url']} ({result['redirect_count']} redirects)\n")
                f.write(f"  Initial Domain: {result['initial_domain']}\n")
                f.write(f"  Final Domain:   {result['final_domain']}\n\n")

    if same_domain_results:
        with open(same_domain_file, 'w') as f:
            for result in same_domain_results:
                f.write(f"FROM: {result['initial_url']}\n")
                f.write(f"  TO: {result['final_url']} ({result['redirect_count']} redirects)\n")
                f.write(f"  Domain: {result['domain']}\n\n")

    if invalid_results:
        with open(invalid_file, 'w') as f:
            for result in invalid_results:
                f.write(f"URL: {result['url']}\n")
                f.write(f"  STATUS: {result['error']}\n")
                f.write(f"  REASON: {result['reason']}\n\n")

    if valid_results:
        with open(valid_file, 'w') as f:
            for result in valid_results:
                f.write(f"FROM: {result['initial_url']}\n")
                f.write(f"  TO: {result['final_url']} ({result['redirect_count']} redirects)\n")
                f.write(f"  Initial Domain: {result['initial_domain']}\n")
                f.write(f"  Final Domain:   {result['final_domain']}\n\n")

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.
    
    This function sets up the command-line interface for the URL Redirect Inspector,
    defining all available options and their default values. It uses argparse to
    handle argument parsing and provide helpful usage information.
    
    Returns:
        argparse.Namespace: An object containing all parsed command-line arguments
            with the following attributes:
            - input_file: Path to the input file containing URLs
            - output: Path for new domain redirects output
            - same_domain_output: Path for same-domain redirects output
            - invalid_output: Path for invalid URLs output
            - valid_output: Path for cross-domain redirects output
            - threads: Number of worker threads
            - redirects: Maximum number of redirects to follow
            - timeout: Request timeout in seconds
    """
    parser = argparse.ArgumentParser(
        description='Check and categorize URL redirects concurrently.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('input_file', help='Path to input file containing URLs (one per line)')
    parser.add_argument('-o', '--output', default='redirected_domains.txt',
                        help='Output file for new domain redirects')
    parser.add_argument('-s', '--same-domain-output', default='same_domain_redirects.txt',
                        help='Output file for same domain redirects')
    parser.add_argument('-x', '--invalid-output', default='invalid_or_failed.txt',
                        help='Output file for invalid or failed URLs')
    parser.add_argument('-v', '--valid-output', default='valid_redirects.txt',
                        help='Output file for cross-domain redirects (potential open redirects)')
    parser.add_argument('-t', '--threads', type=int, default=20,
                        help='Number of worker threads')
    parser.add_argument('-r', '--redirects', type=int, default=10,
                        help='Maximum number of redirects to follow')
    parser.add_argument('--timeout', type=int, default=10,
                        help='Request timeout in seconds')
    return parser.parse_args()

def main() -> None:
    """Main function to run the redirect checker.
    
    This function orchestrates the entire URL redirect checking process:
    1. Displays the program banner
    2. Parses command-line arguments
    3. Reads URLs from the input file
    4. Creates a thread pool for concurrent processing
    5. Processes URLs and collects results
    6. Writes categorized results to output files
    7. Displays a progress bar during processing
    
    The function handles file I/O errors and provides informative logging
    throughout the process.
    """

    print(BANNER)
    args = parse_arguments()

    try:
        with open(args.input_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logging.error(f"Input file not found: {args.input_file}")
        return

    logging.info(f"Found {len(urls)} URLs to process")
    inspector = RedirectInspector(max_redirects=args.redirects, timeout=args.timeout)

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = [executor.submit(inspector.check_url, url) for url in urls]
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(urls), desc="Processing URLs"):
            results.append(future.result())

    write_results(results, args.output, args.same_domain_output, args.invalid_output, args.valid_output)
    logging.info(f"Results written to:\n")
    logging.info(f"  New domain redirects: {args.output}")
    logging.info(f"  Same domain redirects: {args.same_domain_output}")
    logging.info(f"  Invalid/failed URLs: {args.invalid_output}")
    logging.info(f"  Cross-domain redirects (potential open redirects): {args.valid_output}")

if __name__ == "__main__":
    main()
