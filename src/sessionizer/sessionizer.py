import argparse
import os
import re
import xml.etree.ElementTree as ET
from itertools import cycle
from typing import List
from xml.dom import minidom

from sessionizer.colors import RGB_COLOR_DICT
from sessionizer.track_elements import AllignmentColorByOption, AllignmentGroupByOption, BamTrack, BigWigRendererEnum, BigWigTrack, DataTrack
from sessionizer.utils import generate_symlink

GENOMES = {
    "hg19": "hg19",
    "hg38": "hg38",
    "t2t": "chm13v2.0",
}


def create_igv_session(
    files: List[str],
    names: List[str] | None,
    heights: List[int | None],
    bam_group_by: List[AllignmentGroupByOption],
    bam_color_by: List[AllignmentColorByOption],
    bw_ranges: List[str | None],
    bw_color: List[str | None],
    bw_negative_color: List[str | None],
    bw_plot_type: List[BigWigRendererEnum],
    genome: str,
    genome_path: str,
    output: str,
    use_relative_paths: bool | None,
    generate_symlinks: bool | None,
):
    # If generate_symlinks is True, create symlinks to the input files
    if generate_symlinks:
        igv_shortcut_dir = os.path.join(os.path.dirname(output), "igv_shortcuts")
        os.makedirs(igv_shortcut_dir, exist_ok=True)
        files = [generate_symlink(igv_shortcut_dir, file) for file in files]

        if genome_path:
            genome_path = generate_symlink(igv_shortcut_dir, genome_path)

    # If use_relative_paths is True, create paths to the input files relative to the output file
    if use_relative_paths:
        files = [os.path.relpath(path=file, start=os.path.dirname(output)) for file in files]

        if genome_path:
            genome_path = os.path.relpath(path=genome_path, start=os.path.dirname(output))

    if not names:
        # If names list is not provided, set it to the file name
        names = [os.path.basename(file) for file in files]
    elif len(files) != len(names):
        # Check if the lengths of file lists and names lists are equal
        raise ValueError(f"Length of files ({len(files)}) and names ({len(names)}) must be equal.")

    if not heights:
        # If heights list is not provided, set it to none
        heights = [None] * len(files)
    elif len(files) != len(heights):
        # Check if the lengths of file lists and heights lists are equal
        raise ValueError(f"Length of files ({len(files)}) and heights ({len(heights)}) must be equal.")

    # Hanlde bam/cram specific arguments
    alignment_files = [file for file in files if file.endswith(".bam") or file.endswith(".cram")]
    if alignment_files:
        # Check if the length of bam_group_by and bam_color_by lists are 1 or equal to the number of bams
        if bam_group_by:
            if len(bam_group_by) != len(alignment_files) and len(bam_group_by) != 1:
                raise ValueError(f"Length of bam_group_by ({len(bam_group_by)}) must be 1 or equal to the number of bams ({len(alignment_files)}).")
            if len(bam_group_by) == 1:
                bam_group_by = bam_group_by * len(alignment_files)
        else:
            bam_group_by = [AllignmentGroupByOption.NONE] * len(alignment_files)

        # If only 1 group_by_phase or color_by_methylation are provided, set them to the same value
        if bam_color_by:
            if len(bam_color_by) != len(alignment_files) and len(bam_color_by) != 1:
                raise ValueError(f"Length of bam_color_by ({len(bam_color_by)}) must be 1 or equal to the number of bams ({len(alignment_files)}).")
            if len(bam_color_by) == 1:
                bam_color_by = bam_color_by * len(alignment_files)
        else:
            bam_color_by = [AllignmentColorByOption.NONE] * len(alignment_files)

        # If group_by_phase and color_by_methylation are not provided, set them to False

    # Handle BigWig specific arguments
    bigwig_files = [file for file in files if file.endswith(".bw")]
    if bigwig_files:
        if bw_ranges:
            # Check if all bw_ranges fits the pattern float,float (min,max) or float,float,float (min,mid,max)
            for bw_range in bw_ranges:
                if bw_range and not re.match(r"^\d+(\.\d+)?,\d+(\.\d+)?(,\d+(\.\d+)?)?$", bw_range):
                    raise ValueError(f"The bw_range {bw_range} does not fit the pattern float,float (min,max) or float,float,float (min,mid,max).")

        def check_list_length(lst, expected_length, variable_name):
            if len(lst) != expected_length and len(lst) != 1:
                raise ValueError(f"Length of {variable_name}, ({len(lst)}) must be 1 or equal to the number of bigwig files ({expected_length}).")

        check_list_length(bw_color, len(bigwig_files), "bw_color")
        check_list_length(bw_negative_color, len(bigwig_files), "bw_negative_color")
        check_list_length(bw_plot_type, len(bigwig_files), "bw_plot_type")

        if bw_color and len(bw_color) == 1:
            bw_color = bw_color * len(bigwig_files)
        if bw_negative_color and len(bw_negative_color) == 1:
            bw_negative_color = bw_negative_color * len(bigwig_files)
        if bw_plot_type and len(bw_plot_type) == 1:
            bw_plot_type = bw_plot_type * len(bigwig_files)

    # Cycles for sublists
    bam_group_by_cycle = cycle(bam_group_by)
    bam_color_by_cycle = cycle(bam_color_by)

    bw_ranges_cycle = cycle(bw_ranges)
    bw_color_cycle = cycle(bw_color)
    bw_negative_color_cycle = cycle(bw_negative_color)
    bw_plot_type_cycle = cycle(bw_plot_type)

    # Create tracks
    tracks: List[DataTrack] = []
    for file, name, height in zip(files, names, heights):
        # Hanlde bam/cram specific arguments
        if file.endswith(".bam") or file.endswith(".cram"):
            tracks.append(
                BamTrack(
                    name=name,
                    path=file,
                    height=height,
                    group_by=next(bam_group_by_cycle),
                    color_by=next(bam_color_by_cycle),
                )
            )

        # Handle BigWig specific arguments
        if file.endswith(".bw"):
            tracks.append(
                BigWigTrack(
                    name=name,
                    path=file,
                    height=height,
                    range=next(bw_ranges_cycle),
                    color=next(bw_color_cycle),
                    negative_color=next(bw_negative_color_cycle),
                    plot_type=next(bw_plot_type_cycle),
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

    # Create the root element
    root = ET.Element("Session")

    # Add genome information
    if genome in GENOMES:
        root.set("genome", GENOMES[genome])
    elif genome == "custom":
        root.set("genome", genome_path)
    else:
        raise ValueError(f"Invalid genome: {genome}. Must be one of {GENOMES.keys()} or 'custom'.")

    root.set("locus", "All")
    root.set("version", "8")
    root.set("relativePath", "true")

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

    # Save to output file
    with open(output, "w", encoding="utf-8") as output_file:
        output_file.write(xml_str)


def main():
    parser = argparse.ArgumentParser(
        description="""
        Easy way to create an IGV session file in XML format.
        """,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--files",
        required=True,
        nargs="+",
        help="List of input files",
        type=os.path.realpath,
    )
    parser.add_argument(
        "--names",
        nargs="+",
        help="List of names for input files",
    )
    parser.add_argument(
        "--heights",
        nargs="+",
        type=int,
        help="List of heights for input files",
    )

    # Alignement options
    parser.add_argument(
        "--bam_group_by",
        nargs="+",
        choices=list(AllignmentGroupByOption),
        type=AllignmentGroupByOption,
        default=[AllignmentGroupByOption.NONE],
        help="Parameter to group bams by. Either single value (shared) or multiple values (per bam).",
    )
    parser.add_argument(
        "--bam_color_by",
        nargs="+",
        choices=list(AllignmentColorByOption),
        type=AllignmentColorByOption,
        default=[AllignmentColorByOption.NONE],
        help="Parameter to color bams by. Either single value (shared) or multiple values (per bam).",
    )

    # BigWig options
    parser.add_argument(
        "--bw_ranges",
        nargs="+",
        type=str,
        default=[None],
        help="List of comma seperated float values to set bw range. Either 'min,max' or 'min,mid,max', eg. '0.4,10,100'.",
    )
    parser.add_argument(
        "--bw_color",
        nargs="+",
        choices=list(RGB_COLOR_DICT.keys()),
        type=str,
        default=[None],
        help="Parameter to set bw color",
    )
    parser.add_argument(
        "--bw_negative_color",
        nargs="+",
        choices=list(RGB_COLOR_DICT.keys()),
        type=str,
        default=[None],
        help="Parameter to set bw negative color",
    )
    parser.add_argument(
        "--bw_plot_type",
        nargs="+",
        choices=list(BigWigRendererEnum),
        type=BigWigRendererEnum,
        default=[BigWigRendererEnum.BAR_CHART],
        help="Parameter to set bw plot type",
    )

    # Genome options
    parser.add_argument(
        "--genome",
        required=True,
        choices=["hg19", "hg38", "t2t", "custom"],
        help="Genome track option",
    )
    parser.add_argument(
        "--genome_path",
        default="",
        help="Path to custom genome FASTA file (for genome = 'custom' option)",
    )

    # Output options
    parser.add_argument(
        "--output",
        required=True,
        help="Output XML session file",
        type=os.path.realpath,
    )
    parser.add_argument(
        "--use_relative_paths",
        default=True,
        help="Use relative paths for input files",
    )
    parser.add_argument(
        "--generate_symlinks",
        default=False,
        help="Generate symlinks to input files",
    )

    args = parser.parse_args()

    create_igv_session(
        files=args.files,
        names=args.names,
        heights=args.heights,
        # BAM arguments
        bam_group_by=args.bam_group_by,
        bam_color_by=args.bam_color_by,
        # BigWig arguments
        bw_ranges=args.bw_ranges,
        bw_color=args.bw_color,
        bw_negative_color=args.bw_negative_color,
        bw_plot_type=args.bw_plot_type,
        # Genome arguments
        genome=args.genome,
        genome_path=args.genome_path,
        # Output arguments
        output=args.output,
        use_relative_paths=args.use_relative_paths,
        generate_symlinks=args.generate_symlinks,
    )


if __name__ == "__main__":
    main()
