import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from enum import Enum

from sessionizer.colors import RGB_COLOR_DICT


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


class AllignmentDisplayMode(Enum):
    EXPANDED = "expanded"
    COLLAPSED = "collapsed"
    SQUISHED = "squished"

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
    def add_track(self, session_panel: ET.Element):
        track_elem = ET.SubElement(
            session_panel,
            "Track",
            name=self.name,
            id=os.path.basename(self.path),
        )
        if self.height is not None:
            track_elem.set("height", str(self.height))

        return track_elem


@dataclass
class AllignmentTrack(DataTrack):
    group_by: AllignmentGroupByOption
    color_by: AllignmentColorByOption
    display_mode: AllignmentDisplayMode
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
    def add_track(self, session_panel: ET.Element):
        # Create track element using super class method
        track_elem = super().add_track(session_panel)

        # Add attributes for BigWig track
        if self.color is not None and RGB_COLOR_DICT[self.color]:
            track_elem.set("color", RGB_COLOR_DICT[self.color])
        if self.negative_color is not None and RGB_COLOR_DICT[self.negative_color]:
            track_elem.set("altColor", RGB_COLOR_DICT[self.negative_color])
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


@dataclass
class VariantTrack(DataTrack):
    show_genotypes: bool

    def add_track(self, session_panel: ET.Element):
        # Create track element using super class method
        track_elem = super().add_track(session_panel)

        # Add attributes for variant track
        track_elem.set("showGenotypes", str(self.show_genotypes).lower())
