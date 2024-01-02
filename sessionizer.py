import argparse
import os
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from enum import Enum
from itertools import cycle
from typing import List
from xml.dom import minidom

RGB_COLORS = {
    "black": "0,0,0",
    "white": "255,255,255",
    "red": "255,0,0",
    "lime": "0,255,0",
    "blue": "0,0,255",
    "yellow": "255,255,0",
    "cyan": "0,255,255",
    "magenta": "255,0,255",
    "silver": "192,192,192",
    "gray": "128,128,128",
    "maroon": "128,0,0",
    "olive": "128,128,0",
    "green": "0,128,0",
    "purple": "128,0,128",
    "teal": "0,128,128",
    "navy": "0,0,128",
    "none": None,
}

GENOMES = {
    "hg19": "hg19",
    "hg38": "hg38",
    "t2t": "chm13v2.0",
}

FILE_INDEX_EXTENSIONS = {
    "bam": ".bai",
    "cram": ".crai",
    "vcf": ".tbi",
    "vcf.gz": ".tbi",
    "fasta": ".fai",
    "FASTA": ".fai",
    "bed": ".tbi",
    "bed.gz": ".tbi",
}


class AllignmentGroupByOption(Enum):
    # IGVNAME = "toolname"
    NONE = "none"
    PHASE = "phase"

    def __str__(self):
        return self.value


class AllignmentColorByOption(Enum):
    # See full list of options here: https://github.com/igvteam/igv/blob/3a1511c73af1d8eaa31e8fb4058c72314da8157e/src/main/java/org/broad/igv/sam/AlignmentTrack.java#L95
    # IGVNAME = "toolname"
    NONE = "none"
    BASE_MODIFICATION_5MC = "meth"
    INSERT_SIZE = "insert_size"
    READ_STRAND = "read_strand"
    FIRST_OF_PAIR_STRAND = "first_of_pair_strand"
    PAIR_ORIENTATION = "pair_orientation"
    READ_ORDER = "read_order"
    SAMPLE = "sample"
    READ_GROUP = "read_group"
    LIBRARY = "library"
    MOVIE = "movie"
    ZMW = "zmw"
    BISULFITE = "bisulfite"
    NOMESEQ = "nomeseq"
    TAG = "tag"
    UNEXPECTED_PAIR = "unexpected_pair"
    MAPPED_SIZE = "mapped_size"
    LINK_STRAND = "link_strand"
    YC_TAG = "yc_tag"
    BASE_MODIFICATION = "base_modification"
    BASE_MODIFICATION_2COLOR = "base_modification_2color"
    SMRT_SUBREAD_IPD = "smrt_subread_ipd"
    SMRT_SUBREAD_PW = "smrt_subread_pw"
    SMRT_CCS_FWD_IPD = "smrt_ccs_fwd_ipd"
    SMRT_CCS_FWD_PW = "smrt_ccs_fwd_pw"
    SMRT_CCS_REV_IPD = "smrt_ccs_rev_ipd"
    SMRT_CCS_REV_PW = "smrt_ccs_rev_pw"

    def __str__(self):
        return self.value


class BigWigRendererEnum(Enum):
    # IGVNAME = "toolname"
    LINE_PLOT = "line"
    SCATTER_PLOT = "scatter"
    HEATMAP = "heatmap"
    BAR_CHART = "bar"

    def __str__(self):
        return self.value


@dataclass
class DataTrack:
    name: str
    path: str
    height: int | None

    file_type: str = field(init=False)

    def __post_init__(self):
        self.file_type = self.path.split(".")[-1]

    # Method for adding resource to IGV session
    def add_resource(self, parent_elem):
        return ET.SubElement(parent_elem, "Resource", name=self.name, path=self.path)

    # Method for adding track to IGV session
    def add_track(self, parent_elem):
        track_elem = ET.SubElement(
            parent_elem,
            "Track",
            name=self.name,
            id=os.path.basename(self.path),
        )
        if self.height is not None:
            track_elem.set("height", str(self.height))

        return track_elem


@dataclass
class BamTrack(DataTrack):
    group_by: AllignmentGroupByOption
    color_by: AllignmentColorByOption

    def add_track(self, parent_elem):
        track_elem = super().add_track(parent_elem)

        # Add attributes for BAM track
        track_elem.set("groupBy", str(self.group_by))
        track_elem.set("colorBy", str(self.color_by))
        return track_elem


@dataclass
class BigWigTrack(DataTrack):
    """
    This class represents a BigWig Track.

    Attributes:
    - plot_type: The type of renderer for the track.
    - range: The range of the track.
    - color: The color of the track.
    - negative_color: The color for negative values in the track.

    Additional attributes:
    - min: The minimum value of the track.
    - mid: The mid value of the track.
    - max: The maximum value of the track.
    """

    plot_type: BigWigRendererEnum
    range: str | None
    color: str | None
    negative_color: str | None

    min: float | None = field(init=False)
    mid: float | None = field(init=False)
    max: float | None = field(init=False)

    def __post_init__(self):
        if not self.range:
            self.min = self.mid = self.max = None
        else:
            # If range has 2 numbers: extract and set min and max
            if self.range.count(",") == 1:
                self.min, self.max = map(float, self.range.split(","))
            # If range has 3 numbers: min, mid, max
            elif self.range.count(",") == 2:
                self.min, self.mid, self.max = map(float, self.range.split(","))
            # Else invalid range
            else:
                raise ValueError(f"Invalid range: {self.range}. Should be min,max or min,mid,max.")

    # Method for adding track to IGV session
    def add_track(self, parent_elem):
        # Create track element using super class method
        track_elem = super().add_track(parent_elem)

        # Add attributes for BigWig track
        if self.color is not None and RGB_COLORS[self.color]:
            track_elem.set("color", RGB_COLORS[self.color])
        if self.negative_color is not None and RGB_COLORS[self.negative_color]:
            track_elem.set("altColor", RGB_COLORS[self.negative_color])
        if self.plot_type is not None:
            track_elem.set("renderer", self.plot_type.name)
        if all(x is not None for x in [self.min, self.mid, self.max]):
            ET.SubElement(
                track_elem,
                "DataRange",
                minimum=str(self.min),
                baseline=str(self.mid),
                maximum=str(self.max),
                type="LINEAR",
            )
        return track_elem


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


def generate_symlink(shortcut_dir, file):
    symlink = os.path.join(shortcut_dir, os.path.basename(file))
    os.symlink(src=file, dst=symlink)

    # Handle index files if they exist (https://igvteam.github.io/igv-webapp/fileFormats.html)
    file_type = file.split(".")[-1]
    if file_type in FILE_INDEX_EXTENSIONS:
        file_index = file + FILE_INDEX_EXTENSIONS[file_type]
        if os.path.exists(file_index):
            file_index_symlink = os.path.join(shortcut_dir, os.path.basename(file_index))
            os.symlink(file_index, file_index_symlink)

    return symlink


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
        choices=list(RGB_COLORS.keys()),
        type=str,
        default=[None],
        help="Parameter to set bw color",
    )
    parser.add_argument(
        "--bw_negative_color",
        nargs="+",
        choices=list(RGB_COLORS.keys()),
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
