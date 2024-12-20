## Step 1: Thinking

Before writing my pseudocode, I wanted to figure out how my input sam file would be sorted.

## Dual sort

We decided to sort our sam file by chromosome and then UMI before our Python
script begins. To keep everything in one file we had to use bash sort vs. samtools sort.

```bash
cat test.sam | grep -v "@" | sort -t ':'  -k 8 | sort -k 3 -s
```

### No samtools? :cold_sweat:

If this sorting method is too slow, my plan is to use samtools split to split
the files by chromosome. I would then call the second sorting command from above
on each split file.

This makes the Python code much easier to write. Also this high level of sorting
will improve the speed of my python code

## High-level Python code

After much thinking, I came up with this highlevel workflow to run
![h](image.png)

This is the overall flow of my logic, which only ended up getting slightly
altered once I created my more formal pseudocode. 

## Detailed pseudocode

The primary difference in this code, is my code is ordered in partitions, but I
am going line-by-line and checking partition-specific information (strand, position)
with booleans. This will save me a lot of memory in the real files.

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

## Actual Code

### Abandoning the double sort

This above solution is very elegant but hinges upon the previous bash sorting to do so :arrow_right: after listening to lecture decided only sorting by chromosome is much easier

The primary change is now our two sets will contain tuples with two items `(position, umi)`. This will not cause a large issue with memory

### Writing the softclipping function

This was the section of my code that I had to adjust the most from my pseudocode.

#### Plus strand

##### Before

```bash
#plus strand with left softclipping
if plus_strand and cigar_string.split('S')[0].isdigit():
        left_clip=int(cigar_string.split("S")[0])
        #NO -1 needed
        return start_position-left_clip
#minus strand
else:
    return fix_minus_softclipping(cigar_string, start_position)           
```

This placed all plus strand reads with no S into my minus strand function, which produced weird results.

##### After

```bash
#plus strand with left softclipping
if plus_strand and cigar_string.split('S')[0].isdigit():
        left_clip=int(cigar_string.split("S")[0])
        #NO -1 needed
        return start_position-left_clip
#plus strand with no clipping do nothing
elif plus_strand:
    return start_position
#minus strand
else:
    return fix_minus_softclipping(cigar_string, start_position)  
```


#### Minus strand

remove insertions
make regex
add -1

##### Using no regex

Going though the stand building the numbers and modifications as you go. Use a
dictionary to store what modifications are in our string. Iterate through the 
dictionary with case-statements to adjust the position

##### Using regex

```bash
matches = re.findall(r'(\d+)([A-Z]{1})', cigar_string)
```
Iterate over this list of tuples with case-statements to adjust the position.
I realized the regex solution was much cleaner and switched my code over to this

##### Over accounted for insertions

Compared with others and realized I over accounted for insertions I was adjusting
the position `+` for insertions when I should have been doing nothing.

### Other misc. errors

- Was using the wrong bit (4) instead of 16

- Type casting the chromosome to an int caused issues for the scaffolds at the
end of the large test file. Removing this was simple

### Other misc. additions

- Added in the statistics that are asked for in the survey. Some issues with
counter logic that were quickly resolved.