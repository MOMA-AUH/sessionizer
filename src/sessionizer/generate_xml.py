import xml.etree.ElementTree as ET
from typing import List
from xml.dom import minidom

from sessionizer.genomes import GENOMES
from sessionizer.track_elements import DataTrack


def generate_xml(genome: str, genome_path: str, tracks: List[DataTrack]) -> str:
    # Initialize session xml
    root = ET.Element("Session")
    root.set("locus", "All")
    root.set("version", "8")
    root.set("relativePath", "true")

    # Add genome information
    if genome in GENOMES:
        root.set("genome", GENOMES[genome])
    elif genome == "custom":
        root.set("genome", genome_path)

    # Add resources
    resources_element = ET.SubElement(root, "Resources")

    # Add resource paths
    for track in tracks:
        track.add_resource(resources_element)

    # Add data tracks
    main_panel_elem = ET.SubElement(root, "Panel", name="DataPanel")
    for track in tracks:
        track.add_track(main_panel_elem)

    # Add feature tracks
    feature_panel = ET.SubElement(root, "Panel", name="FeaturePanel")

    # Add reference sequnce
    ET.SubElement(
        feature_panel,
        "Track",
        id="Reference sequence",
        name="Reference sequence",
    )
    # Add genes
    gene_ids = []

    if genome == "hg38":
        gene_ids = ["hg38_genes"]
    elif genome == "hg19":
        gene_ids = ["hg19_genes"]
    elif genome == "t2t":
        gene_ids = [
            "https://hgdownload.soe.ucsc.edu/hubs/GCA/009/914/755/GCA_009914755.4/bbi/GCA_009914755.4_T2T-CHM13v2.0.catLiftOffGenesV1/catLiftOffGenesV1.bb",
            "https://hgdownload.soe.ucsc.edu/hubs/GCA/009/914/755/GCA_009914755.4/bbi/GCA_009914755.4_T2T-CHM13v2.0.augustus.bb",
        ]

    if gene_ids:
        for gene_id in gene_ids:
            ET.SubElement(
                feature_panel,
                "Track",
                id=gene_id,
            )

    # Panel layout
    ET.SubElement(root, "PanelLayout", dividerFractions="0.80")

    # Create XML string
    xml_str = ET.tostring(root, encoding="utf-8")

    # Prettify XML using minidom
    xml_str = minidom.parseString(xml_str).toprettyxml(indent="  ")
    return xml_str
