import xml.etree.ElementTree as ET
from itertools import cycle
from pathlib import Path
from typing import List
from xml.dom import minidom

from sessionizer.colors import RGBColorOption
from sessionizer.filetypes import ALIGNMENT_SUFFIXES, BIGWIG_SUFFIXES, GTF_SUFFIXES, VCF_SUFFIXES
from sessionizer.genomes import GENOME
from sessionizer.track_elements import (
    AllignmentColorByOption,
    AllignmentDisplayModeOption,
    AllignmentGroupByOption,
    AllignmentTrack,
    BigWigPlotTypeOption,
    BigWigRangeOption,
    BigWigTrack,
    DataTrack,
    GtfDisplayModeOption,
    GtfTrack,
    VariantTrack,
)
from sessionizer.utils import filter_files_by_filetype


def hanlde_attribute(attribute: str, values: List, files: List, file_type: str) -> List:
    if len(values) not in [len(files), 1]:
        raise ValueError(f"Length of {attribute} ({len(values)}) must be 1 or equal to the number of {file_type} ({len(files)}).")
    return values * len(files) if len(values) == 1 else values


def generate_xml(genome: GENOME, genome_path: Path, tracks: List[DataTrack]) -> str:
    # Initialize session xml
    root = ET.Element("Session")

    # Add genome information
    if genome in [GENOME.HG38, GENOME.HG19, GENOME.T2T]:
        root.set("genome", genome.get_igv_name())
    elif genome == GENOME.CUSTOM:
        root.set("genome", str(genome_path))

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

    if genome == "hg19":
        gene_ids = ["hg19_genes"]
    elif genome == "hg38":
        gene_ids = [
            "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/database/ncbiRefSeq.txt.gz",
        ]
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


def generate_igv_session(
    files: List[Path],
    names: List[str],
    heights: List[int],
    genome: GENOME,
    genome_path: Path,
    bam_group_by: List[AllignmentGroupByOption],
    bam_color_by: List[AllignmentColorByOption],
    bam_color_by_tag: List[str],
    bam_display_mode: List[AllignmentDisplayModeOption],
    bam_hide_small_indels: List[bool],
    bam_small_indel_threshold: List[int],
    bam_show_coverage: List[bool],
    bam_show_junctions: List[bool],
    bw_ranges: List[BigWigRangeOption],
    bw_color: List[RGBColorOption],
    bw_negative_color: List[RGBColorOption],
    bw_plot_type: List[BigWigPlotTypeOption],
    bw_auto_scale: List[bool],
    vcf_show_genotypes: List[bool],
    vcf_feature_visibility_window: List[int],
    gtf_display_mode: List[GtfDisplayModeOption],
):
    # If names list is empty, set it to empty strings
    if names == [""]:
        names = [""] * len(files)
    # Check if the lengths of file lists and names lists are equal
    if len(files) != len(names):
        # Check if the lengths of file lists and names lists are equal
        raise ValueError(f"Length of files ({len(files)}) and names ({len(names)}) must be equal.")
    # Convert empty strings to file names
    names = [file.name if name == "" else name for file, name in zip(files, names)]

    if len(heights) == 1:
        heights = [0] * len(files)
    if len(files) != len(heights):
        # Check if the lengths of file lists and heights lists are equal
        raise ValueError(f"Length of files ({len(files)}) and heights ({len(heights)}) must be equal.")

    # Hanlde bam/cram specific arguments
    alignment_files = filter_files_by_filetype(files, ALIGNMENT_SUFFIXES)
    if alignment_files:
        bam_group_by = hanlde_attribute("bam_group_by", bam_group_by, alignment_files, "alignment files")
        bam_color_by = hanlde_attribute("bam_color_by", bam_color_by, alignment_files, "alignment files")
        bam_color_by_tag = hanlde_attribute("bam_color_by_tag", bam_color_by_tag, alignment_files, "alignment files")
        bam_display_mode = hanlde_attribute("bam_display_mode", bam_display_mode, alignment_files, "alignment files")
        bam_hide_small_indels = hanlde_attribute("bam_hide_small_indels", bam_hide_small_indels, alignment_files, "alignment files")
        bam_small_indel_threshold = hanlde_attribute("bam_small_indel_threshold", bam_small_indel_threshold, alignment_files, "alignment files")
        bam_show_coverage = hanlde_attribute("bam_show_coverage", bam_show_coverage, alignment_files, "alignment files")
        bam_show_junctions = hanlde_attribute("bam_show_junctions", bam_show_junctions, alignment_files, "alignment files")

        # If group_by_phase and color_by_methylation are not provided, set them to False

    # Handle BigWig specific arguments
    bigwig_files = filter_files_by_filetype(files, BIGWIG_SUFFIXES)
    if bigwig_files:
        bw_color = hanlde_attribute("bw_color", bw_color, bigwig_files, "bigwig files")
        bw_negative_color = hanlde_attribute("bw_negative_color", bw_negative_color, bigwig_files, "bigwig files")
        bw_plot_type = hanlde_attribute("bw_plot_type", bw_plot_type, bigwig_files, "bigwig files")
        bw_ranges = hanlde_attribute("bw_ranges", bw_ranges, bigwig_files, "bigwig files")
        bw_auto_scale = hanlde_attribute("bw_auto_scale", bw_auto_scale, bigwig_files, "bigwig files")

    # Handle VCF specific arguments
    vcf_files = filter_files_by_filetype(files, VCF_SUFFIXES)
    if vcf_files:
        vcf_show_genotypes = hanlde_attribute("vcf_show_genotypes", vcf_show_genotypes, vcf_files, "vcf files")
        vcf_feature_visibility_window = hanlde_attribute("vcf_feature_visibility_window", vcf_feature_visibility_window, vcf_files, "vcf files")

    # Handle GTF specific arguments
    gtf_files = filter_files_by_filetype(files, GTF_SUFFIXES)
    if gtf_files:
        gtf_display_mode = hanlde_attribute("gtf_display_mode", gtf_display_mode, gtf_files, "gtf files")

    # Cycles for attribute sublists
    # Allignment files
    bam_group_by_cycle = cycle(bam_group_by)
    bam_color_by_cycle = cycle(bam_color_by)
    bam_color_by_tag_cycle = cycle(bam_color_by_tag)
    bam_display_mode_cycle = cycle(bam_display_mode)
    bam_hide_small_indels_cycle = cycle(bam_hide_small_indels)
    bam_small_indel_threshold_cycle = cycle(bam_small_indel_threshold)
    bam_show_coverage_cycle = cycle(bam_show_coverage)
    bam_show_junctions_cycle = cycle(bam_show_junctions)

    # Bigwig files
    bw_ranges_cycle = cycle(bw_ranges)
    bw_color_cycle = cycle(bw_color)
    bw_negative_color_cycle = cycle(bw_negative_color)
    bw_plot_type_cycle = cycle(bw_plot_type)
    bw_auto_scale_cycle = cycle(bw_auto_scale)

    # VCF files
    vcf_show_genotypes_cycle = cycle(vcf_show_genotypes)
    vcf_feature_visibility_window_cycle = cycle(vcf_feature_visibility_window)

    # Gtf files
    gtf_display_mode_cycle = cycle(gtf_display_mode)

    # Create tracks
    tracks: List[DataTrack] = []
    for file, name, height in zip(files, names, heights):
        if any(file.name.endswith(suffix) for suffix in ALIGNMENT_SUFFIXES):
            # Hanlde bam/cram specific arguments
            tracks.append(
                AllignmentTrack(
                    name=name,
                    path=file,
                    height=height,
                    group_by=next(bam_group_by_cycle),
                    color_by=next(bam_color_by_cycle),
                    color_by_tag=next(bam_color_by_tag_cycle),
                    hide_small_indels=next(bam_hide_small_indels_cycle),
                    small_indel_threshold=next(bam_small_indel_threshold_cycle),
                    display_mode=next(bam_display_mode_cycle),
                    show_coverage=next(bam_show_coverage_cycle),
                    show_junctions=next(bam_show_junctions_cycle),
                )
            )
        elif any(file.name.endswith(suffix) for suffix in BIGWIG_SUFFIXES):
            # Handle BigWig specific arguments
            tracks.append(
                BigWigTrack(
                    name=name,
                    path=file,
                    height=height,
                    range=next(bw_ranges_cycle),
                    color=next(bw_color_cycle),
                    negative_color=next(bw_negative_color_cycle),
                    plot_type=next(bw_plot_type_cycle),
                    autoscale=next(bw_auto_scale_cycle),
                )
            )
        elif any(file.name.endswith(suffix) for suffix in VCF_SUFFIXES):
            # Handle VCF specific arguments
            tracks.append(
                VariantTrack(
                    name=name,
                    path=file,
                    height=height,
                    show_genotypes=next(vcf_show_genotypes_cycle),
                    feature_visibility_window=next(vcf_feature_visibility_window_cycle),
                )
            )
        elif any(file.name.endswith(suffix) for suffix in GTF_SUFFIXES):
            # Handle GTF specific arguments
            tracks.append(
                GtfTrack(
                    name=name,
                    path=file,
                    height=height,
                    display_mode=next(gtf_display_mode_cycle),
                )
            )
        # Handle other files
        else:
            tracks.append(
                DataTrack(
                    name=name,
                    path=file,
                    height=height,
                )
            )

    return generate_xml(genome, genome_path, tracks)
