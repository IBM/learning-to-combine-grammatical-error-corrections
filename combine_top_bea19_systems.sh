#!/bin/sh
# (C) Copyright IBM Corporation 2020.
#
# LICENSE: Apache License 2.0 (Apache-2.0)
# http://www.apache.org/licenses/LICENSE-2.0

# This example script combines the top bea 19 systems.

seed=

top1=OT.UEDIN-MS
top2=OT.KakaoAndBrain
top5=OT.Shuyao
dev_set=dev2
test_set=test2
set -e

./optimized_merge.sh ${top1} ${top2} ${dev_set} ${test_set} ${seed}
#./optimized_merged.sh ${top1}_merged_${top2} ${top5}  ${seed} 


