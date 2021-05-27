import argparse
import os
import spacy
from contextlib import ExitStack
from pathlib import Path
import sys
import re

COMMA = ","


def fixText(text):
	fixedText = text;

	fixedText = fixedText.replace(" n't", "n't")
	fixedText = fixedText.replace(" '", "'")
	fixedText = re.sub("\" ([^\"]+)[., ]+\"",r' "\1" ',fixedText)
	fixedText = re.sub("\( ([^\)ֿֿ\(]+) \)[ ]+",r' (\1) ',fixedText)
	fixedText = fixedText.replace(" ,", ",")
	fixedText = fixedText.replace(" ?", "?")
	fixedText = fixedText.replace(" !", "!")
	fixedText = fixedText.replace(" .", ".")
	fixedText = fixedText.replace("  ", " ")
	# fixedText = fixedText.replace(" \"", "\"")
	# if text != fixedText:
	# 	print(text, " => ", fixedText)
	return fixedText


def changeByCorrectionLine(currentLine, correctionLine):
	currentLineSplitted = currentLine.split()
	if len(currentLineSplitted)<1:
		return currentLine
	corrections =  correctionLine.replace("\n","").split("|||")
	span = list(map(int, corrections[0].split()))
	spanSize = span[1]-span[0]
	# if  spanSize > 1:
	# 	print("debug - span size: ",span)
	#contributor = int(corrections[5])
	#if contributor > 0:
		#print("more then one contributor!")
		#sys.exit(-1)
	errorCode =  corrections[1].split(":")
	currentText = currentLineSplitted[span[0]: span[1]]
	newText =  corrections[2].split()
	# print("span = ",span)
	# print("before:        ",' '.join(currentLineSplitted))
	if len(currentText) > 0:
		# print(currentText, " => ", newText)
		del currentLineSplitted[span[0]:span[1]]
	# else:
	# 	print("[]  => ", newText)
	currentLineSplitted = currentLineSplitted[0: span[0]] + newText + currentLineSplitted[span[1] - spanSize :]
	# print("after insert:  ", ' '.join(currentLineSplitted))
	# print("errorCode = ", errorCode)
	# print(corrections[1:])
	return (' '.join(currentLineSplitted),
			"["+' '.join(currentText) + "] => ["+ ' '.join(newText)+"]",
			errorCode)

def tokenized(txt, nlp):
	sent = nlp(txt)
	joined = ''
	for token in sent:
		joined += (token.text + ' ')
	return re.sub(' +', ' ',joined).strip()


def getCorrectionsForLastAnnotator(corrections):

	maxContributor = 0
	for correction in corrections:
		correctionValues = correction.replace("\n", "").split("|||")
		contributor = int(correctionValues[5])
		if contributor > maxContributor:
			maxContributor = contributor

	corrections_for_max_contributor = list(filter(lambda x: int(x.replace("\n", "").split("|||")[5]) == maxContributor, corrections))

	return corrections_for_max_contributor


def writeSentecne(currentLineAfter, currentLineBefore, corrections, fixedText, fixedTokenized, corrections_m2, i, nlp):
	print("--------------------------")
	# print the previous line
	print(i, "):")
	j = 0;
	correctionsForLastAnnotator = getCorrectionsForLastAnnotator(corrections)
	correctionResults = applyCorrections(currentLineAfter, correctionsForLastAnnotator)
	currentLineAfter = correctionResults[0]
	currentCorrectionSteps = correctionResults[1]
	fixedTxt = fixText(currentLineAfter.strip())
	print("before: ", currentLineBefore.strip())
	print("after : ", currentLineAfter.strip())
	fixedText.write(fixedTxt + "\n")
	fixedTokenized.write(tokenized(fixedTxt, nlp) + "\n")
	for correction in currentCorrectionSteps:
		j += 1
		print(j, ")", correction[1], correction[2])
		corrections_m2.write(' '.join(correction[2]) + COMMA +
			 "\"" + currentLineBefore.strip() + "\"" + COMMA +
			 "\"" + currentLineAfter.strip() + "\"" + COMMA +
			 "\"" + correction[1] + "\"\n")


def main(args):
	# Get base working directory.
	nlp = spacy.load("en")
	basename = os.path.dirname(os.path.realpath(__file__))
	print("Loading resources...")
	# Load Tokenizer and other resources
	nlp = spacy.load("en")

	# ExitStack lets us process an arbitrary number of files line by line simultaneously.
	# See https://stackoverflow.com/questions/24108769/how-to-read-and-process-multiple-files-simultaneously-in-python
	print("Processing files...")	
	with ExitStack() as stack:
		pathlist = Path(args.path).glob(args.files)
		in_files = [stack.enter_context(open(i)) for i in pathlist]
		i=0;
		for file in in_files:
#			if "gold" not in file.name:
#				print("file name should have the word \"gold\" in it. filename: " + file.name + ", skipping file.")
#				continue


			# Process each line of all input files.
			corrections_m2 = open(file.name+".csv", "w")

			origText = open(file.name.replace(".m2",".orig.txt"), "w")
			origTokenized = open(file.name.replace(".m2", ".orig.tokenized.txt"), "w")

			fixedText = open(file.name.replace(".m2",".txt"), "w")
			fixedTokenized = open(file.name.replace(".m2", ".tokenized.txt"), "w")

			currentLineBefore = None
			currentLineAfter = None
			for line_id, line in enumerate(file):
				if line == '\n':
					continue
				if line == "A -1 -1|||noop|||-NONE-|||REQUIRED|||-NONE-|||0\n":
					continue
				if line.strip().startswith("S"):
					if(currentLineBefore != None):
						i += 1
						writeSentecne(currentLineAfter, currentLineBefore, corrections, fixedText, fixedTokenized, corrections_m2, i, nlp)
					corrections = []
					#start proccesing a new line:
					currentLineBefore = line[1:]
					text = fixText(currentLineBefore.strip())
					origText.write(text+'\n')
					origTokenized.write(tokenized(text, nlp) + '\n')
					currentLineAfter = currentLineBefore
				if line.strip().startswith("A"):
					corrections.insert(0, line)
			# do it one more time for the last line
			i += 1
			writeSentecne(currentLineAfter, currentLineBefore, corrections, fixedText, fixedTokenized, corrections_m2, i, nlp)


def applyCorrections(currentLine, corrections):
	currentCorrectionSteps = []
	currentLineAfter = currentLine
	for correction in corrections:
		currentCorrectionStep = changeByCorrectionLine(currentLineAfter, correction[1:])
		currentLineAfter = currentCorrectionStep[0]
		currentCorrectionSteps.append(currentCorrectionStep)
	return (currentLineAfter, currentCorrectionSteps)


if __name__ == "__main__":
	# Define and parse program input
	parser = argparse.ArgumentParser(description="Convert m2 to file to .txt and .tokenized text files.  " +
												 "Both the original version and the correction version are created.",
								formatter_class=argparse.RawTextHelpFormatter,
								usage="%(prog)s -files FILES [FILES ...]")
	parser.add_argument("-files", help="The file name or pattern to >= 1 corrected text files.", required=True)
	parser.add_argument("-path", help="The path", required=True)
	args = parser.parse_args()
	# Run the program.
	main(args)