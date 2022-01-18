# Booky
A command line utility for bookmarking files for quick access
    
With it you can:
- Bookmark and delete your (aliases of) files at demand
- Launch them and use them in pipes like regular files!
    > ```booky booky_source -o | code - ```
- Cat them
- Move their file locations 

Basically, Booky has the following options:
```
  -e ENV, --env ENV     Environment that will be used for the bookmarks
  -a ALIAS, --add ALIAS, --alias ALIAS
                        Bookmarks new file or updates existing one
  -r, --remove          Remove a bookmarked file under current environment
  -o, --output          Show file/dir output (cat file or list dir)
  -p, --path            Show current file/alias'es path
  -l, --list, --list-env
                        Lists every alias in current environment
```                     
(yes, i did just copy the "-h" arg, its a great description imo!)

## Notes
This application was just made for fun, most likely it won't be the most optimized 
or even the best thing you could use, I made it for fun, if it actually helps you,
that's great!

- Please report issues whenever this app breaks! I'll try to fix them ASAP
