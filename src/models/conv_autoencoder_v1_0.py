#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
    *.py: Description of what * does.
    Last Modified:
"""

__author__ = "Debanjan Datta"
__email__ = "ddtta@vt.edu"
__version__ = "0.0.1"

import tensorflow as tf
import logging
import ipdb

log = logging.getLogger('root.convAE')


# ---------------------------------------------------#

class ConvAutoEncoder(object):
	def __init__(self,
				 vocab_size=24,
				 maxlen=2000,
				 batch_size = 128 ,
				 embedding_dim = 256
				 ):

		self.embedding_dim = embedding_dim
		self.batch_size = batch_size
		self.set_hyper_parameters()
		self.vocab_size = vocab_size
		self.maxlen = maxlen
		self.actvn_fn = tf.nn.tanh
		self.emb_matrix = None
		self.set_hyper_parameters()
		self.init_wts()
		self.build()

	# ------------------------- #
	# place layer parameters here
	# ------------------------- #
	def set_hyper_parameters(self):

		self.num_conv_layers = 3
		self.kernel_size = [
			[3, 2],
			[7, 5],
			[9, 5]
		]
		self.num_filters = [32, 16, 8]
		self.inp_channels = [1, 32, 16]

		self.strides = [
			[1, 1, 1, 1],
			[1, 1, 1, 1],
			[1, 1, 1, 1]
		]

	def get_variable(self, shape):
		with tf.name_scope('weight_or_bias'):
			initial = tf.truncated_normal(
				shape,
				stddev=0.1
			)
			return tf.Variable(initial)
		return

	def init_wts(self):
		# Weights for Embedding Layer
		self.embed_w = self.get_variable([self.vocab_size, self.embedding_dim])

		# Weights and biases for each of the convolutional layer
		self.conv_w = []
		self.conv_b = []
		for i in range(self.num_conv_layers):
			dim = [
				self.kernel_size[i][0],
				self.kernel_size[i][1],
				self.inp_channels[i],
				self.num_filters[i]
			]
			w_i = self.get_variable(dim)
			self.conv_w.append(w_i)
			dim = [self.num_filters[i]]
			b_i = self.get_variable(dim)
			self.conv_b.append(b_i)

	def build(self):
		self.build_input()
		self.build_encoder_decoder()
		self.build_train()

	def build_input(self):
		with tf.name_scope('model_input'):
			self.x = tf.placeholder(dtype=tf.int64, shape= [None, self.maxlen, self.vocab_size], name='x')
		return

	def build_encoder_decoder(self):

		with tf.name_scope('Encoder'):
			x = self.x
			x = tf.cast(x,tf.float32)
			print(' Embedding Matrix ', self.embed_w.shape)
			print(' Shape of x ',x.shape)
			emb_op = tf.einsum('ijk,kl->ijl', x, self.embed_w)
			self.emb_op = tf.expand_dims(emb_op,axis=3)
			cur_inp = self.emb_op

			conv_layer_ops = []
			for i in range(self.num_conv_layers) :
				_conv_i = tf.nn.conv2d(
					cur_inp,
					self.conv_w[i],
					strides=self.strides[i],
					padding='SAME'
				) + self.conv_b[i]
				conv_i = tf.nn.relu(_conv_i)
				print(conv_i)
				conv_layer_ops.append(conv_i)
				cur_inp = conv_i

		with tf.name_scope('Decoder'):
			deconv_layer_ops = []
			for i in range(self.num_conv_layers-1,-1,-1) :
				_strides = self.strides[i]
				op_shape = [self.batch_size]
				if i > 0:
					z = conv_layer_ops[i-1].get_shape().as_list()[1:4]
					op_shape.extend(z)
				else :
					z = [
						self.maxlen,
						self.embedding_dim,
						1
					]
					op_shape.extend(z)
				print('Op shape ' ,op_shape)
				dec_i = tf.nn.conv2d_transpose(
					value=conv_layer_ops[i],
					filter=self.conv_w[i],
					output_shape=op_shape,
					strides=_strides,
					padding="SAME"
				)
				print ( 'dec_i ->', dec_i)
				deconv_layer_ops.append(dec_i)

		dec_op = deconv_layer_ops[-1]
		cur_op = tf.squeeze(dec_op,axis=-1)
		print (' cur_op ' , cur_op.shape)
		rev_emb_op = tf.einsum('ijk,kl->ijl', cur_op,  tf.transpose(self.embed_w))
		self.final_op = rev_emb_op
		return


	def build_train (self):
		_x = tf.layers.flatten(self.x)
		_y = tf.layers.flatten(self.final_op)
		self.loss = tf.losses.mean_squared_error(_x,_y)
		self.optimizer = tf.train.AdamOptimizer(learning_rate=1e-5)
		self.train = self.optimizer.minimize(self.loss)

		return


m = ConvAutoEncoder(25,2000)
