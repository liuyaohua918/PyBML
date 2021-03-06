# MIT License

# Copyright (c) 2020 Yaohua Liu

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from functools import reduce

import numpy as np
import scipy as sp
import scipy.sparse as sc_sp
import tensorflow as tf


def get_indices_balanced_classes(n_examples, labels, forbidden_indices):
    """
    :param n_examples: number of examples
    :param labels: paired labels
    :param forbidden_indices:
    :return:
    """
    N = len(labels)
    n_classes = len(labels[0])

    indices = []
    current_class = 0
    for i in range(n_examples):
        index = np.random.random_integers(0, N - 1, 1)[0]
        while (
            index in indices
            or index in forbidden_indices
            or np.argmax(labels[index]) != current_class
        ):
            index = np.random.random_integers(0, N - 1, 1)[0]
        indices.append(index)
        current_class = (current_class + 1) % n_classes

    return indices


def test_if_balanced(dataset):
    """
    :param dataset:
    :return: just for testing
    """
    labels = dataset.target
    n_classes = len(labels[0])
    class_counter = [0] * n_classes
    for l in labels:
        class_counter[np.argmax(l)] += 1
    print("exemple by class: ", class_counter)


def maybe_cast_to_scalar(what):
    """
    :param what: input
    :return: return the scalar of input if the length of input equals 1.
    """
    return what[0] if len(what) == 1 else what


def pad(_example, _size):
    """
    :param _example:
    :param _size:
    :return: performs concatenation
    """
    return np.concatenate([_example] * _size)


def stack_or_concat(list_of_arays):
    func = np.concatenate if list_of_arays[0].ndim == 1 else np.vstack
    return func(list_of_arays)


def merge_dicts(*dicts):
    return reduce(lambda a, nd: {**a, **nd}, dicts, {})


def vstack(lst):
    """
    Vstack that considers sparse matrices

    :param lst:
    :return:
    """
    return (
        sp.vstack(lst)
        if sp and isinstance(lst[0], sc_sp.csr.csr_matrix)
        else np.vstack(lst)
    )


def convert_sparse_matrix_to_sparse_tensor(X):
    """
    :param X: sparse matrix
    :return: sparse tensor of X
    """
    if isinstance(X, sc_sp.csr.csr_matrix):
        coo = X.tocoo()
        indices = np.mat([coo.row, coo.col]).transpose()
    else:
        coo, indices = X, [X.row, X.col]
    # data = np.array(coo.data, dtype=)
    return tf.SparseTensor(indices, tf.constant(coo.data, dtype=tf.float32), coo.shape)


def get_data(d_set):
    """
    :param d_set: instance of dataset
    :return: inputs of datasets
    """
    if hasattr(d_set, "images"):
        data = d_set.images
    elif hasattr(d_set, "data"):
        data = d_set.data
    else:
        raise ValueError("something wrong with the dataset %s" % d_set)
    return data


def get_targets(d_set):
    """
    :param d_set: instance of dataset
    :return: labels of datasets
    """
    if hasattr(d_set, "labels"):
        return d_set.labels
    elif hasattr(d_set, "target"):
        return d_set.target
    else:
        raise ValueError("something wrong with the dataset %s" % d_set)


def as_list(obj):
    """
    Makes sure `obj` is a list or otherwise converts it to a list with a single element.

    :param obj:
    :return: A `list`
    """
    return obj if isinstance(obj, list) else [obj]


def merge_dicts(*dicts):
    return reduce(lambda a, nd: {**a, **nd}, dicts, {})


def get_rand_state(rand):
    """
    Utility methods for getting a `RandomState` object.

    :param rand: rand can be None (new State will be generated),
                    np.random.RandomState (it will be returned) or an integer (will be treated as seed).

    :return: a `RandomState` object
    """
    if isinstance(rand, np.random.RandomState):
        return rand
    elif isinstance(rand, (int, np.ndarray, list)) or rand is None:
        return np.random.RandomState(rand)
    else:
        raise ValueError("parameter rand {} has wrong type".format(rand))


def maybe_call(obj, *args, **kwargs):
    """
    Calls obj with args and kwargs and return its result if obj is callable, otherwise returns obj.
    """
    if callable(obj):
        return obj(*args, **kwargs)
    return obj


def as_tuple_or_list(obj):
    """
    Make sure that `obj` is a tuple or a list and eventually converts it into a list with a single element

    :param obj:
    :return: A `tuple` or a `list`
    """
    return obj if isinstance(obj, (list, tuple)) else [obj]


def to_one_hot_enc(seq, dimension=None):
    """

    :param seq: sequence
    :param dimension: the dimension of output
    :return: output of one-hot encoding
    """
    da_max = dimension or int(np.max(seq)) + 1
    _tmp = np.zeros((len(seq), da_max))
    _tmp[range(len(_tmp)), np.array(seq, dtype=int)] = 1
    return _tmp

