# (C) Copyright IBM Corporation 2020.
#
# LICENSE: Apache License 2.0 (Apache-2.0)
# http://www.apache.org/licenses/LICENSE-2.0
import argparse
from contextlib import ExitStack
import random


def main(args):
    # ExitStack lets us process an arbitrary number of files line by line simultaneously.
    # See https://stackoverflow.com/questions/24108769/how-to-read-and-process-multiple-files-simultaneously-in-python
    numparts = int(args.parts)
    print("Splitting " + args.m2 + " to  " + str(numparts) + " parts ");
    if (args.seed is None):
        print("Split by row index.")
    else:
        print("Split randomly by seed " + args.seed + ".")
        random.seed(int(args.seed))
    m2 = open(args.m2).read().strip().split("\n\n")
    with ExitStack() as stack:
        out_m2_files = [stack.enter_context(open(args.m2.replace(".", ".part" + str(part) + ".", 1), "w"))
                        for part in range(1, numparts + 1)]
        out_tokenized_text_files = [stack.enter_context(
            open(args.m2.replace(".", ".part" + str(part) + ".", 1).replace(".m2", ".orig.tokenized.txt"), "w"))
            for part in range(1, numparts + 1)]

        for sent_id, sent in enumerate(m2):
            if (args.seed is None):
                r = sent_id % numparts
            else:
                r = random.randint(0, numparts - 1)
            out_tokenized_text_files[r].write(sent.split("\n")[0][2:] + "\n")
            out_m2_files[r].write(sent + "\n\n")


if __name__ == "__main__":
    # Define and parse program input
    parser = argparse.ArgumentParser(description="Splits and m2 file into equal parts",
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     usage="%(prog)s -m2 file.m2 -parts 2")
    parser.add_argument("-m2", help="The path of base file to split", required=True)
    parser.add_argument("-parts", help="Number of parts to split", required=True)
    parser.add_argument("-seed", help="Number of parts to split")
    args = parser.parse_args()
    # Run the program.
    main(args)
