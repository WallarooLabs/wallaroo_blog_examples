#!/usr/bin/python

from sklearn import linear_model, decomposition, datasets
from sklearn.model_selection import GridSearchCV

import cPickle as pickle

if __name__ == '__main__':
    #load data
    digits = datasets.load_digits()
    X_digits = digits.data
    y_digits = digits.target

    #train and save P4CA
    pca = decomposition.PCA()
    n_components = [20, 40, 64]
    pca_optimised = GridSearchCV(pca, dict(n_components=n_components))
    pca_optimised.fit(X_digits)
    with open('pca.model','w') as f:
        pickle.dump(pca_optimised, f)

    #apply PCA transformation to train the model
    X_digits_transformed = pca_optimised.transform(X_digits)

    #train and fit a logistic regression
    Cs = [2, 4, 3]
    logistic = linear_model.LogisticRegression()
    logistic_optimised = GridSearchCV(logistic, dict(C=Cs))
    logistic_optimised.fit(X_digits_transformed, y_digits)
    with open('logistic.model','w') as f:
        pickle.dump(logistic_optimised, f )
