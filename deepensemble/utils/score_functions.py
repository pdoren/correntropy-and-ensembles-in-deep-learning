import theano.tensor as T
import numpy as np
from ..utils.utils_functions import ITLFunctions

__all__ = [
    'dummy_score',
    'get_accuracy',
    'score_accuracy',
    'score_ensemble_ambiguity',
    'score_rms',
    'score_silverman',
    'mutual_information_cs',
    'mutual_information_ed',
    'mutual_information_parzen'
]


# noinspection PyUnusedLocal
def dummy_score(_input, _output, _target, model):
    """ Dummy score function, this function only return zeros for each elements in _target.

    Parameters
    ----------
    _input : theano.tensor.matrix
        Input Sample.

    _output : theano.tensor.matrix
        Output model.

    _target : theano.tensor.matrix
        Target Sample.

    model : Model
        Model.

    Returns
    -------
    theano.tensor.matrix
        Returns only zeros for each elements in _target.
    """
    return T.zeros(_target.shape)


#
# Classification Functions
#
def get_accuracy(Y, _target):
    # noinspection PyTypeChecker,PyTypeChecker
    return float(np.sum(Y == _target)) / float(_target.shape[0])


# noinspection PyUnusedLocal
def score_accuracy(_input, _output, _target, model):
    """ Accuracy score in a classifier models.

    Parameters
    ----------
    _input : theano.tensor.matrix
        Input sample.

    _output : theano.tensor.matrix
        Output sample.

    _target : theano.tensor.matrix
        Target sample.

    model : Model
        Model.

    Returns
    -------
    theano.tensor.matrix
        Returns accuracy in a classifier models.
    """
    return _target.shape[-1] * T.mean(_target * _output)


# noinspection PyUnusedLocal
def score_ensemble_ambiguity(_input, _output, _target, model):
    """ Score ambiguity for Ensemble.

    Parameters
    ----------
    _input : theano.tensor.matrix
        Input sample.

    _output : theano.tensor.matrix
        Output sample.

    _target : theano.tensor.matrix
        Target sample.

    model : Model
        Model.

    Returns
    -------
    float
        Returns a score ambiguity.
    """
    ensemble = model
    err = [T.mean(T.sqr(model.output(_input, prob=False) - _output)) for model in ensemble.get_models()]
    return sum(err) / ensemble.get_num_models()


# noinspection PyUnusedLocal
def score_silverman(_input, _output, _target, model):
    """ Score Silverman.

    Parameters
    ----------
    _input : theano.tensor.matrix
        Input sample.

    _output : theano.tensor.matrix
        Output sample.

    _target : theano.tensor.matrix
        Target sample.

    model : Model
        Model.

    Returns
    -------
    float
        Returns size kernel with Silverman Rule.
    """
    return ITLFunctions.silverman(model.output(_input))


#
# Regression Functions
#

# noinspection PyUnusedLocal
def score_rms(_input, _output, _target, model):
    """ Gets Root Mean Square like score in a regressor model.

    Parameters
    ----------
    _input : theano.tensor.matrix
        Input sample.

    _output : theano.tensor.matrix
        Output sample.

    _target : theano.tensor.matrix
        Target sample.

    model : Model
        Model.

    Returns
    -------
    theano.tensor.matrix
        Returns Root Mean Square.
    """
    return T.mean(T.power(_output - _target, 2.0))


# noinspection PyUnusedLocal
def mutual_information_cs(_input, _output, _target, model):
    """ Quadratic Mutual Information Cauchy-Schwarz

    Parameters
    ----------
    _input : theano.tensor.matrix
        Input sample.

    _output : theano.tensor.matrix
        Output sample.

    _target : theano.tensor.matrix
        Target sample.

    model : Model
        Model.

    Returns
    -------
    theano.tensor.matrix
        Returns Quadratic Mutual Information Cauchy-Schwarz.
    """
    s = ITLFunctions.silverman(_target)

    return ITLFunctions.mutual_information_cs([_output], _target, s)


# noinspection PyUnusedLocal
def mutual_information_ed(_input, _output, _target, model):
    """ Quadratic Mutual Information Euclidean.

    Parameters
    ----------
    _input : theano.tensor.matrix
        Input sample.

    _output : theano.tensor.matrix
        Output sample.

    _target : theano.tensor.matrix
        Target sample.

    model : Model
        Model.

    Returns
    -------
    theano.tensor.matrix
        Returns Quadratic Mutual Information Euclidean.
    """
    s = ITLFunctions.silverman(_target)

    return ITLFunctions.mutual_information_ed([_output], _target, s)


# noinspection PyUnusedLocal
def mutual_information_parzen(_input, _output, _target, model):
    """ Mutual Information (Parzen Window)

    Parameters
    ----------
    _input : theano.tensor.matrix
        Input sample.

    _output : theano.tensor.matrix
        Output sample.

    _target : theano.tensor.matrix
        Target sample.

    model : Model
        Model.

    Returns
    -------
    theano.tensor.matrix
        Returns Mutual Information (Parzen Window).
    """
    s = ITLFunctions.silverman(_target)

    return ITLFunctions.mutual_information_parzen(_output, _target, s)
