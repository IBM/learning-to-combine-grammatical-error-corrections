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
	# Load Tokenizer and other resources
	# nlp = spacy.load("en_core_web_sm")
	nlp = spacy.load("en")
	# Lancaster Stemmer
	stemmer = LancasterStemmer()
	# GB English word list (inc -ise and -ize)
	gb_spell = toolbox.loadDictionary(basename+"/../common/resources/en_GB-large.txt")
	# Part of speech map file
	tag_map = toolbox.loadTagMap(basename+"/../common/resources/en-ptb_map")
	# Setup output m2 file

	# ExitStack lets us process an arbitrary number of files line by line simultaneously.
	# See https://stackoverflow.com/questions/24108769/how-to-read-and-process-multiple-files-simultaneously-in-python
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