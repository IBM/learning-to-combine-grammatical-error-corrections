# Learning to combine grammatical error corrections

This repository contains the code that implements the automatic combination of grammatical error correction systems described in [Yoav Kantor, et al. (2019)](#reference) 

**Table of contents**

[Installation](#installation)

[License](#license)

## Installation

You need to install version 2.0.0 of ERRANT according to the instructions in its github page.  These are replicated here for convenience.

conda create --name gec python=3.6
conda activate gec
pip3 install -U pip setuptools wheel
pip3 install errant==2.0.0
python3 -m spacy download en

Then install 

pip install pandas
pip install scipy
 
## Example run

The script combine_top_bea19_system.sh combines the original top restriction systems in the BEA 2019 Shared Task.

The top systems were UEDIN-MS and KakaoAndBrain.  

KakaoAndBrain:
Yo  Joong  Choe,  Jiyeon  Ham,  Kyubyong  Park,  andYeoil  Yoon.  2019. A  Neural  Grammatical  ErrorCorrection System Built On Better Pre-training andSequential Transfer Learning. InProceedings of the14th Workshop on Innovative Use of NLP for Build-ing Educational Applications. Association for Com-putational Linguistics.

UEDIN-MS:
62Roman Grundkiewicz, Marcin Junczys-Dowmunt, andKenneth Heafield. 2019.  Neural Grammatical ErrorCorrection Systems with Unsupervised Pre-trainingon Synthetic Data. InProceedings of the 14th Work-shop on Innovative Use of NLP for Building Educa-tional Applications. Association for ComputationalLinguistics.

The input files are found under the resource directory

dev2.OT.KakaoAndBrain.tokenized.txt
dev2.OT.UEDIN-MS.tokenized.txt
test2.OT.KakaoAndBrain.tokenized.txt
test2.OT.UEDIN-MS.tokenized.txt

The dev2 files are used to find the optimal combination of annotation types between the two systems.   Then, this combination is used to combine the test system annotations.

The output is found in the merged directory.

test2.OT.UEDIN-MS_merged_OT.KakaoAndBrain.tokenized.txt

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
