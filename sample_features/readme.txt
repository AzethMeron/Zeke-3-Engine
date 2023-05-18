Move those files to ".features" directory within main directory (the directory with "executable_main.py") 
If ".features" doesn't exist, create it.

Zeke automatically imports all .py filles from ".features" (and similarly from "engine") as if they were in main directory, so do not use overlapping names.
You can comment out file by using leading comma. 
So "levels.py" is active, ".levels.py" is commented out.