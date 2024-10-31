#!/usr/bin/env python


def get_umi_and_chrom(line):
    """From one line in our sam file, extract the UMI and Chromosome
    """
    line_list=line.split("\t")
    umi=line_list[0].split(":")[-1].strip()
    chrom=int(line_list[2].strip())
    return umi, chrom

def fix_softclipping(cigar_string, start_position, plus_strand=True):
    """On a line determined to have leftmost softclipping, use the CIGAR string and
    softclipped starting position to extract the true start position of our read.
    """

    try:
        #no clipping, EASY
        if "S" not in cigar_string:
            return start_position
        #only have to care about left soft clipping, EASY
        elif plus_strand:
            left_clip=int(cigar_string.split("S")[0])
            return start_position-left_clip
        #minus strand HARD
        else:
            return fix_minus_softclipping(cigar_string, start_position)
           
    except:
        return start_position
        
def fix_minus_softclipping(cigar_string, start_position):
    #ensure there is right softclipping to resolve
    mod_list=[]
    num_list=[]
    num=""
    mod=""
    for char in cigar_string:
        try:
            #build int until we reach a string
            int(char)
            num+=char
        except:
            #once we reach a string ie a sam mod, update the lists
            mod=char
            mod_list.append(mod)
            num_list.append(int(num))

    first_item=True
    for index,item in enumerate(mod_list):
        match item:
            case "I":
                start_position=start_position-num_list[index]
            case "D":
                start_position=start_position+num_list[index]
            #idk
            case "N":
                start_position=start_position+num_list[index]
            case "S":
                if first_item:
                    first_item=False
                    continue
                start_position=start_position+num_list[index]
            #M
            case _:
                first_item=False
                start_position=start_position+num_list[index]
                continue
    return start_position

def determine_strand(bit_flag):
    """From a sam line, extract the bitscore and determine which strand our
    read lies on
    """
    print(bit_flag)
    if((bit_flag & 4) != 4):
            print("False")
            return False
    print("true")
    return True
    #True if positive, False if negative strand

def dedupe(input_file, umi_file):
    chrom=""
    input_file=open(input_file,"r")
    output_file=open("output.sam","w")
    #read in the set of provided UMIS
    all_umis=set(open(umi_file).read().split("\n"))
    plus_position_set=set()
    minus_position_set=set()
    #read through input_file
    for line in input_file:
        if line=="":
            break
        if "@" in line[0]:
            output_file.write(line)
            continue
        curr_bit_flag=int(line.split()[1])
        curr_cigar_string=line.split()[5]
        curr_start_position=line.split()[3]
        curr_UMI, curr_chrom = get_umi_and_chrom(line)
        plus_strand=determine_strand(curr_bit_flag)
        #if unknown UMI, trash
        if curr_UMI not in all_umis:
            continue
        #if you have to update anything, clear the positions
        if curr_chrom!=chrom:
            chrom=curr_chrom
            plus_position_set=set()
            minus_position_set=set()    
        #check existance of this position in the set, only by strand
        #+
        if plus_strand:
            adjusted_position=fix_softclipping(curr_cigar_string,line.split()[3])
            #if a new read
            #print((adjusted_position, curr_UMI))
            print(plus_position_set)
            if (adjusted_position, curr_UMI) not in plus_position_set:
                #add to set
                plus_position_set.add((adjusted_position,curr_UMI))
                #write to file
                output_file.write(line)
            else:
                #discard read, its a dupe
                continue
        #-
        else:
            adjusted_position=fix_softclipping(curr_cigar_string,curr_start_position,False)

            #print((adjusted_position, curr_UMI))
            print(minus_position_set)
            #if a new read
            if (adjusted_position, curr_UMI) not in minus_position_set:
                #add to set
                minus_position_set.add((adjusted_position,curr_UMI))
                #write to line
                output_file.write(line)
            else:
                #discard read, its a dupe   
                pass

dedupe("unit_tests/mini_test_input.sam","STL96.txt")


#N treat the same as a deletion mathematically