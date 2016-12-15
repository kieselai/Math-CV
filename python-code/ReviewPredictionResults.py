"""
	This script uses the currently trained classifier to attempt to classify all
	existing characters.  This gives a decent idea of how each individual character
	compares against other training data, but probably isn't a really scientific
	method of determining how good the classification attributes are.

	I should note that the results here are much better than the results achieved in
	practice, since I tried to use training images that were very well drawn. In reality,
	I've noticed that bad handwriting leads to classification results that are not
	as good as achieved here. 
"""

from MathSymClassifier import MathSymClassifier
c = MathSymClassifier()                       
data = c.training_set.get_training_data()                                            
predictions = c.predict(data)

labels = c.training_set.training_labels
text_labels = c.training_set.text_labels      
incorrect_predictions = {}                                                           
was_correct={}
for n in range(0,len(data)):
    if labels[n] in was_correct:
        was_correct[labels[n]].append(True if predictions[n] == labels[n] else False)
    else:
        was_correct[labels[n]] = [True if predictions[n] == labels[n] else False]
    if predictions[n] != labels[n]:
        if labels[n] in incorrect_predictions:
            incorrect_predictions[labels[n]].append(predictions[n])                 
        else:                                                                        
            incorrect_predictions[labels[n]] = [predictions[n]] 

tl = c.training_set.get_text_labels()
for k in sorted(incorrect_predictions.keys()):
    count_dict = dict((k2, incorrect_predictions[k].count(k2)) for k2 in incorrect_predictions[k])
    count_str = ""
    for k3 in sorted(count_dict.keys()):
        count_str = count_str +  "({}, {}: {}), ".format(count_dict[k3], tl[k3], k3)
    print("{}, {}: [{}]".format(k, tl[k], count_str))

for k in sorted(was_correct.keys()):
    corr = was_correct[k].count(True)
    total = len(was_correct[k])
    print("{}% Correct ----->  {}, {}".format(round(corr/total, 3)*100, k, tl[k]))

