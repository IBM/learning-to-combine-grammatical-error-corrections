# Learning to combine grammarical error corrections

Introduced in [Ein-dor et al. (2020)](#reference), this is a framework for experimenting with text classification tasks.
The focus is on low-resource scenarios, and examining how active learning (AL) can be used in combination with
classification models.

**Table of contents**

[Installation](#installation)

[License](#license)

## Installation

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



# learning-to-combine-grammatical-error-corrections
Code from the "Learning to combine Grammatical Error Corrections"  paper. Proceedings of the Fourteenth Workshop on Innovative Use of NLP for Building Educational Applications (https://www.aclweb.org/anthology/W19-4414/)
