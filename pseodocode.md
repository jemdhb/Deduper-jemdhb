# Psedocode

Write up a strategy for writing a Reference Based PCR Duplicate Removal tool. That is, given a sam file of uniquely mapped reads, remove all PCR duplicates (retain only a single copy of each read). Develop a strategy that avoids loading everything into memory. You should not write any code for this portion of the assignment. Be sure to:

## Define the problem

We are trying to remove PCR duplicates from our sam files. PCR duplicates obscure the actual sequencing data

## Write examples:

Include a properly formatted input sam file (an example sam file is included in the repo for your reference)
Include a properly formatted expected output sam file
Cover several different cases of things that are and are not PCR duplicates
It may be helpful to create a "unit test folder", that contains it's own readme.md describing the test cases in your unit test samfile
Develop your algorithm using pseudocode
Determine high level functions
Description
Function headers
Test examples (for individual functions)
Return statement
For this portion of the assignment, you should design your algorithm for single-end data, with 96 known UMIs. A list of UMIs can also be found in the repo. UMI information will be in the QNAME, like so: NS500451:154:HWKTMBGXX:1:11101:15364:1139:GAACAGGT. Discard any UMIs with errors (or error correct, if you're feeling ambitious).

```bash
cat test.sam | grep -v "@" | sort -t ':'  -k 8 | sort -k 3 -s
```

```bash
In bash, sort by chromosome-umi saving to sorted.sam

driver function():
    chrom=""
    UMI=""
    plus_position_set=()
    minus_position_set=()
    for line in sorted.sam:
        curr_chrom, curr_UMI= get_umi_and_chrom(line)
        if curr_UMI not known UMI:
            continue
        #if you have to update anything, clear the positions
        if curr_chrom!=chrom:
            chrom=curr_chrom
            plus_position_set=()
            minus_position_set=()
        if curr_UMI!=UMI:
            UMI=curr_UMI
            plus_position_set=()
            minus_position_set=()
        if S in start of cigar_string:
            adjusted_position=fix_softclipping(line)
        #can use og position
        else:
            adjusted_position=line.split()[4]
        pos_strand=determine_strand(line)
        if pos_strand:
            if adjusted_position not in plus_position_set:
                plus_position_set.insert(adjusted_position)
                write line to file
            else:
                #discard read, its a dupe
        else:
            if adjusted_position not in minus_position_set:
                minus_position_set.insert(adjusted_position)
                write line to file
            else:
                #discard read, its a dupe   
```


```bash
def get_umi_and_chrom(line):

def fix_softclipping(line):

def determine_strand(line):



```