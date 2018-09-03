#!/usr/bin/python

## Written by Dr. Daniel Pass for IGEM-Cardiff 2018
## https://github.com/passdan

from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
import argparse
from Bio.Blast.Applications import NcbiblastnCommandline

if __name__ =='__main__':
    ## This defines the command line parameters and puts it into an array called args
    parser = argparse.ArgumentParser(description='Provide a region of DNA/RNA to be sliced to test for matches against a reference')
    parser.add_argument('-i', required=True, help='[REQUIRED] | DNA segment you want to slice for probes (FASTA FORMAT)')
    parser.add_argument('-d', required=True, help='[REQUIRED] | Blast database you want to search against (make sure it is discoverable or give full path)')
    parser.add_argument('-w', default=21, help='Window length of the probes you want to test | default = 21')
    parser.add_argument('-a', default=1, help='Number of cores you want to blast with | default = 1')

    args = parser.parse_args()

def main():
    ## If the input file is a fasta (It should be!) then do this to get the main part of the name for the outputs, otherwise use the whole filename
    if args.i.endswith('.fasta'):
        outputSlug = args.i[:-6]
    elif args.i.endswith('.fa'):
        outputSlug = args.i[:-3]
    else
        outputSlug = args.i

    ## Open the input fasta and read it in to memory
    with open(args.i, "rU") as handle:
        for siRNA in SeqIO.parse(handle, "fasta"):
            ## Run the slicing method to get an array of the X-length fragments
            probeArray = sliceProbe(siRNA)
            ## Some nice outputs and write it to a file
            print str(len(probeArray)) + " probes were generated"
            probesFile =  outputSlug + "-probes.fasta"
            SeqIO.write(probeArray, probesFile, "fasta")

    ## Run blast on all the probes generated
    blastn(probesFile, outputSlug)


def sliceProbe(siRNA):
    print "Reading siRNA and slicing it into windows of", args.w, "size"

    probes = []
    i = 0

    ## output the first 21 bases (or user specified) in fasta format (needed to go into blastn) then move one along base at a time, outputting each one
    while i <= len(siRNA.seq) - args.w:
        probeSeq = siRNA.seq[i:i+args.w]
        probes.append(SeqRecord(probeSeq, id=str(probeSeq), description=""))
        i += 1

    return probes

def blastn(probesFile, outputSlug):
    ## define the parameters
    print("blasting probe sequence " + probesFile + " against the " + args.d + " database with BLASTN-SHORT")

    blast_in = (probesFile)
    blast_out = (outputSlug + "-probes.blast")

    ## Define the command. NOTE: Running blastn-short!
    # OUTPUT COLUMNS ARE: query id, subject id, % identity, alignment length, mismatches, gap opens, q. start, q. end, s. start, s. end, evalue, bit score, sequence
    blastn_cline = NcbiblastnCommandline(task="blastn-short", query=blast_in, db=args.d, evalue=0.01, outfmt=6, out=blast_out, num_threads=args.a)

    stdout, stderr = blastn_cline()

    blast_err_log = open("blast_err.txt", "w")
    blast_stdout_log = open("blast_stdout.txt", "w")

    blast_err_log.write(stderr)
    blast_stdout_log.write(stdout)

    return blast_out

if __name__ == "__main__":
    main()
