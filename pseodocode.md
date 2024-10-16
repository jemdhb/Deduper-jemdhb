# Psedocode

Write up a strategy for writing a Reference Based PCR Duplicate Removal tool. That is, given a sam file of uniquely mapped reads, remove all PCR duplicates (retain only a single copy of each read). Develop a strategy that avoids loading everything into memory. You should not write any code for this portion of the assignment. Be sure to:

## Define the problem

We are trying to remove PCR duplicates from our sam files. PCR duplicates obscure the actual sequencing data

## Possible cases:

- Case 1 **Duplicate**: Two reads have the same chromosome, same starting position (after softclipping adjustment), same strand, and the same UMI.
    - Read length, content, and quality are not checked.
- Case 2 **Not a duplicate**: Two reads are the same, expect their chromosomes are different
    - This case is handled by my sorting method which groups reads by chromosome and umi. So, reads with different UMIS would be in different bins.

- Case 3 **Not a duplicate**: Two reads are the same, but they are on different strands
    - This case if handled by my code logic, because reads are checked against a set that only contains reads from the + or - strand. So both reads would be unique for their set.

-  Case 4 **Not a duplicate**: Two reads are the same, but they have different positions (after soft clipping adjustment).
    - This case if handled by my code logic, because the final duplication check is by position, and reads at different positions are treated separately.

- Case 5 **Not a duplicate**: Two reads are the same, but they have a different UMI
    - This case is handled by my sorting method which groups reads by chromosome and UMIS. So, reads with different UMIS would be in different bins from the start.

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

driver function(input_file, header_file, umi_file):
    chrom=""
    UMI=""
    plus_position_set=()
    minus_position_set=()
    output_file=open(output.sam)
    #write header right away because its unchanged
    output_file.write(open(header_file).read())
    #set of all UMIS provided
    all_umis=set(open(umi_file).read().split("\t"))
    #read through input_file
    for line in input_file:
        curr_chrom, curr_UMI= get_umi_and_chrom(line)

        #if unknown UMI, trash
        if curr_UMI not in all_umis:
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

        #if we have to handle soft clipping    
        if S in start of cigar_string:
            adjusted_position=fix_softclipping(line)
        #otherwise can use og position
        else:
            adjusted_position=line.split()[4]
        
        #get what strand we are on
        pos_strand=determine_strand(line)

        #check existance of this position in the set, only by strand
        #+
        if pos_strand:
            #if a new read
            if adjusted_position not in plus_position_set:
                #add to set
                plus_position_set.insert(adjusted_position)
                #write to file
                output_file.write(line)
            else:
                #discard read, its a dupe
                pass
        #-
        else:
            #if a new read
            if adjusted_position not in minus_position_set:
                #add to set
                minus_position_set.insert(adjusted_position)
                #write to line
                output_file.write(line)
            else:
                #discard read, its a dupe   
                pass
```


```bash
def get_umi_and_chrom(line):

def fix_softclipping(line):

def determine_strand(line):



```