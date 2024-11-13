#!/usr/bin/env python
import re
import argparse

def get_args():
    parser = argparse.ArgumentParser(description="Using an input sam and UMI file, remove PCR duplicates writing them to a new output sam file.")
    parser.add_argument("-f", "--input_file",
                     help="Path to input sam file.",
                     required=True, type=str)
    parser.add_argument("-o", "--output_file",
                     help="Path to output sam file with our PCR duplicates removed.",
                     required=True, type=str)
    parser.add_argument("-u", "--umi_file",
                     help="Path to file containing all possible valid UMIs.",
                     required=True, default="STL96.txt",type=str)
    return parser.parse_args()

def get_umi_and_chrom(line: str)->tuple:
    """From one line in our sam file, extract the UMI and Chromosome
    """
    #split line on tab
    line_list=line.split("\t")
    #on the first column grab the UMI by splitting on :
    umi=line_list[0].split(":")[-1].strip()
    #chrom is just chilling on column 2 DONT TYPECAST
    chrom=line_list[2].strip()
    return umi, chrom

def fix_softclipping(cigar_string:str, start_position:int, plus_strand=True)->int:
    """On a line determined to have leftmost softclipping, use the CIGAR string and
    softclipped starting position to extract the true start position of our read.

    Args:
        cigar_string (str): str of alignment operations to determine position
        start_position (int): int start position not encountering for a cigar str
        plus_strand (bool, optional): Determines which clipping function to use.

    Returns:
        int: _description_
    """
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
    
        

def fix_minus_softclipping(cigar_string:str, start_position:int)->int:
    """Fix softclipping on the minus strand

    Args:
        cigar_string (str): string to obtain our true position
        start_position (int): alignment start position before any adjustment

    Returns:
        int: our adjusted start position
    """
    #get cigar string formatted [(7,M),(21,S)]
    matches = re.findall(r'(\d+)([A-Z]{1})', cigar_string)
    first_item=True
    #go through cigar alterations
    for item in matches:
        alteration_type=item[1]
        position_change=int(item[0])
        match alteration_type:
            case "D":
                start_position+=position_change
            case "N":
                start_position+=position_change
            case "S":
                if not first_item:
                    start_position+=position_change
            #M/X/=
            case "M":
                start_position+=position_change
        if first_item:
                    first_item=False
        
    return start_position-1

def determine_strand(bit_flag:int)->bool:
    """From a sam line, extract the bitscore and determine which strand our
    read lies on
    """
    if((bit_flag & 16) != 16):
            return True
    return False
    #True if positive, False if negative strand

def dedupe(input_file, output_file, umi_file):
    """given and input and umi file, find and remove PCR duplicates

    Args:
        input_file (str): path to input file
        output_file (str): path to output file
        umi_file (str): path to UMI file
    """
    num_chrom=0
    wrong_UMIS=0
    header_lines=0
    num_dupes=0
    num_unique=0
    #so we dont print the first line as a new chromosome
    chrom="0"
    input_file=open(input_file,"r")
    output_file=open(output_file,"w")
    STATS_FILE=open(outfile[:outfile.rfind(".")]+"_stats.txt","w")

    #read in the set of provided UMIS
    all_umis=set(open(umi_file).read().split("\n"))
    plus_position_set=set()
    minus_position_set=set()

    #read through input_file
    for line in input_file:
        #EOF do nothing
        if line=="":
            break
        #header, write and continue
        if "@" in line[0]:
            header_lines+=1
            output_file.write(line)
            continue

        #get variables of interest 
        curr_bit_flag=int(line.split()[1])
        curr_cigar_string=line.split()[5]
        curr_start_position=int(line.split()[3])
        curr_UMI, curr_chrom = get_umi_and_chrom(line)
        plus_strand=determine_strand(curr_bit_flag)

        #if unknown UMI, trash
        if curr_UMI not in all_umis:
            wrong_UMIS+=1
            continue

        #if you have to update anything, clear the positions
        if curr_chrom!=chrom:
            #CHROMOSOME STRATS
            if chrom!="0":
                STATS_FILE.write(f"{chrom}\t{num_chrom}\n")
            num_chrom=0
            chrom=curr_chrom
            plus_position_set=set()
            minus_position_set=set()
    
        #check existance of this position in the set, only by strand
        #+
        if plus_strand:
            adjusted_position=fix_softclipping(curr_cigar_string,curr_start_position, True)
            #if a new read
            if (adjusted_position, curr_UMI) not in plus_position_set:
                num_chrom+=1
                #add to set
                plus_position_set.add((adjusted_position,curr_UMI))
                num_unique+=1
                #write to file
                output_file.write(line)
            else:
                num_dupes+=1
                #discard read, its a dupe
                continue
        #-
        else:
            adjusted_position=fix_softclipping(curr_cigar_string,curr_start_position,False)
            #if a new read
            if (adjusted_position, curr_UMI) not in minus_position_set:
                num_chrom+=1
                num_unique+=1
                #add to set
                minus_position_set.add((adjusted_position,curr_UMI))
                #write to line
                output_file.write(line)
            else:
                num_dupes+=1
                #discard read, its a dupe   
                pass
    #STATS
    STATS_FILE.write(f"{chrom}\t{num_chrom}\n")
    STATS_FILE.write(f"The number of header lines is: {header_lines}\n")
    STATS_FILE.write(f"The number of wrong UMIS is: {wrong_UMIS}\n")
    STATS_FILE.write(f"The number of unique reads is: {num_unique}\n")
    STATS_FILE.write(f"The number of dupe reads is: {num_dupes}\n")
    STATS_FILE.close()
    input_file.close()
    output_file.close()

args = get_args()
outfile=args.output_file
infile=args.input_file
umifile=args.umi_file
dedupe(infile, outfile, umifile)