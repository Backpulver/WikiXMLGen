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

    def find_content_for_element(element_name, content):
        normalized_element = normalize_title(element_name)
        text_content = ''
        for key, value in content.items():
            if key.endswith(normalized_element):
                if isinstance(value, dict) and 'text' in value:
                    text_content += value['text']
                elif isinstance(value, str):
                    text_content += value
                text_content += '\n'
        return text_content.strip()

    def add_children_from_dtd(parent_element, dtd_element, content):
        for child_name in dtd_structure.get(dtd_element, []):
            child_text = find_content_for_element(child_name, content)
            child_element = ET.SubElement(parent_element, child_name)
            if child_text:
                child_element.text = child_text
            else:
                nested_content = content.get(normalize_title(child_name), {}).get('subelements', {})
                add_children_from_dtd(child_element, child_name, nested_content)

    add_children_from_dtd(root, root_element_name, content)
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
    tree.write(f"{root_element_name}.xml", encoding='utf-8', xml_declaration=True)
    print(f"XML file generated successfully: {root_element_name}.xml")


if __name__ == "__main__":
    main()