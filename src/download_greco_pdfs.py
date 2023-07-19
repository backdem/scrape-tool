import requests
import argparse
import re
import os
from bs4 import BeautifulSoup

# Specify the URL of the web page you want to fetch
countries = ['albania', 'andorra', 'armenia', 'austria', 'azerbaijan', 'belarus', 'belgium', 'bosnia-and-herzegovina', 'bulgaria', 'croatia', 'cyprus', 'czech-republic', 'denmark', 'estonia', 'finland', 'france', 'georgia', 'germany', 'greece', 'hungary', 'iceland', 'ireland', 'italy', 'latvia', 'liechtenstein', 'lithuania', 'luxembourg', 'malta', 'republic-of-moldova', 'monaco', 'montenegro', 'netherlands', 'north macedonia', 'norway', 'poland', 'portugal', 'romania', 'russian-federation', 'san-marino', 'serbia', 'slovakia', 'slovenia', 'spain', 'sweden', 'switzerland', 'turkiye', 'ukraine', 'united-kingdom']


def get_soup(url):
    # Send an HTTP GET request to the URL
    response = requests.get(url)

    # Get the HTML content from the response
    html_content = response.text

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup


# Parse main page to get list of countries and links to evaluation reports
def get_country_eval_links():
    url = 'https://www.coe.int/en/web/greco/evaluations#{%2222359946%22:[]}'
    head_url = 'https://www.coe.int/en'
    soup = get_soup(url)
    anchor_tags = soup.find_all('a')
    results = []
    for anchor in anchor_tags:
        href = anchor.get('href', None)
        if (href):
            parts = href.split('/')
            if ('evaluations' in parts):
                country = parts[-1]
                if (country in countries):
                    full_href = head_url + href
                    results.append((country, full_href))
    return results


# Download a pdf evaluation report from a link and save it the output folder
def get_pdf(url, country, output_folder):
    response = requests.get(url)

    country = country.replace(" ", "-")

    # Check if the request was successful
    if response.status_code == 200:
        content_disposition = response.headers.get('Content-Disposition')

        if content_disposition:
            # Extract the filename using regex
            filename = re.findall('filename=(.+)', content_disposition)
            if filename:
                # Remove leading and trailing double quotes
                filename = country + "_" + filename[0].strip('"')
                # Save the PDF content to a file
                path = os.path.join(output_folder, filename)
                with open(path, 'wb') as file:
                    file.write(response.content)
                    print(f"PDF file '{filename}' downloaded successfully.")
            else:
                print(f'Filename not found in Content-Disposition header for url {url}')
                return
    else:
        print(f"Failed to download PDF. Status code: {response.status_code}")


def main():
    parser = argparse.ArgumentParser(description='Download GRECO pdf files')
    parser.add_argument('--outputfolder', nargs='?', default='./',
                        help='output folder for csv files.')

    args = parser.parse_args()
    # Start downloading the evaluation pdf files
    country_links = get_country_eval_links()

    for (country, url) in country_links:
        print(country)
        print('------------')
        soup = get_soup(url)
        # Find all anchor tags using the 'a' tag selector
        anchor_tags = soup.find_all('a')

        # Iterate over the anchor tags and extract the href attribute
        for anchor in anchor_tags:
            lang = anchor.text.strip().lower()
            if (lang == 'english' or lang == 'eng'):
                link = anchor['href']
                if (link and link != '#'):
                    print(f'Acessing link {link}')
                    get_pdf(link, country, args.outputfolder)
        print()


main()
