import os
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET


def normalize_title(title):
    return ''.join(e for e in title.lower() if e.isalnum())

def fetch_wikipedia_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    content = {}

    for header in soup.find_all(['h2', 'h3']):
        title = normalize_title(header.get_text())
        content[title] = get_paragraphs(header)

    return content

def get_paragraphs(header):
    next_node = header.find_next_sibling()
    paragraphs = []
    while next_node and next_node.name not in ['h2', 'h3']:
        if next_node.name == 'p':
            paragraphs.append(next_node.get_text().strip())
        next_node = next_node.find_next_sibling()
    return '\n'.join(paragraphs)

def generate_xml_from_content(dtd_structure, content, root_element_name):
    root = ET.Element(root_element_name)
    for element in dtd_structure:
        normalized_element = normalize_title(element)
        for key in content.keys():
            if normalized_element in key:
                child = ET.SubElement(root, element)
                child.text = content[key]
                break
    return root
def read_dtd(file_path):
    elements = []
    with open(file_path, 'r') as file:
        for line in file:
            if '<!ELEMENT' in line and '#' in line:
                parts = line.split(' ')
                elements.append(normalize_title(parts[1]))
    return elements

def main():
    dtd_path = input("Enter the path to the DTD file: ")
    wiki_url = input("Enter the Wikipedia page URL: ")

    root_element_name = os.path.splitext(os.path.basename(dtd_path))[0]

    dtd_structure = read_dtd(dtd_path)
    wiki_content = fetch_wikipedia_content(wiki_url)
    xml_tree = generate_xml_from_content(dtd_structure, wiki_content, root_element_name)

    tree = ET.ElementTree(xml_tree)
    tree.write("output.xml", encoding='utf-8', xml_declaration=True)
    print("XML file generated successfully: output.xml")

if __name__ == "__main__":
    main()