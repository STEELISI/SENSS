#!/usr/bin/env python
import os

output_folder=raw_input("Enter output folder: ")
os.system("wget https://github.com/firehol/blocklist-ipsets/archive/master.zip -P" +output_folder)
