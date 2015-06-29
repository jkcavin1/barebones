__author__ = 'Lab Hatter'

from abc import ABCMeta, abstractmethod

class CommandBase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute(self):
        raise AttributeError("Can't inherit abstract class CommandBase without overriding method 'execute'.")
