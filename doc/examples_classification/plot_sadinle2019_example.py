"""
================================================
Reproducing Example 7 from Sadinle et al. (2019)
================================================

We use :class:`mapie.classification.MapieClassifier` to reproduce
Example 7 from Sadinle et al. (2019).

We consider a two-dimensional dataset with three labels. The distribution
of the data is a bivariate normal with diagonal covariance matrices for
each label.
We model the data with Gaussian Naive Bayes classifier
:class:`sklearn.naive_bayes.GaussianNB` as a base model.

Prediction sets are estimated by :class:`mapie.classification.MapieClassifier`
from the distribution of the softmax scores of the true labels for three
alpha values (0.2, 0.1, and 0.05) giving different class coverages.

When the class coverage is not large enough, the prediction sets can be empty
when the model is uncertain at the border between two labels. The null region
disappears for larger class coverages but ambiguous classification regions
arise with several labels included in the prediction sets.
"""
import numpy as np
import matplotlib.pyplot as plt

from sklearn.naive_bayes import GaussianNB

from mapie.classification import MapieClassifier


# Create training set from multivariate normal distribution
centers = [(0, 3.5), (-2, 0), (2, 0)]
covs = [[[1, 0], [0, 1]], [[2, 0], [0, 2]], [[5, 0], [0, 1]]]
x_min, x_max, y_min, y_max, step = -5, 7, -5, 7, 0.1
n_samples = 500
alphas = [0.2, 0.1, 0.05]
X_train = np.zeros((3*n_samples, 2))
i = 0
for center, cov in zip(centers, covs):
    (
        X_train[i*n_samples:(i+1)*n_samples, 0],
        X_train[i*n_samples:(i+1)*n_samples, 1]
    ) = np.random.multivariate_normal(center, cov, n_samples).T
    i += 1
y_train = np.stack([i for i in range(3) for _ in range(n_samples)]).ravel()

# Create test from (x, y) coordinates
X_test = np.stack([
    [x, y]
    for x in np.arange(x_min, x_max, step)
    for y in np.arange(x_min, x_max, step)
])


# Apply MapieClassifier on the dataset to get prediction sets
clf = GaussianNB().fit(X_train, y_train)
y_pred = clf.predict(X_test)
y_pred_proba = clf.predict_proba(X_test)
y_pred_proba_max = np.max(y_pred_proba, axis=1)
mapie = MapieClassifier(estimator=clf, cv="prefit")
mapie.fit(X_train, y_train)
y_pred_mapie, y_pi_mapie = mapie.predict(X_test, alpha=alphas)

# Plot the results
tab10 = plt.cm.get_cmap('Purples', 4)
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
y_pred_col = [colors[int(i)] for _, i in enumerate(y_pred_mapie)]
y_train_col = [colors[int(i)] for _, i in enumerate(y_train)]
fig, axs = plt.subplots(1, 4, figsize=(20, 4))
axs[0].scatter(
    X_test[:, 0],
    X_test[:, 1],
    color=y_pred_col,
    marker='.',
    s=10,
    alpha=0.4
)
axs[0].scatter(
    X_train[:, 0],
    X_train[:, 1],
    color=y_train_col,
    marker='o',
    s=10,
    edgecolor='k'
)
axs[0].set_title("Predicted labels")
for i, alpha in enumerate(alphas):
    y_pi_sums = y_pi_mapie[:, :, i].sum(axis=1)
    num_labels = axs[i+1].scatter(
        X_test[:, 0],
        X_test[:, 1],
        c=y_pi_sums,
        marker='.',
        s=10,
        alpha=1,
        cmap=tab10,
        vmin=0,
        vmax=3
    )
    cbar = plt.colorbar(num_labels, ax=axs[i+1])
    axs[i+1].set_title(f"Number of labels for alpha={alpha}")
plt.show()
