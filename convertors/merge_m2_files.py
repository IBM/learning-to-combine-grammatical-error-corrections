# (C) Copyright IBM Corporation 2020.
#
# LICENSE: Apache License 2.0 (Apache-2.0)
# http://www.apache.org/licenses/LICENSE-2.0
import argparse
import os
import errant
import spacy
from nltk import LancasterStemmer

from contextlib import ExitStack

from span import Span
from edit import Edit

emptySpan = Span(-1, -1)


# Input: An m2 format sentence with edits.
# Output: A list of lists. Each edit: [start, end, cat, cor, coder]
def simplifyEdits(sent):
    out_edits = []
    # Get the edit lines from an m2 block.
    edits = sent.split("\n")[1:]
    # Loop through the edits
    for edit in edits:
        origLine = edit
        # Preprocessing
        edit = edit[2:].split("|||")  # Ignore "A " then split.
        span = edit[0].split()
        start = int(span[0])
        end = int(span[1])
        cat = edit[1]
        cor = edit[2]
        coder = int(edit[-1])
        edit = Edit(start, end, cat, cor, coder, origLine)
        # out_edit = [Span(start, end), cat, cor, coder, origLine]
        out_edits.append(edit)
    return out_edits


def isCoveredByFilterEdits(edit, filterEdits):
    editSpan = edit.span
    for filterEdit in filterEdits:
        filteredSpan = filterEdit.span
        #     if editSpan.start >= filteredSpan.start and editSpan.start < filteredSpan.end:
        #        return filteredSpan
        #   if editSpan.end >= filteredSpan.start and editSpan.end < filteredSpan.end:
        #       return filteredSpan

        if (editSpan.start >= filteredSpan.start and editSpan.start < filteredSpan.end) or (
                filteredSpan.start >= editSpan.start and filteredSpan.end < editSpan.end):  # we are using span [ )
            if (editSpan.start == filteredSpan.start):
                if edit.cat in ("M:PUNCT", "M:DET", "M:PREP", "M:NOUN:POSS"):
                    # print("edit is NOT filtered: ", edit.origLine)
                    continue
            return filteredSpan
    return emptySpan


def isExistsInEdits(sideAEdit, sideBEdits):
    for edit in sideBEdits:
        if edit.origLine == sideAEdit.origLine:
            return True
    return False


def isSpanExistsInEdits(sideAEdit, sideBEdits):
    aSpan = sideAEdit.span
    for edit in sideBEdits:
        bSpan = edit.span
        if bSpan.start == aSpan.start and bSpan.end == aSpan.end:
            return True
        if aSpan.end - aSpan.start > 0 and bSpan.end - bSpan.start > 0:
            if bSpan.start > aSpan.start and bSpan.end <= aSpan.end or bSpan.start >= aSpan.start and bSpan.end < aSpan.end:
                # print ("OR found overlap spans:["+sideAEdit[2],sideAEdit[3]+"] on one side, but ["+edit[2],edit[3]+"] on the other side")
                return True
    return False


def mergeAndSortBothSides(sideA_edits, sideB_edits):
    if len(sideA_edits) == 1 and sideA_edits[0].origLine == "A -1 -1|||noop|||-NONE-|||REQUIRED|||-NONE-|||0":
        edits = []
    else:
        edits = sideA_edits
    if len(sideB_edits) == 1 and sideB_edits[0].origLine == "A -1 -1|||noop|||-NONE-|||REQUIRED|||-NONE-|||0":
        return edits
    for edit in sideB_edits:
        if not isSpanExistsInEdits(edit, edits):
            edits.append(edit)
    edits.sort()
    return edits


def main(args):
    # Get base working directory.
    nlp = spacy.load("en")
    basename = os.path.dirname(os.path.realpath(__file__))
    # Load Tokenizer and other resources
    nlp = spacy.load("en")
    # Lancaster Stemmer
    stemmer = LancasterStemmer()
    # GB English word list (inc -ise and -ize)
    # Setup output m2 file

    # ExitStack lets us process an arbitrary number of files line by line simultaneously.
    # See https://stackoverflow.com/questions/24108769/how-to-read-and-process-multiple-files-simultaneously-in-python
    print("Processing " + args.sideA + " by: " + args.sideB + " using " + args.heuristics + "...")
    with ExitStack() as stack:
        sideA_m2 = open(args.sideA).read().strip().split("\n\n")
        sideB_m2 = open(args.sideB).read().strip().split("\n\n")
        outputFile = open(args.out, "w")

        # Make sure they have the same number of sentences
        assert len(sideA_m2) == len(sideB_m2)
        sents = zip(sideA_m2, sideB_m2)
        for sent_id, sent in enumerate(sents):
            sentencesLine = sent[0].split("\n")[0]
            otherSentencesLine = sent[1].split("\n")[0]

            if (sentencesLine != otherSentencesLine):
                print("Sentences not equals:")
                print(sentencesLine)
                print(otherSentencesLine)

            sideA_edits = simplifyEdits(sent[0])
            sideB_edits = simplifyEdits(sent[1])
            if len(sideB_edits) == 1 and sideB_edits[0][0] == -1 and sideB_edits[0][1] == -1 and len(
                    sideA_edits) == 1 and sideA_edits[0][0] == -1 and sideA_edits[0][1] == -1:
                # nothing to filter - write this line and continue:
                outputFile.write(sent[0] + "\n\n")
                continue
            if args.heuristics == "DIFF":
                # add only lines where the span is not covered by filtered spans:
                outputFile.write(sentencesLine + "\n")
                changeDone = False
                for edit in sideA_edits:
                    if (not isExistsInEdits(edit, sideB_edits)):
                        # print ("----------------------------\nin sentence: \n", sentencesLine, "\n", edit,"\nexists in both sides:\n ", sideB_edits)
                        outputFile.write(edit.origLine + "\n")
                        changeDone = True
                if changeDone == False:
                    outputFile.write("A -1 -1|||noop|||-NONE-|||REQUIRED|||-NONE-|||0\n")
                outputFile.write("\n")
            elif args.heuristics == "FILTER":
                # add only lines where the span is not covered by filtered spans:
                outputFile.write(sentencesLine + "\n")
                changeDone = False
                for edit in sideA_edits:
                    coveredSpan = isCoveredByFilterEdits(edit, sideB_edits)
                    if (coveredSpan == (-1, -1)):
                        outputFile.write(edit.origLine + "\n")
                    changeDone = True
                if changeDone == False:
                    outputFile.write("A -1 -1|||noop|||-NONE-|||REQUIRED|||-NONE-|||0\n")
                outputFile.write("\n")
            elif args.heuristics == "AND":
                # add only lines where the span is not covered by filtered spans:
                outputFile.write(sentencesLine + "\n")
                changeDone = False
                for edit in sideA_edits:
                    if (isExistsInEdits(edit, sideB_edits)):
                        # print ("----------------------------\nin sentence: \n", sentencesLine, "\n", edit,"\nexists in both sides:\n ", sideB_edits)
                        outputFile.write(edit.origLine + "\n")
                        changeDone = True
                if changeDone == False:
                    outputFile.write("A -1 -1|||noop|||-NONE-|||REQUIRED|||-NONE-|||0\n")
                outputFile.write("\n")
            elif args.heuristics == "OR":
                outputFile.write(sentencesLine + "\n")
                edits = mergeAndSortBothSides(sideA_edits, sideB_edits)
                for edit in edits:
                    outputFile.write(edit.origLine + "\n")
                    changeDone = True
                if changeDone == False:
                    outputFile.write("A -1 -1|||noop|||-NONE-|||REQUIRED|||-NONE-|||0\n")
                outputFile.write("\n")
            else:
                print("not sure what do you want me to do, please implement the heuristics " + args.heuristics)


if __name__ == "__main__":
    # Define and parse program input
    parser = argparse.ArgumentParser(description="TBD",
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     usage="%(prog)s -files FILES [FILES ...]")
    parser.add_argument("-sideA", help="The path of base file", required=True)
    parser.add_argument("-sideB", help="The path of second file", required=True)
    parser.add_argument("-out", help="output file [m2]", required=True)
    parser.add_argument("-heuristics", help="FILTER/AND/OR... [tbd]", required=False)
    args = parser.parse_args()
    # Run the program.
    main(args)
