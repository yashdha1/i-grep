# Igrep 
## Provides pattern and semantic search functionality in a single Place. 
> light weight
>     ~100mb tess_fast model
>     ~90mb mini model


NOTE : supports only shell and wsl right now.

1. setup command
```shell
    chmod +x setup_igrep.sh
    ./setup_igrep.sh
```

2. commands intro using : *if bundle succesful*
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

3. else look into 

```shell
    uv run main.py --help
```



##### tradeoffs 
1. accuracy vs fast -> tessaract vs tess_fast.
2. tested it for ~2.5k images takes ~5-7mins
3. instant search results.
4. Manual testing accuracy shows promising results.

TODO : 
1. bundelling
2. optimisations
