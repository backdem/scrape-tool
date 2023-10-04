import requests
import argparse
import re
import os
from bs4 import BeautifulSoup


def get_soup(url):
    # Send an HTTP GET request to the URL
    response = requests.get(url)

    # Get the HTML content from the response
    html_content = response.text

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup


# Parse main page to get list of countries and links to evaluation reports
def get_complete_book_links():
    url = "https://freedomhouse.org/reports/publication-archives"
    domain = "http://freedomhouse.org"
    soup = get_soup(url)
    anchor_tags = soup.find_all('a')
    results = []
    for anchor in anchor_tags:
        href = anchor.get('href', None)
        if (href):
            parts = href.split('/')
            file_name = parts[-1].lower()
            if('complete_book' in file_name):
                if ("freedomhouse.org" in href):
                    results.append(href)
                else:
                    results.append(domain + href)
    return results


# Download a pdf evaluation report from a link and save it the output folder
def get_pdf(url, output_folder):
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        filename = url.split('/')[-1]
        path = os.path.join(output_folder, filename)
        with open(path, 'wb') as file:
            file.write(response.content)
            print(f"PDF file '{filename}' downloaded successfully.")


def main():
    parser = argparse.ArgumentParser(description='Download Freedomhouse archive complete book pdf files')
    parser.add_argument('--outputfolder', nargs='?', default='./',
                        help='output folder for csv files.')

    args = parser.parse_args()
    complete_book_links = get_complete_book_links()
    for link in complete_book_links:
        print(f"Downloading {link}")
        get_pdf(link, args.outputfolder)


main()
