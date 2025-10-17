import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from sessionizer.colors import RGBColorOption


class AlignmentGroupByOption(str, Enum):
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


class AlignmentColorByOption(str, Enum):
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
    TAG = "tag"  # Special case - needs to be acompained by tag value

    def __str__(self):
        return self.value


class AlignmentDisplayModeOption(str, Enum):
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
    height: int
    clazz: str = field(default="org.broad.igv.track.DataSourceTrack")

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
            clazz=self.clazz,
            id=str(self.path),
        )
        if self.height != 0:
            track_elem.set("height", str(self.height))

        return track_elem


@dataclass
class AlignmentTrack(DataTrack):
    clazz: str = field(default="org.broad.igv.sam.AlignmentTrack", init=False)

    group_by: AlignmentGroupByOption
    color_by: AlignmentColorByOption
    color_by_tag: str
    display_mode: AlignmentDisplayModeOption

    hide_small_indels: bool
    small_indel_threshold: int

    show_coverage: bool
    show_junctions: bool

    def add_track(self, session_panel: ET.Element):
        # Add coverage track
        ET.SubElement(
            session_panel,
            "Track",
            clazz="org.broad.igv.sam.CoverageTrack",
            id=f"{self.path}_coverage",
            visible=str(self.show_coverage).lower(),
        )

        # Add junctions track
        ET.SubElement(
            session_panel,
            "Track",
            clazz="org.broad.igv.sam.SpliceJunctionTrack",
            id=f"{self.path}_junctions",
            visible=str(self.show_junctions).lower(),
        )

        # Add alligment track
        track_elem = super().add_track(session_panel)

        # Add attributes for BAM track
        track_elem.set("displayMode", str(self.display_mode.name))

        # Add RenderOptions:
        render_options = ET.SubElement(
            track_elem,
            "RenderOptions",
        )
        render_options.set("colorOption", str(self.color_by.name))
        if self.color_by == AlignmentColorByOption.TAG:
            render_options.set("colorByTag", self.color_by_tag)
        render_options.set("groupByOption", str(self.group_by.name))
        render_options.set("hideSmallIndels", str(self.hide_small_indels).lower())
        render_options.set("smallIndelThreshold", str(self.small_indel_threshold))

        return track_elem


@dataclass
class BigWigRangeOption:
    minimum: float
    baseline: float
    maximum: float


@dataclass
class BigWigTrack(DataTrack):
    """
    This class represents a BigWig Track.

    Attributes:
    - plot_type: The type of renderer for the track.
    - range: The range of the track.
    - color: The color of the track.
    - negative_color: The color for negative values in the track.
    - autoscale: Whether to autoscale the track values.

    """

    clazz: str = field(default="org.broad.igv.track.DataSourceTrack", init=False)

    plot_type: BigWigPlotTypeOption
    range: BigWigRangeOption
    color: RGBColorOption
    negative_color: RGBColorOption
    autoscale: bool

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
        track_elem.set("autoScale", str(self.autoscale).lower())

        # Add DataRange element
        if self.range is not None:
            range_elem = ET.SubElement(
                track_elem,
                "DataRange",
                type="LINEAR",
            )
            if self.range.minimum is not None:
                range_elem.set("minimum", str(self.range.minimum))
            if self.range.baseline is not None:
                range_elem.set("baseline", str(self.range.baseline))
            if self.range.maximum is not None:
                range_elem.set("maximum", str(self.range.maximum))
        return track_elem


@dataclass
class VariantTrack(DataTrack):
    clazz: str = field(default="org.broad.igv.variant.VariantTrack", init=False)

    show_genotypes: bool
    feature_visibility_window: int

    def add_track(self, session_panel: ET.Element):
        # Create track element using super class method
        track_elem = super().add_track(session_panel)

        # Add attributes for variant track
        track_elem.set("showGenotypes", str(self.show_genotypes).lower())
        track_elem.set("featureVisibilityWindow", str(self.feature_visibility_window))

        return track_elem


class GtfDisplayModeOption(str, Enum):
    EXPANDED = "expanded"
    COLLAPSED = "collapsed"
    SQUISHED = "squished"

    def __str__(self):
        return self.value


@dataclass
class GtfTrack(DataTrack):
    clazz: str = field(default="org.broad.igv.track.FeatureTrack", init=False)

    display_mode: GtfDisplayModeOption

    def add_track(self, session_panel: ET.Element):
        # Create track element using super class method
        track_elem = super().add_track(session_panel)

        # Add attributes for GTF track
        track_elem.set("displayMode", self.display_mode.name)

        return track_elem
