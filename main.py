import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote

def download_image(image_url, folder):
    try:
        response = requests.get(image_url)
        response.raise_for_status()

        parsed_url = urlparse(image_url)
        image_filename = os.path.basename(parsed_url.path)

        image_path = os.path.join(folder, image_filename)
        with open(image_path, 'wb') as file:
            file.write(response.content)

        return image_filename
    except requests.RequestException as e:
        print(f"An error occurred while downloading the image: {e}")
        return None

def save_wikipedia_content_with_images(url, folder=None):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        if not folder:
            title = soup.find('h1', {'id': 'firstHeading'}).text
            folder = os.path.join('wikipedia_content', unquote(title))
        os.makedirs(folder, exist_ok=True)

        content = soup.find('div', {'id': 'mw-content-text'})
        if content:
            for a_tag in content.find_all('a', href=True):
                href = a_tag['href']
                if href.startswith('/wiki/'):
                    a_tag['href'] = 'https://en.wikipedia.org' + href

            for img_tag in content.find_all('img'):
                img_url = urljoin(url, img_tag.get('src'))
                downloaded_img = download_image(img_url, folder)
                if downloaded_img:
                    img_tag['src'] = downloaded_img
                    if 'srcset' in img_tag.attrs:
                        del img_tag.attrs['srcset']

            with open(os.path.join(folder, 'content.html'), 'w', encoding='utf-8') as file:
                file.write(str(content))
            print(f"Content saved in '{folder}' folder.")
        else:
            print("Could not find the main content area of the page.")

    except requests.RequestException as e:
        print(f"An error occurred: {e}")

def main():
    url = input("Enter a Wikipedia URL: ")
    save_wikipedia_content_with_images(url)

if __name__ == "__main__":
    main()
