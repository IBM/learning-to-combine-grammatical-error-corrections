#!/bin/sh
# (C) Copyright IBM Corporation 2020.
#
# LICENSE: Apache License 2.0 (Apache-2.0)
# http://www.apache.org/licenses/LICENSE-2.0
# The script accepts to tool names to merge

tool1=$1
tool2=$2
dev_set=$3
test_set=$4

if [ -z $test_set ]; then
   echo "NAME"
   echo "optimized_merged.sh - This combines the results script performs an operation (AND/OR/FILTER) between two m2 files"
   echo 
   echo "SYNOPSIS"
   echo "optimized_merged.sh tool1 tool2 dev_set train_set [seed]" 
   echo
   exit
fi 

# Optional seed used to split the dev set, if not specified, split by row index
seed=$5
if [ ! -z $seed ] ; then
   seed_arg="-seed ${seed}"
else
   seed_arg=""
fi

# stop on error
set -e

# The name of the dev and tests sets.
dev_gold_m2="${dev_set}.gold.bea19.m2"
resource_dir="resources"
echo "*******************************************************************************************************"
echo "*******************************************************************************************************"
echo "*******************************************************************************************************"
echo "****"
echo "**** ${tool1}"
echo "****"
echo "**** AND"
echo "****"
echo "**** ${tool2}"
echo "****"
echo "*******************************************************************************************************"
echo "*******************************************************************************************************"
echo

mkdir -p merged

# The merge is done according the the categorization level
# Level 3 - includes M/R/U + type
# LEvel 2 - type
# Level 1 - not supported
CAT="3"


# Copy the dev gold m2
echo "Copy the dev gold files and split them..."
cp ${resource_dir}/${dev_gold_m2} merged/${dev_gold_m2}
python ./convertors/split_m2_file.py -m2 merged/${dev_gold_m2} -parts 2 ${seed_arg}


# Copy or create the dev set of each tool and then split into two parts

echo "Creating input files of all tools, if do not exist.  Assumes .m2 or tokenized.txt or .txt are in resource folder"
for type in $dev_set $test_set
do
    for i in $tool1 $tool2 
    do
        if [ ! -s merged/${type}.part1.$i.m2 ]; then
            echo "Creating m2 for $type $i"
            if [ ! -s merged/${type}.$i.m2 ]; then
                if [ -s ${resource_dir}/${type}.$i.m2 ]; then
                    cp ${resource_dir}/${type}.$i.m2 merged/${type}.$i.m2
                else
                    if [ ! -s merged/${type}.$i.tokenized.txt ]; then
                        if [ -s ${resource_dir}/${type}.$i.tokenized.txt ]; then
                           cp ${resource_dir}/${type}.$i.tokenized.txt merged/${type}.$i.tokenized.txt
                        else
                           if [ ! -s ${resource_dir}/${type}.$i.txt ]; then
                              echo "${resource_dir}/${type}.$i.txt does not exist"
                              exit 1
                           fi
                           cp ${resource_dir}/${type}.$i.txt merged/${type}.$i.txt
                           python ./convertors/text_to_splitted_text.py  -path merged -files ${type}.$i.txt
                        fi
                    fi
                    errant_parallel -orig ${resource_dir}/$type.orig.bea19.tokenized.txt -cor merged/${type}.$i.tokenized.txt -out merged/${type}.$i.m2
                fi
            fi
            python ./convertors/split_m2_file.py -m2 merged/${type}.$i.m2 -parts 2 ${seed_arg}
        fi
    done
done

# Configuration to used in development, where we split the dev set
if [ dev_set == test_set ]; then
  dev_set="${sev_set}.part1"
  test_set="${dev_set}.part2"
  test_gold_m2="${test_set}.gold.bea19.m2"
  dev_gold_m2="${dev_set}.gold.bea19.m2"
else 
  # Configuration to be used in actual test
  test_gold_m2=""
  dev_gold_m2="${dev_set}.gold.bea19.m2"
fi

# Show the assessment of each of the tools on the dev set
for i in $tool1 $tool2
do
    errant_compare -hyp merged/${dev_set}.$i.m2 -ref merged/${dev_gold_m2} -cat ${CAT} | tee merged/${dev_set}.$i.results | tail -5
done

# Generate the diffs between the two tools  and their intersections on dev set
for type in ${dev_set}
do
  if [ ! -s merged/${type}.${tool1}_minus_${tool2}.m2 ]; then
    ./run_m2_op.sh merged/${type}.${tool1}.m2 DIFF merged/${type}.${tool2}.m2  merged/${type}.${tool1}_minus_${tool2}.m2 merged/${dev_gold_m2} ${CAT}
  fi

  if [ ! -s merged/${type}.${tool2}_minus_${tool1}.m2 ]; then
    ./run_m2_op.sh merged/${type}.${tool2}.m2 DIFF merged/${type}.${tool1}.m2  merged/${type}.${tool2}_minus_${tool1}.m2 merged/${dev_gold_m2} ${CAT}
  fi

  if [ ! -s merged/${type}.${tool1}_and_${tool2}.m2 ]; then
    ./run_m2_op.sh merged/${type}.${tool1}.m2 AND  merged/${type}.${tool2}.m2  merged/${type}.${tool1}_and_${tool2}.m2 merged/${dev_gold_m2} ${CAT}
  fi
done

# Create optimal filter models

python convertors/optimized_merge.py \
  -trainAminusB merged/${dev_set}.${tool1}_minus_${tool2}.results \
  -trainBminusA merged/${dev_set}.${tool2}_minus_${tool1}.results \
  -trainAandB   merged/${dev_set}.${tool1}_and_${tool2}.results \
  -modelAminusB merged/${tool1}_minus_${tool2}.model \
  -modelBminusA merged/${tool2}_minus_${tool1}.model \
  -modelAandB   merged/${tool1}_and_${tool2}.model

# Generate the diffs between the two tools  and their intersections on the test set
for type in ${test_set}
do
  if [ ! -s merged/${type}.${tool1}_minus_${tool2}.m2 ]; then
    ./run_m2_op.sh merged/${type}.${tool1}.m2 DIFF merged/${type}.${tool2}.m2  merged/${type}.${tool1}_minus_${tool2}.m2
  fi

  if [ ! -s merged/${type}.${tool2}_minus_${tool1}.m2 ]; then
    ./run_m2_op.sh merged/${type}.${tool2}.m2 DIFF merged/${type}.${tool1}.m2  merged/${type}.${tool2}_minus_${tool1}.m2
  fi

  if [ ! -s merged/${type}.${tool1}_and_${tool2}.m2 ]; then
    ./run_m2_op.sh merged/${type}.${tool1}.m2 AND  merged/${type}.${tool2}.m2  merged/${type}.${tool1}_and_${tool2}.m2
  fi
done


# Generated merged output for both dev and test set

for type in ${dev_set} ${test_set}
do

  # apply filter models
  for comb in ${tool1}_minus_${tool2}  ${tool2}_minus_${tool1}  ${tool1}_and_${tool2}
  do
    if [ ! -s merged/${type}.${comb}.filtered.m2 ]; then
      python ./convertors/filter_m2_file_by_selection_model.py -hyp  merged/${type}.${comb}.m2 -model merged/${comb}.model -out merged/${type}.${comb}.filtered.m2
    fi
  done

  # merge filtered models
  if [ ! -s merged/${type}.${tool1}_xor_${tool2}.m2 ]; then
     ./run_m2_op.sh merged/${type}.${tool1}_minus_${tool2}.filtered.m2 OR merged/${type}.${tool2}_minus_${tool1}.filtered.m2  merged/${type}.${tool1}_xor_${tool2}.m2
  fi
  if [ ! -s merged/${type}.${tool1}_merged_${tool2}.m2 ]; then
     ./run_m2_op.sh merged/${type}.${tool1}_xor_${tool2}.m2 OR merged/${type}.${tool1}_and_${tool2}.filtered.m2  merged/${type}.${tool1}_merged_${tool2}.m2
  fi
done

echo "Evaluate of merge on ${dev_set} - TEST ON TRAIN"

for i in $tool1 $tool2
do
    echo $i:
    cat merged/${dev_set}.$i.results | tail -5
done

echo "${tool1}_merged_${tool2}:"
errant_compare -hyp merged/${dev_set}.${tool1}_merged_${tool2}.m2 -ref merged/${dev_gold_m2} -cat ${CAT} | tee merged/${dev_set}.${tool1}_merged_${tool2}.results | tail -5

echo "Convert to text files and regenerate m2"
python ./convertors/m2_to_text.py -path . -file merged/${test_set}.${tool1}_merged_${tool2}.m2 > /dev/null
cat merged/${test_set}.${tool1}_merged_${tool2}.m2 | grep "^S" | cut -c3- > merged/${test_set}.orig.tokenized.txt
errant_parallel -orig merged/${test_set}.orig.tokenized.txt -cor merged/${test_set}.${tool1}_merged_${tool2}.tokenized.txt -out merged/${test_set}.${tool1}_merged_${tool2}_validate.m2

echo "Compare the regenerated m2 and the m2"
errant_compare -hyp merged/${test_set}.${tool1}_merged_${tool2}.m2 -ref merged/${test_set}.${tool1}_merged_${tool2}_validate.m2 -cat ${CAT} | tail -5
echo
echo

if [ ! -z $test_gold_m2 ]; then
    echo "Evaluation on ${test_set} (TEST)"

    for i in $tool1 $tool2
    do
        echo $i:
        errant_compare -hyp merged/${test_set}.$i.m2 -ref merged/${test_gold_m2} -cat ${CAT} | tee merged/${test_set}.$i.results | tail -5
    done

    echo "${tool1}_merged_${tool2}:"
    errant_compare -hyp merged/${test_set}.${tool1}_merged_${tool2}.m2 -ref merged/${test_gold_m2} -cat ${CAT} | tee merged/${test_set}.${tool1}_merged_${tool2}.results | tail -5

    echo "merged/${test_set}.${tool1}_merged_${tool2}_validate.m2"
    errant_compare -hyp merged/${test_set}.${tool1}_merged_${tool2}_validate.m2 -ref merged/${test_gold_m2} -cat ${CAT} | tee merged/${test_set}.${tool1}_merged_${tool2}_validate.results | tail -5

fi

echo merged/${test_set}.${tool1}_merged_${tool2}.tokenized.txt

