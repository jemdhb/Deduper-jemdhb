# Extra Credit

## jones_deduper.py

Handles UMI correction with the `-c` flag. Set `-c True` if UMI correction should be
performed. Default is `-c False` which performs deduping as-is. 

## jones_randomer.py

Handles randomer UMIS and a provided UMI file. No flag update for UMIS, `-u` 
has simply become optional with a default value of `None`. These options will
treat our UMIS as randomers. UMI correction can also be performed with this code using the `-c` flag. But no correction can be performed on randomers so these flags are 
essentially mutually exclusive.
- Randomers are required to have only `ATCG` nucleotides and to be the exact
length specified (default of 8). Randomer length can be specified with `-r 8`

## jones_deduper_choose_hq.py

Handles writing the best duplicate to the file. The best duplicate is selected based
on the average phred score of the read. The read with the higher phred score is 
retained. UMI correction can also be performed with this code using the `-c` flag.