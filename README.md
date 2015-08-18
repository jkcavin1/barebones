barebones
=========

A level editor capable of saving a graph to a pickle file which a programmer can easily rebuild in their custom format. It has the ability of undo/redo. No longer is there a need to procedurally position a Node through trial and error. Currently only positioning Models and Actors on the render graph is supported.  In the future, this will become a level-wide Pview (Panda's program for previewing Models and Actors). Soon, GUI editing will be supported, and later it will have the capability of adjusting color, transparency, parenting, and any other attribute of a Node or NodePath in pursuit of true WYSIWYG level editing using files and code you are already familiar with. It's purely Panda with no other libraries used, except Python's of course. Admittedly, it’s unpolished as of yet, but as they say, “Release early. Release often.”

Here's a demo of my widget plus undo/redo:
https://www.youtube.com/watch?v=CEyCf2z-qrc
