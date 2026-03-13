# i-grep : cli based grep tool for images

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



TODO : 
1. igrep command shall work and added to the path.
2. optimisation -> lazy-loading in imports and sync speed up working and accuracy increase. 
3. butify the output and better res. 
4. uv tools