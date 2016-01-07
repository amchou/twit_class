# twit_class
cleaning web corpora, playing with classification, and using WEKA


###Sample Commands:
(note that /twts/ contains tweets normalized via twtt.py)
 
Building .arff:
```
python buildarff.py BO:twts/BarackObama.twt SC:twts/StephenAtHome.twt AK:twts/aplusk.twt KK:twts/KimKardashian.twt NT:twts/neiltyson.twt Sh:twts/shakira.twt sample.arff
```
WEKA (10-fold cross-validation):
```
SVM: java -cp /u/cs401/WEKA/weka.jar weka.classifiers.functions.SMO -t sample.arff -x 10 -o
Bayes:java -cp /u/cs401/WEKA/weka.jar weka.classifiers.bayes.NaiveBayes -t sample.arff -x 10 -o
Trees: java -cp /u/cs401/WEKA/weka.jar weka.classifiers.trees.J48 -t sample.arff -x 10 -o
```
SVM, Naive Bayes and decision trees give accuracies 49.5%,43.1%, and 47.2% respectively.

###Another sample:
```
=== Confusion Matrix ===
 a   b   c   d   e   f   <-- classified as
 722  39  60  55  91  33 |   a = CBC
 304 169 125 137 106 159 |   b = CNN
 498  52 178  85 132  55 |   c = TStar
 369  77  89 250 130  85 |   d = Reuters
 195  32  53  76 532 112 |   e = NYTimes
 152 113  63  62 197 413 |   f = Onion
```
From WEKA's Confusion Matrix we can compute precision and recall for each class.
```
Class: precision, recall
CBC: 	0.722, 	0.322
CNN: 	0.169, 	0.351
TStar: 	0.178, 	0.313
Reuters:0.25, 	0.376
NYTimes:0.532, 	0.448
Onion:	0.413,	0.482
```

Improvement after trying new features:
SVM: 47.7%, decision trees at 48.8% up from original of 37.7% (from SVM): over 10% increase!

```
=== Confusion Matrix ===
   a   b   c   d   e   f   <-- classified as
   483 127 169 173  25  23 |   a = CBC
   125 450 164 158  53  50 |   b = CNN
   310 151 337 165  21  16 |   c = TStar
   251 168 155 358  35  33 |   d = Reuters
   22  61  22  30 665 200 |   e = NYTimes
   28  67  20  37 211 637 |   f = Onion
```

We have new precision and recalls:
```
Class: precision, recall
CBC: 	0.483, 	0.396
CNN: 	0.45, 	0.439
TStar: 	0.337, 	0.389
Reuters:0.358, 	0.389
NYTimes:0.665, 	0.658
Onion:	0.637,	0.664
```
Note that recall is higher for every class, but follows the same trend across classes. Precision is higher on average but not for all.

```
Ranked attributes (by information gain):
 0.51147   25 Abcd
 0.18771   21 num_chars
 0.10865   18 avg_sent_len
 0.10389   13 prop_noun
``` 
We can see that capitalized words are most useful for News. (notably, the Onion has almost whole tweets composed of these).
