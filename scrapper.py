import requests
from bs4 import BeautifulSoup

def scrape_website(url):
    # Send a GET request to the website
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Example: Extract all paragraph texts
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            print(p.get_text())
        
        # Example: Extract all links
        links = soup.find_all('a', href=True)
        for link in links:
            print(f"Text: {link.get_text()} - URL: {link['href']}")
    else:
        print(f"Failed to retrieve the website. Status code: {response.status_code}")

# Example usage
url = 'https://jobs.careers.microsoft.com/global/en/job/1704672/Software-Engineer-II'  # Replace with the target website URL
scrape_website(url)
