"""



http://www.acgt.me/blog/2014/12/16/understanding-mapq-scores-in-sam-files-does-37-42

http://biofinysics.blogspot.fr/2014/05/how-does-bowtie2-assign-mapq-scores.html


https://gitlab.univ-nantes.fr/a-slide/ContaVect/blob/9a411abfa720064c205c5f6c811afdfea206ed12/pyDNA/pySamTools/Bam.py

pysamtools
"""

from collections import deque
import pandas as pd
import pylab
import pysam

# pysam uses htlib behing the scene and is very fast
# pysam works great for BAM file but with SAM, it needs to read the file after
# each compete iteration, which is not very useful


class BAM(pysam.AlignmentFile):
    """

    mode rb for bam files

    """
    def __init__(self, filename, mode="rb", *args):
        super(BAM, self).__init__(filename, mode, *args)

    def get_read_names(self):
        self.reset()
        names = [this.qname for this in self]
        self.reset()
        return names

    def iter_unmapped_reads(self):
        self.reset()
        unmapped = (this.qname for this in self if this.is_unmapped)
        self.reset()
        return unmapped

    def iter_mapped_reads(self):
        self.reset()
        mapped = (this.qname for this in self if this.is_unmapped is False)
        self.reset()
        return mapped

    def __len__(self):
        self.reset()
        N = len([x for x in self])
        self.reset()
        return N

    def get_stats(self):
        d = {}
        d['total_reads'] = len(list(self.iter_unmapped_reads()))
        d['mapped_reads'] = len(list(self.iter_mapped_reads()))
        d['unmapped_reads'] = len(list(self.iter_unmapped_reads()))
        d['contamination [%]'] = float(d['mapped_reads']) /float(d['unmapped_reads']) 
        d['contamination [%]'] *= 100
        return d


class SAM(pysam.AlignmentFile):
    """

    Header of a SAM file has N lines starting with '@' character.
    Using comment='@' and header None does not make the job.Using skiprows=N
    works but requires to know the number of lines in the header.


    .. todo:: read by chunk size for large files ?
    .. todo:: read two files for comparison ?


    FLAGS SAM format::

        1        0x1     template having multiple segments in sequencing
        2        0x2     each segment properly aligned according to the aligner
        4        0x4     segment unmapped
        8        0x8     next segment in the template unmapped
        16      0x10     SEQ being reverse complemented
        32      0x20     SEQ of the next segment in the template being reverse complemented
        64      0x40     the first segment in the template
        128      0x80    the last segment in the template
        256     0x100    secondary alignment
        512     0x200    not passing filters, such as platform/vendor quality controls
        1024     0x400   PCR or optical duplicate
        2048     0x800   supplementary alignme



    """
    def __init__(self, filename, *args):
        super(SAM, self).__init__(filename, "r", *args)
        self.skiprows = self._guess_header_length()

    def _guess_header_length(self):
        with open(self.filename, 'r') as fin:
            skiprows = 0
            while True:
                line = fin.readline()
                if line.startswith('@'):
                    skiprows += 1
                else:
                    break
        return skiprows

    def get_read_names(self):
        return self._get_column(0)

    def _get_column(self, col):
        data = []
        with open(self.filename, "r") as fin:
            for header in range(self.skiprows):
                fin.readline()

            for line in fin:
                data.append(line.split()[col])
        return data

    def plot_mapq_distribution(self):
        """Plot distribution of MAPQ scores (fifth column of SAM)


        The maximum MAPQ value that Bowtie 2 generates is 42 (though it doesn't
        say this anywhere in the documentation). In contrast, the maximum MAPQ
        value that BWA will generate is 37 (though once again, you -
        frustratingly - won't find this information in the manual).

        :reference: http://www.acgt.me/blog/2014/12/16/understanding-mapq-scores-in-sam-files-does-37-42
        """
        pylab.clf()
        data = [float(x) for x in self._get_column(3)]
        pylab.hist(data, bins=100, normed=True)
        pylab.grid(True)
        pylab.xlabel('MAPQ score')
        pylab.ylabel('Fraction of reads')





