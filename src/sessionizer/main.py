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
    GtfDisplayModeOption,
)
from sessionizer.utils import generate_symlink

app = typer.Typer(rich_markup_mode="rich")


def bw_range_parser(value: str):
    if not re.match(r"^\d+(\.\d+)?,\d+(\.\d+)?(,\d+(\.\d+)?)?$", value):
        raise ValueError(f"The bw_range {value} does not fit the pattern float,float (min,max) or float,float,float (min,mid,max).")

    # If range has 2 numbers: extract and set min and max
    if value.count(",") == 1:
        minimum, maximum = map(float, value.split(","))
        baseline = None
    # If range has 3 numbers: min, mid, max
    elif value.count(",") == 2:
        minimum, baseline, maximum = map(float, value.split(","))

    return BigWigRangeOption(minimum=minimum, baseline=baseline, maximum=maximum)


# Options sections
GENOME_OPTIONS = "Genome options"
INPUT_FILES_OPTIONS = "Input files options"
TRACK_OPTIONS = "Track options"
ALIGNMENT_OPTIONS = "Alignment options"
BIGWIG_OPTIONS = "BigWig options"
VARIANT_OPTIONS = "Variant options"
GTF_OPTIONS = "GTF options"


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
            help="Output XML session file. If not specified, session will be printed to stdout.",
            exists=False,
        ),
    ] = None,
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
    ] = False,
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
    bam_hide_small_indels: Annotated[
        List[bool],
        typer.Option(
            help="Parameter to hide small indels on bams.",
            rich_help_panel=ALIGNMENT_OPTIONS,
        ),
    ] = [False],
    bam_small_indel_threshold: Annotated[
        List[int],
        typer.Option(
            help="Parameter to set small indel threshold on bams.",
            rich_help_panel=ALIGNMENT_OPTIONS,
        ),
    ] = [0],
    bam_quick_consensus_mode: Annotated[
        List[bool],
        typer.Option(
            help="Parameter to use quick consensus mode on bams.",
            rich_help_panel=ALIGNMENT_OPTIONS,
        ),
    ] = [False],
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
    ] = [None],
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
    # Gtf options
    gtf_display_mode: Annotated[
        List[GtfDisplayModeOption],
        typer.Option(
            help="Parameter to display mode for gtf tracks.",
            rich_help_panel=GTF_OPTIONS,
        ),
    ] = [GtfDisplayModeOption.COLLAPSED],
):
    """
    Generate an IGV session XML file.

    To add multiple input files/tracks to the IGV session:
    * Use the --file option multiple times.
    * The --name and --height parameters needs to be used the same number of times, if provided.
    * The alignment specific options e.g. --bam_group_by and --bam_color_by need to be used either once or the same number of times as the provided number of alignment files. Same for the other track types.

    Examples:

    # Generate an IGV session for a single file
    sessionizer generate --file test.bam
    """
    # If generate_symlinks is True, create symlinks to the input files
    if generate_symlinks:
        # Raise error if output is not given
        if not output:
            raise ValueError("Output needs to be given if generate_symlinks is True")

        # Generate symlinks
        igv_shortcut_dir = output.parent / "igv_shortcuts"
        igv_shortcut_dir.mkdir(parents=True, exist_ok=True)
        file = [generate_symlink(igv_shortcut_dir, file) for file in file]

        if genome_path:
            genome_path = generate_symlink(igv_shortcut_dir, genome_path)

    # If use_relative_paths is True, create paths to the input files relative to the output file
    if use_relative_paths:
        # Raise error if output is not given
        if not output:
            raise ValueError("Output needs to be given if use_relative_paths is True")

        file = [Path(f).relative_to(output.parent.absolute(), walk_up=True) for f in file]

        if genome_path:
            genome_path = Path(genome_path).relative_to(output.parent.absolute(), walk_up=True)

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
        bam_hide_small_indels=bam_hide_small_indels,
        bam_small_indel_threshold=bam_small_indel_threshold,
        bam_quick_consensus_mode=bam_quick_consensus_mode,
        bam_show_coverage=bam_show_coverage,
        bam_show_junctions=bam_show_junctions,
        bw_ranges=bw_ranges,
        bw_color=bw_color,
        bw_negative_color=bw_negative_color,
        bw_plot_type=bw_plot_type,
        vcf_show_genotypes=vcf_show_genotypes,
        gtf_display_mode=gtf_display_mode,
    )

    # Write XML to standard output
    if not output:
        print(xml_str)
    else:
        with open(output, "w", encoding="utf-8") as f:
            f.write(xml_str)


if __name__ == "__main__":
    app()
