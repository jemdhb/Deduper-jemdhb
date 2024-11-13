#!/usr/bin/env python
import re
import argparse

def get_args():
    parser = argparse.ArgumentParser(description="Using an input sam and UMI file, remove PCR duplicates writing them to a new output sam file.")
    parser.add_argument("-i", "--input_file",
                     help="Path to input sam file.",
                     required=True, type=str)
    parser.add_argument("-o", "--output_file",
                     help="Path to output sam file with our PCR duplicates removed.",
                     required=True, type=str)
    parser.add_argument("-u", "--umi_file",
                     help="Path to file containing all possible valid UMIs.",
                     required=True, default="STL96.txt",type=str)
    parser.add_argument("-c","--correction",help="perform umi correction",type=bool)
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
        int: return adjusted position
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

def dedupe(input_file, output_file, umi_file, umi_correction=False):
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

    #new stats for fixing bad umis
    number_of_umis_corrected=0
    number_of_umis_uncorrected=0


    #so we dont print the first line as a new chromosome
    chrom="0"
    input_file=open(input_file,"r")
    output_file=open(output_file,"w")
    STATS_FILE=open(outfile[:outfile.rfind(".")]+"_stats.txt","w")

    #read in the set of provided UMIS
    all_umis=set(open(umi_file).read().split("\n"))
    #plus_position_set=set()
    plus_position_dict={}
    #minus_position_set=set()
    minus_position_dict={}

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
        curr_qs= qual_score(line.split()[10])
        plus_strand=determine_strand(curr_bit_flag)

        #if unknown UMI, trash
        if curr_UMI not in all_umis:
            wrong_UMIS+=1
            if umi_correction:
                 corrected_umi=UMI_correction(curr_UMI,all_umis)
                 if corrected_umi==-1:
                      #no good correction
                      number_of_umis_uncorrected+=1
                      continue
                 else:
                      number_of_umis_corrected+=1
                      curr_UMI=corrected_umi
            #were not correcting UMIS, discard
            else:
                 continue

        #if you have to update anything, clear the positions
        if curr_chrom!=chrom:
            #CHROMOSOME STRATS
            if chrom!="0":
                STATS_FILE.write(f"{chrom}\t{num_chrom}\n")
            num_chrom=0
            chrom=curr_chrom
            for item in plus_position_dict.values():
                 output_file.write(item[1])
            plus_position_dict={}
            for item in minus_position_dict.values():
                 output_file.write(item[1])
            minus_position_dict={}
    
        #check existance of this position in the set, only by strand
        #+
        
        if plus_strand:
            adjusted_position=fix_softclipping(curr_cigar_string,curr_start_position, True)
            key=(adjusted_position, curr_UMI)
            #if a new read 
            if key not in plus_position_dict.keys():
                num_chrom+=1
                #add to dict
                plus_position_dict[key]=(curr_qs,line)
                num_unique+=1
            #if this read is hq than the old one
            elif key in plus_position_dict.keys() and plus_position_dict[key][0]<curr_qs:
                plus_position_dict[key]=(curr_qs,line)
                num_dupes+=1
            else:
                num_dupes+=1
                #discard read, its a dupe
                continue
        #-
        else:
            adjusted_position=fix_softclipping(curr_cigar_string,curr_start_position,False)
            key=(adjusted_position, curr_UMI)
            #if a new read
            if key not in minus_position_dict.keys():
                num_chrom+=1
                num_unique+=1
                #add to set
                minus_position_dict[key]=(curr_qs,line)
            #if read is hq than the previous
            elif key in minus_position_dict.keys() and minus_position_dict[key][0]<curr_qs:
                minus_position_dict[key]=(curr_qs,line)
                num_dupes+=1
        
            else:
                num_dupes+=1
                #discard read, its a dupe   
                continue
    #STATS
    STATS_FILE.write(f"{chrom}\t{num_chrom}\n")
    for item in plus_position_dict.values():
            output_file.write(item[1])
    for item in minus_position_dict.values():
            output_file.write(item[1])
    STATS_FILE.write(f"The number of header lines is: {header_lines}\n")
    STATS_FILE.write(f"The number of wrong UMIS is: {wrong_UMIS}\n")
    STATS_FILE.write(f"The number of unique reads is: {num_unique}\n")
    STATS_FILE.write(f"The number of dupe reads is: {num_dupes}\n")
    if umi_correction:
        STATS_FILE.write(f"Extra Credit: UMI Correction\nThe number of UMI corrected reads is: {number_of_umis_corrected}\n")
        STATS_FILE.write(f"The number unknown UMIS that could not be corrected is: {number_of_umis_uncorrected}\n")


    STATS_FILE.close()
    input_file.close()
    output_file.close()

def UMI_correction(UMI,ALL_UMIS):
    """correct unknown UMIS according to the lowest hamming distance. If there are
    multiple best hits, return -1 because we are not confident which UMI to correct to

    Args:
        UMI (str): unknown umi to correct

    Returns:
        variable: return a corrected UMI if successful, -1 if not 
    """
    best_umi=""
    #chose some long 
    best_ham_score=len(UMI)
    unique_match=True
    for known_umi in ALL_UMIS:
        if known_umi=="": continue
        current_ham_score=sum(c1 != c2 for c1, c2 in zip(known_umi, UMI))
        if current_ham_score==best_ham_score:
             unique_match=False
             best_umi=known_umi
             best_ham_score=current_ham_score
        elif current_ham_score < best_ham_score:
             unique_match=True
             best_umi=known_umi
             best_ham_score=current_ham_score
        else:
             pass
    if unique_match:
        return best_umi
    return -1
             
#FROM BIOINFO.PY
def convert_phred(letter: str) -> int:
    '''Converts a single character into a phred score'''
    return ord(letter)-33
def qual_score(phred_score: str) -> float:
    """Convert a phred33 encoded string to a list of quality values 
    then compute the average of those values"""
    scores=[]
    for item in phred_score:
        scores.append(convert_phred(item))
    return sum(scores)/len(scores)

args = get_args()
outfile=args.output_file
infile=args.input_file
umifile=args.umi_file
correction=args.correction

dedupe(infile, outfile, umifile, umi_correction=correction)


#N treat the same as a deletion mathematically