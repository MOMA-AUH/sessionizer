import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from sessionizer.colors import RGBColorOption


class AllignmentGroupByOption(str, Enum):
    # IGVNAME = "toolname"
    STRAND = "strand"
    SAMPLE = "sample"
    READ_GROUP = "read_group"
    LIBRARY = "library"
    FIRST_OF_PAIR_STRAND = "first_of_pair"
    PAIR_ORIENTATION = "pair_orientation"
    MATE_CHROMOSOME = "mate_chromosome"
    CHIMERIC = "chimeric"
    SUPPLEMENTARY = "supplementary"
    BASE_AT_POS = "base_at_position"
    INSERTION_AT_POS = "insertion_at_position"
    MOVIE = "movie"
    ZMW = "ZMW"
    HAPLOTYPE = "haplotype"
    READ_ORDER = "read_order"
    LINKED = "linked"
    PHASE = "phase"
    REFERENCE_CONCORDANCE = "reference_concordance"
    MAPPING_QUALITY = "mapping_quality"
    NONE = "none"

    def __str__(self):
        return self.value


class AllignmentColorByOption(str, Enum):
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


class AllignmentDisplayModeOption(str, Enum):
    EXPANDED = "expanded"
    COLLAPSED = "collapsed"
    SQUISHED = "squished"

    def __str__(self):
        return self.value


class BigWigPlotTypeOption(str, Enum):
    # IGVNAME = "toolname"
    LINE_PLOT = "line"
    SCATTER_PLOT = "scatter"
    HEATMAP = "heatmap"
    BAR_CHART = "bar"
    NONE = "none"

    def __str__(self):
        return self.value


@dataclass
class DataTrack:
    name: str
    path: Path
    height: int | None

    file_type: str = field(init=False)

    def __post_init__(self):
        self.file_type = self.path.suffix

    # Method for adding resource to IGV session
    def add_resource(self, parent_elem):
        return ET.SubElement(parent_elem, "Resource", path=str(self.path))

    # Method for adding track to IGV session
    def add_track(self, session_panel: ET.Element):
        track_elem = ET.SubElement(
            session_panel,
            "Track",
            name=self.name,
            id=self.path.name,
        )
        if self.height is not None:
            track_elem.set("height", str(self.height))

        return track_elem


@dataclass
class AllignmentTrack(DataTrack):
    group_by: AllignmentGroupByOption
    color_by: AllignmentColorByOption
    display_mode: AllignmentDisplayModeOption

    hide_small_indels: bool
    small_indel_threshold: int
    quick_consensus_mode: bool

    show_coverage: bool
    show_junctions: bool

    def add_track(self, session_panel: ET.Element):
        # Add coverage track
        ET.SubElement(
            session_panel,
            "Track",
            id=os.path.basename(self.path) + "_coverage",
            visible=str(self.show_coverage).lower(),
        )

        # Add junctions track
        ET.SubElement(
            session_panel,
            "Track",
            id=os.path.basename(self.path) + "_junctions",
            visible=str(self.show_junctions).lower(),
        )

        # Add alligment track
        track_elem = super().add_track(session_panel)

        # Add attributes for BAM track
        track_elem.set("groupBy", str(self.group_by.name))
        track_elem.set("colorBy", str(self.color_by.name))
        track_elem.set("displayMode", str(self.display_mode.name))

        # Add RenderOptions:
        render_options = ET.SubElement(
            track_elem,
            "RenderOptions",
        )
        render_options.set("hideSmallIndels", str(self.hide_small_indels).lower())
        render_options.set("smallIndelThreshold", str(self.small_indel_threshold))
        render_options.set("quickConsensusMode", str(self.quick_consensus_mode).lower())

        return track_elem


@dataclass
class BigWigRangeOption:
    minimum: float | None
    baseline: float | None
    maximum: float | None


@dataclass
class BigWigTrack(DataTrack):
    """
    This class represents a BigWig Track.

    Attributes:
    - plot_type: The type of renderer for the track.
    - range: The range of the track.
    - color: The color of the track.
    - negative_color: The color for negative values in the track.

    """

    plot_type: BigWigPlotTypeOption
    range: BigWigRangeOption
    color: RGBColorOption
    negative_color: RGBColorOption

    # Method for adding track to IGV session
    def add_track(self, session_panel: ET.Element):
        # Create track element using super class method
        track_elem = super().add_track(session_panel)

        # Add attributes for BigWig track
        if self.color != RGBColorOption.NONE:
            track_elem.set("color", self.color.rgb_values())
        if self.negative_color != RGBColorOption.NONE:
            track_elem.set("altColor", self.negative_color.rgb_values())
        if self.plot_type != BigWigPlotTypeOption.NONE:
            track_elem.set("renderer", self.plot_type.name)
        if self.range is not None:
            range_elem = ET.SubElement(
                track_elem,
                "DataRange",
                type="LINEAR",
            )
            if self.range.minimum:
                range_elem.set("minimum", str(self.range.minimum))
            if self.range.baseline:
                range_elem.set("baseline", str(self.range.baseline))
            if self.range.maximum:
                range_elem.set("maximum", str(self.range.maximum))
        return track_elem


@dataclass
class VariantTrack(DataTrack):
    show_genotypes: bool

    def add_track(self, session_panel: ET.Element):
        # Create track element using super class method
        track_elem = super().add_track(session_panel)

        # Add attributes for variant track
        track_elem.set("showGenotypes", str(self.show_genotypes).lower())

        return track_elem


class GtfDisplayModeOption(str, Enum):
    EXPANDED = "expanded"
    COLLAPSED = "collapsed"
    SQUISHED = "squished"

    def __str__(self):
        return self.value


@dataclass
class GtfTrack(DataTrack):
    display_mode: GtfDisplayModeOption

    def add_track(self, session_panel: ET.Element):
        # Create track element using super class method
        track_elem = super().add_track(session_panel)

        # Add attributes for GTF track
        track_elem.set("displayMode", self.display_mode)

        return track_elem
