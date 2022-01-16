# Booky
A command line utility for bookmarking files for quick access
    
With it you can:
- Bookmark and delete your (registers of) files at demand
- Launch them and use them in pipes like regular files!
    > ```booky booky_source -o | code - ```
- Cat them
- Move their file locations 

Basically, Booky has the following "modes"(?):
- SELECT - selects a file! (it's the default arg!)
- ADD - adds selected file to environment
- DEL - deletes file from environment
- ENV - environment (base json file) for bookmarked files (-e (something))
- OUT - echo selected file to stdout
- LIST - lists every "alias" (bookmark)