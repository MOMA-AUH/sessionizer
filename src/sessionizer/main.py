import os
import re
from pathlib import Path
from typing import List

import typer
from typing_extensions import Annotated

from sessionizer.colors import RGBColorOption
from sessionizer.create_igv_session import generate_igv_session
from sessionizer.genomes import GENOME
from sessionizer.track_elements import (
    AllignmentColorByOption,
    AllignmentDisplayModeOption,
    AllignmentGroupByOption,
    BigWigPlotTypeOption,
    BigWigRangeOption,
)
from sessionizer.utils import generate_symlink

app = typer.Typer(rich_markup_mode="rich")


def bw_range_parser(value: str):
    if not re.match(r"^\d+(\.\d+)?,\d+(\.\d+)?(,\d+(\.\d+)?)?$", value):
        raise ValueError(f"The bw_range {value} does not fit the pattern float,float (min,max) or float,float,float (min,mid,max).")

    # If range has 2 numbers: extract and set min and max
    if value.count(",") == 1:
        minimum, maximum = map(float, value.split(","))
    # If range has 3 numbers: min, mid, max
    elif value.count(",") == 2:
        minimum, baseline, maximum = map(float, value.split(","))

    return BigWigRangeOption(minimum=float(minimum), baseline=float(baseline), maximum=float(maximum))


# Options sections
GENOME_OPTIONS = "Genome options"
INPUT_FILES_OPTIONS = "Input files options"
TRACK_OPTIONS = "Track options"
ALIGNMENT_OPTIONS = "Alignment options"
BIGWIG_OPTIONS = "BigWig options"
VARIANT_OPTIONS = "Variant options"


@app.command()
def run(
    file: Annotated[
        List[Path],
        typer.Option(
            help="Input file (can be used multiple times)",
            exists=True,
        ),
    ],
    output: Annotated[
        Path,
        typer.Option(
            help="Output XML session file",
            exists=False,
        ),
    ] = Path("session.xml"),
    # Genome options
    genome: Annotated[
        GENOME,
        typer.Option(
            help="Genome track options",
            rich_help_panel=GENOME_OPTIONS,
        ),
    ] = GENOME.HG38,
    genome_path: Annotated[
        Path,
        typer.Option(
            help="Path to custom genome FASTA file",
            rich_help_panel=GENOME_OPTIONS,
            exists=True,
        ),
    ] = None,
    # Input files options
    use_relative_paths: Annotated[
        bool,
        typer.Option(
            help="Use relative paths for input files",
            rich_help_panel=INPUT_FILES_OPTIONS,
        ),
    ] = True,
    generate_symlinks: Annotated[
        bool,
        typer.Option(
            help="Generate symlinks to input files",
            rich_help_panel=INPUT_FILES_OPTIONS,
        ),
    ] = False,
    # Track options
    name: Annotated[
        List[str],
        typer.Option(
            help="Name shown in IGV for input file (can be used multiple times)",
            rich_help_panel=TRACK_OPTIONS,
        ),
    ] = None,
    height: Annotated[
        List[int],
        typer.Option(
            help="Height of track in IGV (can be used multiple times)",
            rich_help_panel=TRACK_OPTIONS,
        ),
    ] = None,
    # Alignment options
    bam_group_by: Annotated[
        List[AllignmentGroupByOption],
        typer.Option(
            help="Parameter to group bams by.",
            rich_help_panel=ALIGNMENT_OPTIONS,
        ),
    ] = [AllignmentGroupByOption.NONE],
    bam_color_by: Annotated[
        List[AllignmentColorByOption],
        typer.Option(
            help="Parameter to color bams by.",
            rich_help_panel=ALIGNMENT_OPTIONS,
        ),
    ] = [AllignmentColorByOption.NONE],
    bam_display_mode: Annotated[
        List[AllignmentDisplayModeOption],
        typer.Option(
            help="Parameter to display mode for bams.",
            rich_help_panel=ALIGNMENT_OPTIONS,
        ),
    ] = [AllignmentDisplayModeOption.COLLAPSED],
    bam_show_coverage: Annotated[
        List[bool],
        typer.Option(
            help="Parameter to show coverage on bams.",
            rich_help_panel=ALIGNMENT_OPTIONS,
        ),
    ] = [False],
    bam_show_junctions: Annotated[
        List[bool],
        typer.Option(
            help="Parameter to show junctions on bams.",
            rich_help_panel=ALIGNMENT_OPTIONS,
        ),
    ] = [False],
    # BigWig options
    bw_ranges: Annotated[
        List[BigWigRangeOption],
        typer.Option(
            help="Parameter to set bw ranges",
            rich_help_panel=BIGWIG_OPTIONS,
            parser=bw_range_parser,
        ),
    ] = None,
    bw_color: Annotated[
        List[RGBColorOption],
        typer.Option(
            help="Parameter to set bw color",
            rich_help_panel=BIGWIG_OPTIONS,
        ),
    ] = [RGBColorOption.NONE],
    bw_negative_color: Annotated[
        List[RGBColorOption],
        typer.Option(
            help="Parameter to set bw negative color",
            rich_help_panel=BIGWIG_OPTIONS,
        ),
    ] = [RGBColorOption.NONE],
    bw_plot_type: Annotated[
        List[BigWigPlotTypeOption],
        typer.Option(
            help="Parameter to set bw plot type",
            rich_help_panel=BIGWIG_OPTIONS,
        ),
    ] = [BigWigPlotTypeOption.BAR_CHART],
    # Variant options
    vcf_show_genotypes: Annotated[
        List[bool],
        typer.Option(
            help="Parameter to show genotypes on vcf tracks.",
            rich_help_panel=VARIANT_OPTIONS,
        ),
    ] = [False],
):
    # If generate_symlinks is True, create symlinks to the input files
    if generate_symlinks:
        igv_shortcut_dir = os.path.join(os.path.dirname(output), "igv_shortcuts")
        os.makedirs(igv_shortcut_dir, exist_ok=True)
        file = [generate_symlink(igv_shortcut_dir, file) for file in file]

        if genome_path:
            genome_path = generate_symlink(igv_shortcut_dir, genome_path)

    # If use_relative_paths is True, create paths to the input files relative to the output file
    if use_relative_paths:
        file = [os.path.relpath(path=file, start=os.path.dirname(output)) for file in file]

        if genome_path:
            genome_path = os.path.relpath(path=genome_path, start=os.path.dirname(output))

    # Generate XML
    xml_str = generate_igv_session(
        files=file,
        names=name,
        heights=height,
        genome=genome,
        genome_path=genome_path,
        bam_group_by=bam_group_by,
        bam_color_by=bam_color_by,
        bam_display_mode=bam_display_mode,
        bam_show_coverage=bam_show_coverage,
        bam_show_junctions=bam_show_junctions,
        bw_ranges=bw_ranges,
        bw_color=bw_color,
        bw_negative_color=bw_negative_color,
        bw_plot_type=bw_plot_type,
        vcf_show_genotypes=vcf_show_genotypes,
    )

    # Save to output file
    with open(output, "w", encoding="utf-8") as output_file:
        output_file.write(xml_str)


if __name__ == "__main__":
    app()
