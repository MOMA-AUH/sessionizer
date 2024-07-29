from enum import Enum


class GENOME(str, Enum):
    HG19 = "hg19"
    HG38 = "hg38"
    T2T = "t2t"
    CUSTOM = "custom"

    def get_igv_name(self) -> str:
        genome_mapping = {
            GENOME.HG19: "hg19",
            GENOME.HG38: "hg38",
            GENOME.T2T: "chm13v2.0",
            GENOME.CUSTOM: "custom",
        }

        if self not in genome_mapping:
            raise ValueError(f"Genome {self} is not valid.")

        return genome_mapping[self]

    def __str__(self):
        return self.value
