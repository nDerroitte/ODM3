import numpy as np
from keras.layers import Input, Dense, Concatenate, Lambda
from keras.models import Model
from tensorflow.train import AdamOptimizer
from keras.layers.advanced_activations import PReLU

import tensorflow as tf


class ActorNetwork(object):
    def __init__(self, sess, state_dim, action_dim, GAMMA, TAU, MAX_F):
        """
        Parameters:
        -----------
        sess : A tensorflow session
        state_dim : int
            Number of dimension of the state-space
        action_dim : int
            Number of dimension of the action-space
        GAMMA: double
            Learning rate of the AdamOptimizer
        TAU : double
            Learning rate of the target network
        MAX_F: double
            Force maximum that we can apply to the board
        """
        self.__GAMMA = GAMMA
        self.__TAU = TAU
        self.__MAX_F = MAX_F

        self.__state_dim = state_dim
        self.__action_dim = action_dim

        self.model, self.state = self.__create_model()
        self.target_model, _ = self.__create_model()

        # Placeholder (var to be fed) for the action gradients
        self.action_grad_ph = tf.placeholder(tf.float32, [None, action_dim])
        # Get the gradient of output wrt trainable_weights.
        # action_gradient allow to start with different gradient for each
        # action
        # /!\ minus action_grad_ph because we need to do gradient ascent
        # and not gradient descent!!!
        delta_j = tf.gradients(self.model.output,  # dQ
                               self.model.trainable_weights,  # da
                               -self.action_grad_ph)  # dmu/dtheta
        gradients = zip(delta_j, self.model.trainable_weights)
        optim = AdamOptimizer(GAMMA)
        self.train_op = optim.apply_gradients(gradients)

        init = tf.global_variables_initializer()
        self.sess = sess
        self.sess.run(init)

    def train(self, states, action_gradients):
        """
        Allow to update the weights of the networks

        Parameters:
        -----------
        states : []
            List of the 4 elements composing the states
        action_gradient : Gradients used to update the weights
        """
        self.sess.run(self.train_op,
                      feed_dict={self.state: states,
                                 self.action_grad_ph: action_gradients})

    def predict(self, states):
        """
        Simple call of the predict function of the keras model for the actor
        Parameters:
        -----------
        states : []
            List of the 4 elements composing the states
        """
        return self.model.predict(states)

    def target_predict(self, states):
        """
        Simple call of the predict function of the keras model for the target
        network
        Parameters:
        -----------
        states : []
            List of the 4 elements composing the states
        """
        return self.target_model.predict(states)

    def target_train(self):
        """
        Update the weights of the target network based on the actor network
        weights. See report for more detail.
        """
        weights_model = self.model.get_weights()
        weights_target = self.target_model.get_weights()

        for i in range(len(weights_model)):
            weights_target[i] = (self.__TAU * weights_model[i]) + (
                                (1 - self.__TAU) * weights_target[i])
        self.target_model.set_weights(weights_target)

    def __create_model(self):
        """
        Create the actor model

        Returns:
        ---------
        keras Model : the actor network
        """
        try:
            input = Input(shape=(self.__state_dim, ))

            l1 = Dense(256, activation='relu')(input)
            l2 = Dense(512, activation='relu')(l1)

            output = Dense(1, activation='tanh')(l1)
            sc_output = Lambda(lambda x: x * self.__MAX_F)(output)


            return Model(inputs=input, outputs=sc_output), input

        except ValueError as e:
            print("""Error: couldn't create the
                     actor network :{}.""".format(e.strerror))
