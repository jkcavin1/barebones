__author__ = 'Lab Hatter'

from subprocess import call
import fileinput

class CommandLineModelConverter(object):
    def __init__(self):
        super(CommandLineModelConverter, self).__init__()

    def x2egg(self, argues, exe, stdout):
        call( argues, executable=exe,stdout=stdout)




if __name__ == '__main__':
    cmdLine = CommandLineModelConverter()
    cmdLine.x2egg(" -h", 'x2egg.exe','stdout.txt')