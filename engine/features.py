
import os
import sys
import importlib

from constants import FEATURES_DIR
sys.path.extend( [FEATURES_DIR] )
features_filenames = [file for file in os.listdir(FEATURES_DIR) if os.path.isfile( os.path.join(FEATURES_DIR, file) )]

for filename in features_filenames:
    #filepath = os.path.join(FEATURES_DIR, filename)
    if filename.startswith("."): continue
    f = filename[:-3]
    importlib.import_module(f)