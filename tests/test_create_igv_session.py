import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

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


class TestCreateIgvSession(unittest.TestCase):
    def setUp(self):
        # Set up temporary directories and files for testing
        self.temp_dir = TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

        self.input_dir = self.test_dir / "input"
        self.input_dir.mkdir()

        # Input files
        self.input_bam = self.input_dir / "input.bam"
        self.input_vcf_gz = self.input_dir / "input.vcf.gz"
        self.input_gtf_gz = self.input_dir / "input.gtf.gz"

        for f in [self.input_bam, self.input_vcf_gz]:
            f.touch()

    def test_attribute_handling(self):
        # Assert that simple call runs without errors
        self.assertRaises(
            ValueError,
            generate_igv_session,
            # Relevant arguments
            files=[self.input_bam],
            bam_group_by=[],
            # Other arguments
            names=[],
            heights=[],
            genome=GENOME.HG38,
            genome_path="",
            bam_color_by=[AllignmentColorByOption.NONE],
            bam_display_mode=[AllignmentDisplayModeOption.COLLAPSED],
            bam_hide_small_indels=[False],
            bam_small_indel_threshold=[0],
            bam_quick_consensus_mode=[False],
            bam_show_coverage=[False],
            bam_show_junctions=[False],
            bw_ranges=[BigWigRangeOption(minimum=0.0, baseline=0.0, maximum=0.0)],
            bw_color=[RGBColorOption.NONE],
            bw_negative_color=[RGBColorOption.NONE],
            bw_plot_type=[BigWigPlotTypeOption.NONE],
            bw_auto_scale=[False],
            vcf_show_genotypes=[False],
            vcf_feature_visibility_window=[0],
            gtf_display_mode=[GtfDisplayModeOption.COLLAPSED],
        )

        self.assertRaises(
            ValueError,
            generate_igv_session,
            # Relevant arguments
            files=[self.input_bam],
            bam_group_by=[AllignmentGroupByOption.NONE, AllignmentGroupByOption.NONE],
            # Other arguments
            names=[],
            heights=[],
            genome=GENOME.HG38,
            genome_path="",
            bam_color_by=[AllignmentColorByOption.NONE],
            bam_display_mode=[AllignmentDisplayModeOption.COLLAPSED],
            bam_hide_small_indels=[False],
            bam_small_indel_threshold=[0],
            bam_quick_consensus_mode=[False],
            bam_show_coverage=[False],
            bam_show_junctions=[False],
            bw_ranges=[BigWigRangeOption(minimum=0.0, baseline=0.0, maximum=0.0)],
            bw_color=[RGBColorOption.NONE],
            bw_negative_color=[RGBColorOption.NONE],
            bw_plot_type=[BigWigPlotTypeOption.NONE],
            bw_auto_scale=[False],
            vcf_show_genotypes=[False],
            vcf_feature_visibility_window=[0],
            gtf_display_mode=[GtfDisplayModeOption.COLLAPSED],
        )

        self.assertRaises(
            ValueError,
            generate_igv_session,
            # Relevant arguments
            files=[self.input_vcf_gz],
            vcf_show_genotypes=[],
            vcf_feature_visibility_window=[],
            # Other arguments
            names=[],
            heights=[],
            genome=GENOME.HG38,
            genome_path="",
            bam_color_by=[AllignmentColorByOption.NONE],
            bam_display_mode=[AllignmentDisplayModeOption.COLLAPSED],
            bam_group_by=[AllignmentGroupByOption.NONE],
            bam_hide_small_indels=[False],
            bam_small_indel_threshold=[0],
            bam_quick_consensus_mode=[False],
            bam_show_coverage=[False],
            bam_show_junctions=[False],
            bw_ranges=[BigWigRangeOption(minimum=0.0, baseline=0.0, maximum=0.0)],
            bw_color=[RGBColorOption.NONE],
            bw_negative_color=[RGBColorOption.NONE],
            bw_plot_type=[BigWigPlotTypeOption.NONE],
            bw_auto_scale=[False],
            gtf_display_mode=[GtfDisplayModeOption.COLLAPSED],
        )

        self.assertRaises(
            ValueError,
            generate_igv_session,
            # Relevant arguments
            files=[self.input_vcf_gz],
            vcf_show_genotypes=[False, False],
            vcf_feature_visibility_window=[10, 1000],
            # Other arguments
            names=[],
            heights=[],
            genome=GENOME.HG38,
            genome_path="",
            bam_color_by=[AllignmentColorByOption.NONE],
            bam_display_mode=[AllignmentDisplayModeOption.COLLAPSED],
            bam_group_by=[False],
            bam_hide_small_indels=[False],
            bam_small_indel_threshold=[0],
            bam_quick_consensus_mode=[False],
            bam_show_coverage=[False],
            bam_show_junctions=[False],
            bw_ranges=[BigWigRangeOption(minimum=0.0, baseline=0.0, maximum=0.0)],
            bw_color=[RGBColorOption.NONE],
            bw_negative_color=[RGBColorOption.NONE],
            bw_plot_type=[BigWigPlotTypeOption.NONE],
            bw_auto_scale=[False],
            gtf_display_mode=[GtfDisplayModeOption.COLLAPSED],
        )

        self.assertRaises(
            ValueError,
            generate_igv_session,
            # Relevant arguments
            files=[self.input_gtf_gz],
            gtf_display_mode=[],
            # Other arguments
            names=[],
            heights=[],
            genome=GENOME.HG38,
            genome_path="",
            bam_color_by=[AllignmentColorByOption.NONE],
            bam_display_mode=[AllignmentDisplayModeOption.COLLAPSED],
            bam_group_by=[False],
            bam_hide_small_indels=[False],
            bam_small_indel_threshold=[0],
            bam_quick_consensus_mode=[False],
            bam_show_coverage=[False],
            bam_show_junctions=[False],
            bw_ranges=[BigWigRangeOption(minimum=0.0, baseline=0.0, maximum=0.0)],
            bw_color=[RGBColorOption.NONE],
            bw_negative_color=[RGBColorOption.NONE],
            bw_plot_type=[BigWigPlotTypeOption.NONE],
            bw_auto_scale=[False],
            vcf_show_genotypes=[False],
            vcf_feature_visibility_window=[10],
        )

        self.assertRaises(
            ValueError,
            generate_igv_session,
            # Relevant arguments
            files=[self.input_gtf_gz],
            gtf_display_mode=[GtfDisplayModeOption.COLLAPSED, GtfDisplayModeOption.COLLAPSED],
            # Other arguments
            names=[],
            heights=[],
            genome=GENOME.HG38,
            genome_path="",
            bam_color_by=[AllignmentColorByOption.NONE],
            bam_display_mode=[AllignmentDisplayModeOption.COLLAPSED],
            bam_group_by=[False],
            bam_hide_small_indels=[False],
            bam_small_indel_threshold=[0],
            bam_quick_consensus_mode=[False],
            bam_show_coverage=[False],
            bam_show_junctions=[False],
            bw_ranges=[BigWigRangeOption(minimum=0.0, baseline=0.0, maximum=0.0)],
            bw_color=[RGBColorOption.NONE],
            bw_negative_color=[RGBColorOption.NONE],
            bw_plot_type=[BigWigPlotTypeOption.NONE],
            bw_auto_scale=[False],
            vcf_show_genotypes=[False],
            vcf_feature_visibility_window=[1000],
        )
