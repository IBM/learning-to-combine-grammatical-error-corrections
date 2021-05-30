# (C) Copyright IBM Corporation 2020.
#
# LICENSE: Apache License 2.0 (Apache-2.0)
# http://www.apache.org/licenses/LICENSE-2.0

import argparse
import os
import spacy
from contextlib import ExitStack
from nltk.stem.lancaster import LancasterStemmer
import common.scripts.toolbox as toolbox
from pathlib import Path
import sys
import re

def tokenized(txt, nlp):
	sent = nlp(txt)
	joined = ''
	for token in sent:
		joined += (token.text + ' ')
	return re.sub(' +', ' ',joined).strip()

def main(args):
	# Get base working directory.
	basename = os.path.dirname(os.path.realpath(__file__))
	print("Loading resources...")
	nlp = spacy.load("en")
	print("Processing files...")	
	with ExitStack() as stack:
		pathlist = Path(args.path).glob(args.files)
		in_files = [stack.enter_context(open(i)) for i in pathlist]
		for file in in_files:
			tokenizedFile = open(file.name.replace(".txt", ".tokenized.txt"), "w")
			for line_id, line in enumerate(file):
				tokenizedFile.write(tokenized(line, nlp).strip()+"\n")

if __name__ == "__main__":
	# Define and parse program input
	parser = argparse.ArgumentParser(description="TBD",
								formatter_class=argparse.RawTextHelpFormatter,
								usage="%(prog)s -files FILES [FILES ...]")
	parser.add_argument("-files", help="The file name or pattern to >= 1 corrected text files.", required=True)
	parser.add_argument("-path", help="The path", required=True)
	args = parser.parse_args()
	# Run the program.
	main(args)