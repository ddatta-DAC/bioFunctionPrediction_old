#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
    *.py: Description of what * does.
    Last Modified:
"""

__author__ = "Sathappan Muthiah"
__email__ = "sathap1@vt.edu"
__version__ = "0.0.1"


import tensorflow as tf
from tensorflow import keras
import logging
from collections import deque
# from keras.callbacks import EarlyStopping, ModelCheckpoint
# from keras import backend as K
# from keras.models import Sequential, Model, load_model
# from keras.layers import (
    # Dense, Dropout, Activation, Input,
    # Flatten, Highway, merge, BatchNormalization)
# from keras.layers.embeddings import Embedding
# from keras.layers.convolutional import (
#     Convolution1D, MaxPooling1D)

log = logging.getLogger('root.deepgo')

BIOLOGICAL_PROCESS = 'GO:0008150'
MOLECULAR_FUNCTION = 'GO:0003674'
#CELLULAR_COMPONENT = 'GO:0005575'
FUNC_DICT = { #'cc': CELLULAR_COMPONENT,
              'mf': MOLECULAR_FUNCTION,
              'bp': BIOLOGICAL_PROCESS}



class KerasDANQ(object):
    def __init__(self, functions, root, godag, maxlen, ngramsize):
        self.functions = functions
        self.root = root
        self.godag = godag
        self.inputs = None
        self.model = None
        self.maxlen = maxlen
        self.func_set = set(functions)
        self.ngramsize = ngramsize

    def get_feature_model(self):
        embedding_dims = 128
        max_features = self.ngramsize
        model = keras.models.Sequential()
        model.add(keras.layers.Embedding(
            max_features,
            embedding_dims,
            input_length=self.maxlen
        )) #dropout=0.2))
        model.add(keras.layers.Convolution1D(
            filters=320,
            kernel_size=26,
            padding='valid',
            activation='relu',
            strides=1))
        model.add(keras.layers.MaxPooling1D(pool_size=13, strides=13))
        model.add(keras.layers.Dropout(0.2))
        model.add(keras.layers.Bidirectional(keras.layers.LSTM(110)))
        model.add(keras.layers.Dropout(0.5))
        model.add(keras.layers.Flatten())
        model.add(keras.layers.Dense(925, activation='relu'))
        model.add(keras.layers.Flatten())
        return model

    def get_node_name(self, go_id, unique=False):
        #log.info('name-{}'.format(go_id))
        name = go_id.split(':')[1]
        return name

    def get_function_node(self, name, inputs):
        output_name = name + '_o'
        # var = tf.get_variable(name, shape=[self.inputs.shape[-1], 1], dtype=tf.float32)
        # bias = tf.get_variable('{}_b'.format(name), shape=[1], dtype=tf.float32)
        # output = tf.sigmoid(tf.matmul(self.inputs, var) + bias, name='{}_out'.format(name))
        output = keras.layers.Dense(1, name=output_name, activation='sigmoid')(inputs)
        return output, output

    def get_layers(self, inputs):
        q = deque()
        layers = {}
        if self.root == '':
            for fn in FUNC_DICT:
                layers[FUNC_DICT[fn]] = {'net': inputs}
                q.append((FUNC_DICT[fn], inputs))
        # else:
            # layers[FUNC_DICT[self.root]] = {'net': inputs}

        else:
            for fn in [FUNC_DICT[self.root]]:
                for node_id in self.godag.isagraph.successors(fn):
                    if node_id in self.func_set:
                        q.append((node_id, inputs))

        log.info('creating tree')
        while len(q) > 0:
            node_id, net = q.popleft()
            parent_nets = [inputs]
            name = self.get_node_name(node_id)
            net, output = self.get_function_node(name, inputs)
            if node_id not in layers:
                layers[node_id] = {'net': net, 'output': output}
                for n_id in self.godag.isagraph.successors(node_id):
                    if n_id in self.func_set and n_id not in layers:
                        ok = True
                        for p_id in self.godag.isagraph.predecessors(n_id):
                            if p_id in self.func_set and p_id not in layers:
                                ok = False
                        if ok:
                            q.append((n_id, net))

        log.info('finished tree, layers-{}, functions-{}'.format(len(layers), len(self.functions)))
        for node_id in self.functions:
            childs = set(self.godag.isagraph.successors(node_id)).intersection(self.func_set)
            if node_id not in layers:
                name = self.get_node_name(node_id)
                net, output = self.get_function_node(name, inputs)
                layers[node_id] = {'net': net, 'output': output}

            if len(childs) > 0:
                outputs = [layers[node_id]['output']]
                for ch_id in childs:
                    if ch_id not in layers:
                        name = self.get_node_name(ch_id)
                        net, output = self.get_function_node(name, inputs)
                        layers[ch_id] = {'net': net, 'output': output}

                    outputs.append(layers[ch_id]['output'])
                name = self.get_node_name(node_id) + '_max'
                layers[node_id]['output'] = keras.layers.maximum(outputs)

        log.info('tree len {}'.format(len(layers)))
        return layers


    def build(self):
        log.info("Building the model")
        log.info('funtion-{}'.format(self.root))
        inputs = keras.layers.Input(shape=(self.maxlen,), dtype='int32', name='i1')
        feature_model = self.get_feature_model()(inputs)
        net = keras.layers.Dense(1024, activation='relu')(feature_model)
        layers = self.get_layers(net)
        output_models = []
        delete = []
        for i in range(len(self.functions)):
            try:
                output_models.append(layers[self.functions[i]]['output'])
            except:
                print("func deleted")
                log.info('function {} not found'.format(functions[i]))
                delete.append(i)

        print("hello how are you")
        for i in delete:
            self.functions.pop(i)

        net = keras.layers.concatenate(output_models, axis=1)
        model = keras.models.Model(inputs=inputs, outputs=net)
        log.info('Compiling the model')
        # optimizer = keras.optimizers.RMSprop()
        optimizer = keras.optimizers.Adam()

        model.compile(
            optimizer=optimizer,
            loss='binary_crossentropy')
        log.info(
            'Compilation finished')
        return model
