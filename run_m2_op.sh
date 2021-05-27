#!/bin/sh
set -e
CONVERTORS_SCRIPTS="./convertors/"

SIDE_A="${1}"
ACTION="${2}"
SIDE_B="${3}"
OUT="${4}"
COMPARE="${5}"
CAT="${6}"

if [ -z $SIDE_B ]; then
   echo "NAME"
   echo "run_m2_op.sh - This script performs an operation (AND/OR/FILTER) between two m2 files"
   echo 
   echo "SYNOPSIS"
   echo "run_m2_op.sh sideA.m2 AND/OR/FILTER sideB.m2 output.m2 [ gold.m2 cat]"
   echo
   echo "DESCRIPTION"
   echo
   echo "Takes sideA.m2 and sideB.m2 , performs the specified operation (AND/OR/FILTER)  and stores the result in output.m2"
   echo
   echo "If gold.m2 is specified, compares output.m2 with gold.m2.  The optional 'cat' params specifies the level of details of the compare (1,2,3 or omitted)."
   echo "The comparision is printed to the screen and also saved in the output.result file in the same directory as output.m2 ."
   exit
fi 

# SIDE_A="dev.bea19.TW.filtered.m2"
# SIDE_B="dev.bea19.NER.filtered.m2"
# OUT="dev.bea19.TW.and.NER.filtered.m2"
# ACTION="AND"
python $CONVERTORS_SCRIPTS/merge_m2_files.py -sideA $SIDE_A -sideB $SIDE_B -out $OUT -heuristics $ACTION
echo " ################################################################"
echo " ##     $SIDE_A"
echo " ##     \t$ACTION"
echo " ##     $SIDE_B"
echo " ##      \t="
echo " ##     $OUT"
echo " ################################################################"
if [ ! -z $COMPARE ]; then
  if [ ! -z $CAT ]; then
    CATARG="-cat $CAT"
  else
    CATARG=""
  fi
  errant_compare -ref $COMPARE -hyp $OUT $CATARG | tee ${OUT%.m2}.results | tail -5
fi
