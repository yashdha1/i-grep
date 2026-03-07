
1. make sure you have the tessaract installed. locally. 
2. check with 

```shell
    tessaract --version
``` 

3. application setup and startup
```shell
    uv sync
    uv run main.py
```

```
    # pattern search
    igrep "pattern_search"           : normal 
    igrep -i "pattern_search"        : ignore casing
    igrep -c "pattern"               : count the occurences

    # semantics search :
    igrep -s "text"                  : semantic search default top_5 
    igrep -s "text" <topk>           : semantic search default top_k

    # sync the images
    igrep sync                       : sync the images present in the folder to have in the db

    # setup
    igrep setup                      : model installation and db setup  (hide all the ugly shit)
```
