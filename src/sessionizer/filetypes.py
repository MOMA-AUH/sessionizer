ALIGNMENT_SUFFIXES = [
    ".sam",
    ".bam",
    ".cram",
]

VCF_SUFFIXES = [
    ".vcf",
    ".vcf.gz",
]

BIGWIG_SUFFIXES = [
    ".bw",
    ".bigwig",
    ".wig",
]

GTF_SUFFIXES = [
    ".gtf",
    ".gtf.gz",
]

FILE_INDEX_EXTENSIONS = {
    ".bam": ".bai",
    ".cram": ".crai",
    ".vcf": ".tbi",
    ".vcf.gz": ".tbi",
    ".fasta": ".fai",
    ".FASTA": ".fai",
    ".bed": ".tbi",
    ".bed.gz": ".tbi",
}
