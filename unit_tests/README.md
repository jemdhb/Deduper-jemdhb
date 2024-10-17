# Cases

Cases handled by my test file:

- Case 1, **duplicate**: Two reads have the same chromosome, same starting position (after softclipping adjustment), same strand, and the same UMI.
    - Read length, content, and quality are not checked.

- Case 2, **not a duplicate**: Two reads are the same, except their chromosomes are different.
    - This case is handled by the sorting method which groups reads by chromosome and UMI. So, reads with different chromosomes would be in different bins from the start (and thus be treated uniquely).

- Case 3, **not a duplicate**: Two reads are the same, but they are on different strands.
    - This case is handled by my code logic, because reads are checked against a set that only contains reads from the + or - strand. So, both reads would be unique for their set.

- Case 4, **not a duplicate**: Two reads are the same, but they have different positions (after soft clipping adjustment).
    - This case is handled by my code logic, because the final duplication check is by position, and reads at different positions are considered distinct.
    - I've included a softclipped example as well to ensure that that aspect of my code is being tested.

- Case 5, **not a duplicate**: Two reads are the same, but they have a different UMIs
    - This case is handled by my sorting method which groups reads by chromosome and UMIs. So similar to case 2, reads with different UMIS would be in different bins from the start.

From my `mini_test_input.sam` only C1 (the duplicate line) should be discarded
