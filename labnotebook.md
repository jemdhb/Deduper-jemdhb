## Step 1: Thinking

We decided to sort our sam file by chr then umi before our python script begins

```bash
cat test.sam | grep -v "@" | sort -t ':'  -k 8 | sort -k 3 -s
```

After much thinking, I came up with this highlevel workflow to run
![h](highlevel_pseudocode.png)

