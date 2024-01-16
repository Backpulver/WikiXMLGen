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

    current_h2 = None
    for header in soup.find_all(['h2', 'h3']):
        title = normalize_title(header.get_text())

        if header.name == 'h2':
            current_h2 = title
            content[current_h2] = {'text': get_paragraphs(header), 'subelements': {}}
        elif header.name == 'h3' and current_h2 is not None:
            content[current_h2]['subelements'][title] = get_paragraphs(header)

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

    for h2_header, h2_content in content.items():
        parent_element = ET.SubElement(root, normalize_title(h2_header))
        if h2_content['text']:
            parent_element.text = h2_content['text']

        for h3_header, h3_text in h2_content['subelements'].items():
            child_element = ET.SubElement(parent_element, normalize_title(h3_header))
            child_element.text = h3_text

    return root

def read_dtd(file_path):
    elements_structure = {}
    with open(file_path, 'r') as file:
        for line in file:
            if '<!ELEMENT' in line:
                parts = line.split()
                parent = normalize_title(parts[1])

                children_str = line[line.find('(')+1 : line.find(')')]
                children = [normalize_title(child.strip()) for child in children_str.split(',') if child.strip()]

                if not children or children == ['#PCDATA']:
                    children = None

                elements_structure[parent] = children

    return elements_structure


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