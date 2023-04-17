import argparse
import requests
from concurrent.futures import ThreadPoolExecutor
import tldextract


print('''\
                                                                                    
                                                                                    
██████╗  ██████╗  ██╗      ██╗   ██╗██████╗ 
╚════██╗██╔═████╗███║      ██║   ██║╚════██╗
 █████╔╝██║██╔██║╚██║█████╗██║   ██║ █████╔╝
 ╚═══██╗████╔╝██║ ██║╚════╝╚██╗ ██╔╝██╔═══╝ 
██████╔╝╚██████╔╝ ██║       ╚████╔╝ ███████╗
╚═════╝  ╚═════╝  ╚═╝        ╚═══╝  ╚══════╝
                     @github.com/Fla4sh
                     @twitter : fla4sh403\
''')


parser = argparse.ArgumentParser(description='Check redirects and extract final domains.')
parser.add_argument('input_file', metavar='INPUT_FILE', type=str, help='the path to the input file')
parser.add_argument('-o', '--output', type=str, default='valid_domains.txt', help='the path to the output file (default: valid_domains.txt)')
parser.add_argument('-t', '--threads', type=int, default=10, help='the number of worker threads to use (default: 10)')
parser.add_argument('-r', '--redirects', type=int, default=5, help='the maximum number of redirects to follow (default: 5)')
parser.add_argument('-x', '--invalid', type=str, default='invalid_domains.txt', help='the path to the invalid output file (default: invalid_domains.txt)')
args = parser.parse_args()

with open(args.input_file, 'r', encoding='utf-8') as file:
    urls = [line.strip() for line in file if line.strip()]

def check_redirect(url):
    try:
        with requests.Session() as session:
            response = session.get(url, allow_redirects=True, timeout=5)
            redirects = response.history[:args.redirects]
            num_redirects = len(redirects)

        if redirects:
            final_url = response.url
            initial_domain = tldextract.extract(url).registered_domain
            final_domain = tldextract.extract(final_url).registered_domain
            if final_url.startswith(('http', 'https')) and final_domain != initial_domain:
                if tldextract.extract(final_url).suffix is not None:
                    print(f"The URL {url} redirected {num_redirects} times to {final_url}")
                    with open(args.output, "a+") as file:
                        file.write(f"{url} redirected {num_redirects} times to {final_url}\n")
                        file.write(f"Initial domain: {initial_domain}\n")
                        file.write(f"Final domain: {final_domain}\n\n")
                else:
                    print(f"The URL {url} redirected to an invalid domain")
                    with open(args.invalid, "a+") as file:
                        file.write(f"{url} redirected {num_redirects} times to {final_url}\n")
                        file.write(f"Initial domain: {initial_domain}\n")
                        file.write(f"Final domain: {final_domain}\n\n")
            else:
                print(f"The URL {url} redirected {num_redirects} times to the same domain ({initial_domain})")
        else:
            print(f"The URL {url} did not redirect")
    except Exception as e:
        print(f"Error occurred while checking URL: {url}")
        print(e)

with ThreadPoolExecutor(max_workers=args.threads) as executor:
    results = executor.map(check_redirect, urls)
