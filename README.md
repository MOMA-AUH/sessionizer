# ✨ sessionizer ✨

Your new favorite tool for creating XML session files for IGV. 

# Usage
```bash
$ sessionizer --help
  Usage: sessionizer [OPTIONS]

 Generate an IGV session XML file.
 To add multiple input files/tracks to the IGV session:
 * Use the --file option multiple times.
 * The --name and --height parameters needs to be used the same number of times, if provided.
 * The alignment specific options e.g. --bam_group_by and --bam_color_by need to be used either once or the same number of times as the provided number of alignment files. Same for
 the other track types.

 Examples:

 # Generate an IGV session for a single file
 sessionizer generate --file test.bam

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --file                      PATH                             Input file (can be used multiple times) [default: None] [required]                                                │
│    --output                    PATH                             Output XML session file. If not specified, session will be printed to stdout. [default: None]                     │
│    --install-completion        [bash|zsh|fish|powershell|pwsh]  Install completion for the specified shell. [default: None]                                                       │
│    --show-completion           [bash|zsh|fish|powershell|pwsh]  Show completion for the specified shell, to copy it or customize the installation. [default: None]                │
│    --help                                                       Show this message and exit.                                                                                       │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Genome options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --genome             [hg19|hg38|t2t|custom]  Genome track options [default: hg38]                                                                                                 │
│ --genome-path        PATH                    Path to custom genome FASTA file [default: None]                                                                                     │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Input files options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --use-relative-paths    --no-use-relative-paths      Use relative paths for input files [default: no-use-relative-paths]                                                          │
│ --generate-symlinks     --no-generate-symlinks       Generate symlinks to input files [default: no-generate-symlinks]                                                             │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Track options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --name          TEXT     Name shown in IGV for input file (can be used multiple times) [default: None]                                                                            │
│ --height        INTEGER  Height of track in IGV (can be used multiple times) [default: None]                                                                                      │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Alignment options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --bam-group-by                                     [strand|sample|read_group|library|first_of_pair|pair_orientat  Parameter to group bams by. [default: none]                     │
│                                                    ion|mate_chromosome|chimeric|supplementary|base_at_position|i                                                                  │
│                                                    nsertion_at_position|movie|ZMW|haplotype|read_order|linked|ph                                                                  │
│                                                    ase|reference_concordance|mapping_quality|none]                                                                                │
│ --bam-color-by                                     [none|meth|insert_size|read_strand|first_of_pair_strand|pair_  Parameter to color bams by. [default: none]                     │
│                                                    orientation|read_order|sample|read_group|library|movie|zmw|bi                                                                  │
│                                                    sulfite|nomeseq|tag|unexpected_pair|mapped_size|link_strand|y                                                                  │
│                                                    c_tag|base_modification|base_modification_2color|smrt_subread                                                                  │
│                                                    _ipd|smrt_subread_pw|smrt_ccs_fwd_ipd|smrt_ccs_fwd_pw|smrt_cc                                                                  │
│                                                    s_rev_ipd|smrt_ccs_rev_pw]                                                                                                     │
│ --bam-display-mode                                 [expanded|collapsed|squished]                                  Parameter to display mode for bams. [default: collapsed]        │
│ --bam-show-coverage     --no-bam-show-coverage                                                                    Parameter to show coverage on bams. [default: False]            │
│ --bam-show-junctions    --no-bam-show-junctions                                                                   Parameter to show junctions on bams. [default: False]           │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ BigWig options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --bw-ranges                BW_RANGE_PARSER                                                             Parameter to set bw ranges [default: None]                                 │
│ --bw-color                 [black|white|red|lime|blue|yellow|cyan|magenta|silver|gray|maroon|olive|gr  Parameter to set bw color [default: none]                                  │
│                            een|purple|teal|navy|none]                                                                                                                             │
│ --bw-negative-color        [black|white|red|lime|blue|yellow|cyan|magenta|silver|gray|maroon|olive|gr  Parameter to set bw negative color [default: none]                         │
│                            een|purple|teal|navy|none]                                                                                                                             │
│ --bw-plot-type             [line|scatter|heatmap|bar|none]                                             Parameter to set bw plot type [default: bar]                               │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Variant options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --vcf-show-genotypes    --no-vcf-show-genotypes      Parameter to show genotypes on vcf tracks. [default: False]                                                                  │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

# How to install
The package can be installed using conda from a local build directory:

```bash
conda install -c file:///path/to/build sessionizer
```

To a new conda environment:

```bash
conda create -n sessionizer -c file:///path/to/build sessionizer
```

## Local build
The `build_local.sh` and `build_from_git.sh` scripts in `build` can be used to build the package. The scripts utilize the `conda build` command to build the package from a meta.yaml file.
