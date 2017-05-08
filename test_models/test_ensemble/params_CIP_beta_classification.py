import matplotlib
matplotlib.use('Qt4Agg')  # debug

import os

import matplotlib.pylab as plt
import numpy as np
from sklearn import model_selection

from deepensemble.utils import *
from deepensemble.utils.utils_functions import ActivationFunctions

plt.style.use('ggplot')

#############################################################################################################
# Load Data
#############################################################################################################
data_input, data_target, classes_labels, name_db, desc, col_names = load_data('germannumer_scale',
                                                                              data_home='../data', normalize=False)

input_train, input_test, target_train, target_test = \
    model_selection.train_test_split(data_input, data_target, test_size=0.3)

#############################################################################################################
# Define Parameters nets
#############################################################################################################

n_features = input_train.shape[1]
n_classes = len(classes_labels)

n_output = n_classes
n_inputs = n_features

fn_activation = ActivationFunctions.sigmoid

n_neurons = n_inputs + n_output

#############################################################################################################
# Define Parameters training
#############################################################################################################

max_epoch = 500
folds = 10
batch_size = 32
training = True

args_train_ncl = {'max_epoch': max_epoch, 'batch_size': batch_size, 'early_stop': False,
              'improvement_threshold': 0.995, 'update_sets': True}

args_train_cip = {'max_epoch': max_epoch, 'batch_size': batch_size, 'early_stop': False,
              'improvement_threshold': 0.995, 'update_sets': True, 'minibatch': True,
              'criterion_update_params': 'cost', 'maximization_criterion': True}

y = get_index_label_classes(translate_target(data_target, classes_labels))
silverman = ITLFunctions.silverman(np.array(y)).eval()

s_sigma = silverman

n_ensemble_models = 3


# ==========< Ensemble   >===================================================================================
def get_ensemble_ncl(_name, _param, fast=True):
    ensemble = get_ensembleNCL_model(name=_name,
                                     n_input=n_features, n_output=n_output,
                                     n_ensemble_models=n_ensemble_models, n_neurons_models=n_neurons,
                                     classification=True,
                                     classes_labels=classes_labels,
                                     fn_activation1=fn_activation, fn_activation2=fn_activation,
                                     lamb=_param, params_update={'learning_rate': 0.1})
    ensemble.compile(fast=fast)

    return ensemble


# noinspection PyUnusedLocal
def get_ensemble_cip_cs(_name, _param, fast=True):
    ensemble = get_ensembleCIP_model(name='Ensamble CIP',
                                    n_input=n_features, n_output=n_output,
                                    n_ensemble_models=n_ensemble_models, n_neurons_models=n_neurons,
                                    classification=True,
                                    is_cip_full=False,
                                    classes_labels=classes_labels,
                                    fn_activation1=fn_activation, fn_activation2=fn_activation,
                                    dist='CS',
                                    beta=_param, lamb=_param, s=s_sigma,
                                    lsp=1.5, lsm=0.5,
                                    lr=0.1,
                                    bias_layer=False, mse_first_epoch=True, annealing_enable=True,
                                    update=sgd, name_update='SGD',
                                    params_update={'learning_rate': -0.1}
                                    )

    ensemble.compile(fast=fast)

    return ensemble

def get_ensemble_cip_ed(_name, _param, fast=True):
    ensemble = get_ensembleCIP_model(name='Ensamble CIP',
                                    n_input=n_features, n_output=n_output,
                                    n_ensemble_models=n_ensemble_models, n_neurons_models=n_neurons,
                                    classification=True,
                                    is_cip_full=False,
                                    classes_labels=classes_labels,
                                    fn_activation1=fn_activation, fn_activation2=fn_activation,
                                    dist='ED',
                                    beta=_param, lamb=_param, s=s_sigma,
                                    lsp=1.5, lsm=0.1,
                                    lr=0.1,
                                    bias_layer=False, mse_first_epoch=True, annealing_enable=True,
                                    update=sgd, name_update='SGD',
                                    params_update={'learning_rate': -0.5}
                                    )

    ensemble.compile(fast=fast)

    return ensemble


#############################################################################################################
#  TEST
#############################################################################################################
parameters = [n for n in np.linspace(-1, 1, 21)]

list_ensemble = [(get_ensemble_cip_cs, 'Ensemble CIP CS', args_train_cip),
                 (get_ensemble_cip_ed, 'Ensemble CIP ED', args_train_cip),
                 (get_ensemble_ncl, 'Ensemble NCL', args_train_ncl)]
path_data = 'test_params_beta_cip/'

f, ax = plt.subplots()
plt.hold(True)

for get_ensemble, name, args_train in list_ensemble:

    data = {}
    scores = []

    if not os.path.exists(path_data):
        os.makedirs(path_data)
    Logger().log('Processing %s' % name)
    file_data = path_data + '%s_%s.pkl' % (name, name_db)

    if not os.path.exists(file_data):
        Logger().reset()
        for _p in Logger().progressbar(it=parameters, end='Finish'):
            Logger().log_disable()
            model = get_ensemble(_name=name, _param=_p)

            metrics, best_score, list_score = test_model(cls=model,
                                                         input_train=input_train, target_train=target_train,
                                                         input_test=input_test, target_test=target_test,
                                                         folds=folds, **args_train)

            scores.append(best_score)
            data[_p] = {'list_score': list_score}
            Logger().log_enable()

        scores = np.array(scores)
        s_data = Serializable((data, parameters, scores))
        s_data.save(file_data)
    else:
        Logger().log('Load file: %s' % file_data)
        s_data = Serializable()
        s_data.load(file_data)
        data, parameters, scores = s_data.get_data()

    #############################################################################################################
    #
    #  PLOT DATA CLASSIFIERS
    #
    #############################################################################################################

    list_dp = []
    for i in range(folds):
        y = list([data[l]['list_score'][i] for l in parameters])
        x = list(np.array(parameters))
        dp = DataPlot(name=name, _type='score')
        dp.set_data(x, y)
        list_dp.append(dp)

    plot_data(ax, [(list_dp, 'score')],
              x_max=max(parameters), x_min=min(parameters),
              title='%s Accuracy' % name)

plt.xlabel('$\\beta$')
plt.ylabel('score')
plt.tight_layout()

plt.show()
