#!/bin/sh

seed=

top1=OT.UEDIN-MS
top2=OT.KakaoAndBrain
top5=OT.Shuyao

set -e

./optimized_merge.sh ${top1} ${top2} ${seed}
#./optimized_merged.sh ${top1}_merged_${top2} ${top5}  ${seed}


