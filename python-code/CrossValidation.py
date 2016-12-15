from MathSymClassifier import MathSymClassifier
import numpy as np
from sklearn.model_selection import cross_val_score
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

classifier = MathSymClassifier()
data = classifier.training_set.get_training_data()
labels = classifier.training_set.get_training_labels()
text_labels = classifier.training_set.get_text_labels()

cross_validate = cross_val_score(classifier.svm, data, labels, cv=10)

bars = plt.bar(range(1,11), [100 * c for c in cross_validate], alpha=0.4, color='b', label="Accuracy")
plt.savefig("cross_validation.jpg")




