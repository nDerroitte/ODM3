import matplotlib
#matplotlib.use("macOSX")
from matplotlib import pyplot as plt
from ddpg import *

class Plot:
    def __init__(self):
        self.__x = []
        self.__y1 = []
        self.__y2 = []

    def prepare_plot(self, sess, actor, action_dim, game, gui, episode_nb):
        """
        Prepare the plot of the overall computation

        Parameters
        -----------
        sess : A tensorflow session
        actor : Actor network (actor object)

        action_dim : int
                Dimension of the action-space
        game : catcher object
        gui : GUI object
        """
        # Run a simple simulation
        self.__x.append(episode_nb)
        fruits, reward = runSimple(game, sess, actor, action_dim, gui,
                                   episode_nb)
        self.__y1.append(fruits)
        self.__y2.append(reward)

    def make_plot(self):
        """
        Create the evolution plot
        """
        fig = plt.figure()
        print("Making the plots!")
        plt.plot(self.__x, self.__y1)
        plt.ylabel('Number of fruit catch')
        plt.xlabel('Number of episodes')
        plt.savefig('fruits.png')
        ######
        fig = plt.figure()
        plt.plot(self.__x, self.__y2)
        plt.ylabel('Total reward')
        plt.xlabel('Number of episodes')
        plt.savefig('reward.png')
        print("done")

def runSimple(game, sess, actor, action_dim, gui, episode_nb):
    print("==============================================================")
    print("Running a simulation for the plot with epsilon = 0.")
    d = False
    total_reward = 0
    while d == False:
        # Get observations
        states =  game.observe()
        # Generate the action
        act = getAction(sess, states, actor, 0, 0, action_dim, 0)
        # Perform the action2
        next_states, r, d = game.step(act[0])
        total_reward += r
        # Update GUI
        gui.updateGUI(game, episode_nb)
    # End loop print
    print("")
    print("Number of fruit catch : {}".format(game.nb_fruit_catch))
    print("Total reward: {}".format(total_reward))
    game.reset()
    return game.nb_fruit_catch, total_reward
