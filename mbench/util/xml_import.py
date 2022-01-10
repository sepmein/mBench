from lxml import etree


def load_xml_config(path: str):
    """
    parse XML file into an lxml object
    :param path: string
    :return: parsed etree object
    """
    # xml file is quite small, load it into string once
    root = etree.parse(path)
    return root
