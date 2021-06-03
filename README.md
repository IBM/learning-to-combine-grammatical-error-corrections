# Learning to combine grammatical error corrections

This repository contains the code that implements the automatic combination of grammatical error correction systems described in [Yoav Kantor, et al. (2019)](#reference) 

**Table of contents**

[Installation](#installation)

[Example](#example)

[License](#license)

## Installation

You need to install version 2.0.0 of ERRANT according to the instructions in its github page.  These are replicated here for convenience.

```
conda create --name gec python=3.6
conda activate gec
pip3 install -U pip setuptools wheel
pip3 install errant==2.0.0
python3 -m spacy download en
```

Then install

```
pip install pandas
pip install scipy
```
 
## Example

The script `combine_top_bea19_systems.sh` combines the original top systems in the BEA 2019 Shared Task.

The top systems were UEDIN-MS and KakaoAndBrain.  

KakaoAndBrain:
Yo Joong Choe, Jiyeon Ham, Kyubyong Park, and Yeoil Yoon.  2019. A Neural Grammatical Error Correction System Built On Better Pre-training andSequential Transfer Learning. In Proceedings of the 14th Workshop on Innovative Use of NLP for Building Educational Applications. Association for Computational Linguistics.
https://www.aclweb.org/anthology/W19-4423/

UEDIN-MS:
Roman Grundkiewicz, Marcin Junczys-Dowmunt, and Kenneth Heafield. 2019.  Neural Grammatical Error Correction Systems with Unsupervised Pre-training on Synthetic Data. In Proceedings of the 14th Workshop on Innovative Use of NLP for Building Educational Applications. Association for Computational Linguistics.
https://www.aclweb.org/anthology/W19-4427/

The input files are found under the `resource` directory

`
dev2.OT.KakaoAndBrain.tokenized.txt
dev2.OT.UEDIN-MS.tokenized.txt
test2.OT.KakaoAndBrain.tokenized.txt
test2.OT.UEDIN-MS.tokenized.txt
`

The `dev2` files are used to find the optimal combination of annotation types between the two systems.   Then, this combination is used to combine the test system annotations.

The output is found in the `output` directory.

`test2.OT.UEDIN-MS_merged_OT.KakaoAndBrain.tokenized.txt`

After zipping the file and uploading to the current CodeLab website (https://competitions.codalab.org/competitions/20228).  The results are:

```tp_cs:3133
fp_cs:868
fn_cs:2269
p_cs:78.31
r_cs:58.00
f0.5_cs:73.18
```

F0.5 of the combined system is 73.18 compared to F0.5 of 69.47 for UEDIN-MS and  69.00 KakaoAndBrain, respectively (see https://www.cl.cam.ac.uk/research/nl/bea2019st/)

The script `combine_top_bea19_systems.sh` is simply a wrapper of the `optimized_merge.sh` script that takes two systems and two datasets (a dev set for selection of combination policy and the test set).

```
optimized_merge.sh OT.UEDIN-MS $OT.KakaoAndBrain dev2 test2
```


Following the run the `merged` directory contains a cache of intermediate results, that make future runs faster.  It can be deleted to ensure a clean run after a failure.

## Combining more than two systems

To combine three or more systems, the merge should be done in a pairwise fashion.

```
optimized_merge.sh OT.UEDIN-MS OT.KakaoAndBrain dev2 test2
optimized_merge.sh OT.UEDIN-MS_merged_OT.KakaoAndBrain OT.Shuyao dev2 test2
```

Shayao was the 5th system in the original shared task.

Shuyao Xu, Jiehao Zhang, Jin Chen, and Long Qin. 2019. Erroneous data generation for Grammatical Error Correction.   In proceedings of the 14th Workshop on Innovative Use of NLP for Building Educational Applications. Association for Computational Linguistics. 
https://www.aclweb.org/anthology/W19-4415/

## Reference
Yoav Kantor, Yoav Katz, Leshem Choshen, Edo Cohen-Karlik, Naftali Liberman, Assaf Toledo, Amir Menczel, Noam Slonim
 (2019). 
[Learning to combine Grammatical Error Corrections](https://www.aclweb.org/anthology/W19-4414/).  Proceedings of the Fourteenth Workshop on Innovative Use of NLP for Building Educational Applications 

Please cite: 
```
inproceedings{kantor-etal-2019-learning,
    title = "Learning to combine Grammatical Error Corrections",
    author = "Kantor, Yoav  and
      Katz, Yoav  and
      Choshen, Leshem  and
      Cohen-Karlik, Edo  and
      Liberman, Naftali  and
      Toledo, Assaf  and
      Menczel, Amir  and
      Slonim, Noam",
    booktitle = "Proceedings of the Fourteenth Workshop on Innovative Use of NLP for Building Educational Applications",
    month = aug,
    year = "2019",
    address = "Florence, Italy",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/W19-4414",
    doi = "10.18653/v1/W19-4414",
    pages = "139--148",
    abstract = "The field of Grammatical Error Correction (GEC) has produced various systems to deal with focused phenomena or general text editing. We propose an automatic way to combine black-box systems. Our method automatically detects the strength of a system or the combination of several systems per error type, improving precision and recall while optimizing F-score directly. We show consistent improvement over the best standalone system in all the configurations tested. This approach also outperforms average ensembling of different RNN models with random initializations. In addition, we analyze the use of BERT for GEC - reporting promising results on this end. We also present a spellchecker created for this task which outperforms standard spellcheckers tested on the task of spellchecking. This paper describes a system submission to Building Educational Applications 2019 Shared Task: Grammatical Error Correction. Combining the output of top BEA 2019 shared task systems using our approach, currently holds the highest reported score in the open phase of the BEA 2019 shared task, improving F-0.5 score by 3.7 points over the best result reported.",
}

```

## License
This work is released under the Apache 2.0 license. The full text of the license can be found in [LICENSE](LICENSE).
