# emClarity_setup.py
Simple user-friendly script for setting up an emClarity project from a set of IMOD alignments

USAGE: `emClarity_setup.py -i <IMOD_BASE_DIR> -o <EMCLARITY_PROJECT_DIR>`
  
| Argument              |   Input               |    Explanation |
|:----------------------|:----------------------|:-----------|
|-i  |  <IMOD_BASE_DIR>| Directory containing all tilt series reconstructed in IMOD |
|-o  |   <EMCLARITY_PROJECT_DIR>| emClarity project directory, necessary files will be copied here|

## Example:

Want to set up an emClarity project tilt-series & IMOD alignments found in subdirectories of /home/user/tilt_series and put all necessary files in /home/user/emClarity_proj...

```python emClarity_setup.py -i /home/user/tilt_series -o /home/user/emClarity_proj```

## Requirements:

IMOD programs must be on the path (one step involves conversion of model file to .txt file containing model coordinates
