import argparse
import numpy as np
import random
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


def main(args):
    print("Processing " + args.hyp + " by: " + args.model + " to" + args.out + "...")
    with open(args.hyp) as hyp:
        m2 = hyp.read().strip().split("\n\n")
    model = np.genfromtxt(args.model, dtype=[('cat', 'U13'), ('sel', 'f8')])
    with open(args.out, "w") as output_file:
        for sent_id, sent in enumerate(m2):
            sentencesLine = sent.split("\n")[0]
            edits = simplifyEdits(sent)
            output_file.write(sentencesLine + "\n")
            changeDone = False
            for edit in edits:
                if edit.cat == "noop":
                    continue
                pairs = [pair for pair in zip(model['cat'], model['sel']) if edit.cat.endswith(pair[0])]
                if (len(pairs) == 0):
                    print("Unable to find model value " + str(edit.cat) + " in " + str(model['cat']))
                    print("Skipping this correction")
                    continue
                assert len(pairs) == 1
                prob = pairs[0][1]
                # Selection probability is between [0,1],
                # we randomly choose a number between [0,1) and if it falls within the selection probability
                # we add the correction.
                # As for now , probability is either 0 ,1
                if (random.random() >= prob):
                    pass
                else:
                    output_file.write(edit.origLine + "\n")
                    changeDone = True
            if changeDone == False:
                output_file.write("A -1 -1|||noop|||-NONE-|||REQUIRED|||-NONE-|||0\n")
            output_file.write("\n")


if __name__ == "__main__":
    # Define and parse program input
    parser = argparse.ArgumentParser(description="Filter m2 by selection model",
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     usage="%(prog)s -hyp <m2> -model <model> -out <output m2>")
    parser.add_argument("-hyp", help="The path of base file", required=True)
    parser.add_argument("-model", help="The path model file containing categories", required=True)
    parser.add_argument("-out", help="output file [m2]", required=True)
    args = parser.parse_args()
    # Run the program.
    main(args)
