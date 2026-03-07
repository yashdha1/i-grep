
1. make sure you have the tessaract installed. locally. 
2. check with 

```shell
    tessaract --version
``` 

3. application setup and startup
```shell
    uv sync
```

```shell
    # pattern search
    igrep "pattern_search"     # normal search
    igrep -i "pattern_search"  # ignore case (--ignore-case)
    igrep -c "pattern"         # count occurrences (--count)

    # semantic search
    igrep -s "text"            # semantic search, default top 5
    igrep -s "text" 10         # semantic search with top-k (e.g. 10)

    # sync the images
    igrep sync                 # sync images in the folder to the db

    # setup
    igrep setup                # model installation and db setup
```


tradeoffs 
1. accuracy vs fast -> tessaract vs tess_fast.
    1.1. tess_fast -> still preety good
    