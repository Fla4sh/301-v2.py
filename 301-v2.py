import requests
from concurrent.futures import ThreadPoolExecutor
import tldextract

print('''\
                                                                                    
                                                                                    
██████╗  ██████╗  ██╗
╚════██╗██╔═████╗███║
 █████╔╝██║██╔██║╚██║
 ╚═══██╗████╔╝██║ ██║
██████╔╝╚██████╔╝ ██║
╚═════╝  ╚═════╝  ╚═╝
                     @github.com/Fla4sh
                     @twitter : fla4sh403\
''')

output_file = "valid_domains.txt"
not_same_domain_file = "not_same_domain.txt"

file_path = input("Please enter your file: ")
with open(file_path, 'r', encoding='utf-8') as file:
    urls = [line.strip() for line in file if line.strip()]

def check_redirect(url):
    try:
        with requests.Session() as session:
            response = session.get(url, allow_redirects=True, timeout=5)
            redirects = response.history[:5]
            num_redirects = len(redirects)

        if redirects:
            final_url = response.url
            initial_domain = tldextract.extract(url).registered_domain
            final_domain = tldextract.extract(final_url).registered_domain
            if final_url.startswith(('http', 'https')) and final_domain != initial_domain:
                if tldextract.extract(final_url).suffix is not None:
                    print(f"The URL {url} redirected {num_redirects} times to {final_url}")
                    with open(output_file, "a+") as file:
                        file.write(f"{url} redirected {num_redirects} times to {final_url}\n")
                        file.write(f"Initial domain: {initial_domain}\n")
                        file.write(f"Final domain: {final_domain}\n\n")
                else:
                    print(f"The URL {url} redirected to an invalid domain")
                    with open(not_same_domain_file, "a+") as file:
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

with ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(check_redirect, urls)
