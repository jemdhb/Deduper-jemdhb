# Cases

Cases handled by my test file:
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

From my `mini_test_input.sam` only C1 (the duplicate line) should be discarded
