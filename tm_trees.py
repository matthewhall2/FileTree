"""Assignment 2: Trees for Treemap

=== CSC148 Winter 2019 ===
This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2019 Bogdan Simion, David Liu, Diane Horton, Jacqueline Smith

=== Module Description ===
This module contains the basic tree interface required by the treemap
visualiser. You will both add to the abstract class, and complete a
concrete implementation of a subclass to represent files and folders on your
computer's file system.
"""

from __future__ import annotations
import os
import math
from random import randint
from typing import List, Tuple, Optional


class TMTree:
    """A TreeMappableTree: a tree that is compatible with the treemap
    visualiser.

    This is an abstract class that should not be instantiated directly.

    You may NOT add any attributes, public or private, to this class.
    However, part of this assignment will involve you implementing new public
    *methods* for this interface.
    You should not add any new public methods other than those required by
    the client code.
    You can, however, freely add private methods as needed.

    === Public Attributes ===
    rect:
        The pygame rectangle representing this node in the treemap
        visualization.
    data_size:
        The size of the data represented by this tree.

    === Private Attributes ===
    _colour:
        The RGB colour value of the root of this tree.
    _name:
        The root value of this tree, or None if this tree is empty.
    _subtrees:
        The subtrees of this tree.
    _parent_tree:
        The parent tree of this tree; i.e., the tree that contains this tree
        as a subtree, or None if this tree is not part of a larger tree.
    _expanded:
        Whether or not this tree is considered expanded for visualization.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.

    - _colour's elements are each in the range 0-255.

    - If _name is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.

    - if _parent_tree is not None, then self is in _parent_tree._subtrees

    - if _expanded is True, then _parent_tree._expanded is True
    - if _expanded is False, then _expanded is False for every tree
      in _subtrees
    - if _subtrees is empty, then _expanded is False
    """

    rect: Tuple[int, int, int, int]
    data_size: int
    _colour: Tuple[int, int, int]
    _name: str
    _subtrees: List[TMTree]
    _parent_tree: Optional[TMTree]
    _expanded: bool

    def __init__(self, name: str, subtrees: List[TMTree],
                 data_size: int = 0) -> None:
        """Initialize a new TMTree with a random colour and the provided <name>.

        If <subtrees> is empty, use <data_size> to initialize this tree's
        data_size.

        If <subtrees> is not empty, ignore the parameter <data_size>,
        and calculate this tree's data_size instead.

        Set this tree as the parent for each of its subtrees.

        Precondition: if <name> is None, then <subtrees> is empty.
        """

        self.rect = (0, 0, 0, 0)
        self._name = name
        self._subtrees = subtrees[:]
        self._parent_tree = None
        self._colour = (randint(0, 255), randint(0, 255), randint(0, 255))

        # You will change this in Task 5
        if len(self._subtrees) > 0:
            self._expanded = False
        else:
            self._expanded = False

        if self._name is None:
            self.data_size = 0
        elif self._subtrees == []:
            self.data_size = data_size
        else:
            #  sets data_size equal to sum of sizes of its subtrees
            self.data_size = self._get_data_size()

        for i in range(len(self._subtrees)):
            self._subtrees[i]._parent_tree = self


    def _get_data_size(self)-> float:
        """
        returns the size of the tree
        """
        if self.is_empty():
            return 0
        elif self._subtrees == []:
            return self.data_size
        else:
            count = 0
            for subtrees in self._subtrees:
                count += subtrees._get_data_size()
            return count


    def is_empty(self) -> bool:
        """Return True iff this tree is empty.
        """
        return self._name is None

    def update_rectangles(self, rect: Tuple[int, int, int, int]) -> None:
        """Update the rectangles in this tree and its descendents using the
        treemap algorithm to fill the area defined by pygame rectangle <rect>.
        """
        x, y, width, height = rect
        self.rect = rect
        total_width = 0
        total_height = 0
        if self._name is None:
            self.rect = 0, 0, 0, 0
        elif self.data_size == 0:
            self.rect = x, y, 0, 0
        elif self._subtrees == []:
            self.rect = x, y, width, height
        else:
            for subtrees in self._subtrees:
                sub_size = subtrees.data_size
                total_size = self.data_size
                # ratio between subtree size and parents tree size
                data_size_ratio = sub_size / total_size
                if width > height:  # divide the width into smaller pieces
                    #
                    new_dim = math.floor(width * data_size_ratio)
                    # changes the width if its the last subtree
                    new_dim = subtrees._is_last(width, total_width, new_dim)

                    new_rec = (x, y, new_dim, height)
                    subtrees.update_rectangles(new_rec)
                    x += new_dim
                    total_width += new_dim
                elif width <= height:  # divide the height into smaller pieces
                    new_dim = math.floor(height * data_size_ratio)
                    # changes the height if its the last subtree
                    new_dim = subtrees._is_last(height, total_height, new_dim)

                    new_rec = (x, y, width, new_dim)
                    subtrees.update_rectangles(new_rec)
                    y += new_dim
                    total_height += new_dim


    def _is_last(self, width: int, total_width: int, new_width: int)-> int:
        """
        returns the amount needed to fill the input rectangle
        """
        tree_lst = self._parent_tree._subtrees
        if self is tree_lst[len(tree_lst) - 1]:
            # returns right dimension so it matches its parent tree
            return width - total_width
        return new_width


    def get_rectangles(self) -> List[Tuple[Tuple[int, int, int, int],
                                           Tuple[int, int, int]]]:
        """Return a list with tuples for every leaf in the displayed-tree
        rooted at this tree. Each tuple consists of a tuple that defines the
        appropriate pygame rectangle to display for a leaf, and the colour
        to fill it with.
        """
        rect_list = []
        if self.data_size == 0:
            return []
        elif not self._expanded:
            return [(self.rect, self._colour)]
        else:
            for subtrees in self._subtrees:
                rect_list.extend(subtrees.get_rectangles())
            return rect_list


    def get_tree_at_position(self, pos: Tuple[int, int]) -> Optional[TMTree]:
        """Return the leaf in the displayed-tree rooted at this tree whose
        rectangle contains position <pos>, or None if <pos> is outside of this
        tree's rectangle.

        If <pos> is on the shared edge between two rectangles, return the
        tree represented by the rectangle that is closer to the origin.
        """
        rects = self._list_rec(pos)
        dst = []
        if len(rects) == 0:
            return None
        elif len(rects) == 1:
            return rects[0]
        else:
            for items in rects:
                #  find the distance between the origin and the top left corner
                #  of this rectangle using using the pathagorean theorem
                dst.append(math.sqrt((items.rect[0] ** 2) + items.rect[1] ** 2))
            rec = min(dst)
            # this will be index of the rectangle closest to the origin
            ind = dst.index(rec)
            return rects[ind]


    def _list_rec(self, pos: Tuple[int, int])-> Optional[List[TMTree]]:
        """
        returns a list of rectangle that contain the tuple
        """
        rect_list = []
        if self.data_size == 0:
            return []
        elif not self._expanded:
            # if the tuple is in the rectangle
            if self._in_rec(pos):
                return [self]
            else:
                return []
        else:
            for subtrees in self._subtrees:
                rect_list.extend(subtrees._list_rec(pos))
            return rect_list

    def _in_rec(self, pos: Tuple[int, int])-> bool:
        """
        returns whether or not the tuple is in the specified rectangle
        """
        x, y, width, height = self.rect
        if (x <= pos[0] <= x + width) and y <= pos[1] <= y + height:
            return True
        else:
            return False


    def update_data_sizes(self) -> int:
        """Update the data_size for this tree and its subtrees, based on the
        size of their leaves, and return the new size.

        If this tree is a leaf, return its size unchanged.
        """
        if self.is_empty():
            return 0
        elif self._subtrees == []:
            return self.data_size
        else:
            self.data_size = 0
            for subtrees in self._subtrees:
                self.data_size += subtrees.update_data_sizes()
            return self.data_size


    def move(self, destination: TMTree) -> None:
        """If this tree is a leaf, and <destination> is not a leaf, move this
        tree to be the last subtree of <destination>. Otherwise, do nothing.
        """
        if self._subtrees == [] and len(destination._subtrees) > 0:
            destination._subtrees.append(self)
            self._parent_tree._subtrees.remove(self)
            if self._parent_tree._subtrees == []:
                self._parent_tree.data_size = 0
            self._parent_tree = destination


    def change_size(self, factor: float) -> None:
        """Change the value of this tree's data_size attribute by <factor>.

        Always round up the amount to change, so that it's an int, and
        some change is made.

        Do nothing if this tree is not a leaf.
        """
        if len(self._subtrees) == 0:
            new_size = math.ceil(self.data_size * (1 + factor))
            if new_size == self.data_size:
                if factor < 0 and self.data_size > 1:
                    self.data_size -= 1
                elif factor > 0:
                    self.data_size += 1
                else:
                    pass
            else:
                self.data_size = new_size


    def expand(self) -> None:
        """
        sets the is expanded value of this tree to true (if it has subtrees)
        """
        if len(self._subtrees) > 0:
            self._expanded = True
        else:
            self._expanded = False


    def collapse(self) -> None:
        """
        collapses this tree, as well as all of its subtrees by
        setting their _expanded attribute to False
        :return:
        """

        if self._parent_tree is not None:
            self._parent_tree._expanded = False
            self._parent_tree._collapse_children()


    def _collapse_children(self) -> None:
        """
        sets the _expanded attributes of all of this trees children, children's
        children etc to False
        """
        if len(self._subtrees) == 0:
            self._expanded = False
        else:
            self._expanded = False
            for subtrees in self._subtrees:
                subtrees._collapse_children()

    def expand_all(self)-> None:
        """
        expands all this tree as well as all of its subtrees
        """
        if len(self._subtrees) == 0:
            self._expanded = False
        else:
            self._expanded = True
            for subtrees in self._subtrees:
                subtrees.expand_all()

    def collapse_all(self)-> None:
        """
        collapses every element in the entire tree back to the root
        """
        tree = self
        while tree._parent_tree is not None:
            tree = tree._parent_tree
        tree._collapse_children()

    #  Methods for the string representation
    def get_path_string(self, final_node: bool = True) -> str:
        """Return a string representing the path containing this tree
        and its ancestors, using the separator for this tree between each
        tree's name. If <final_node>, then add the suffix for the tree.
        """
        if self._parent_tree is None:
            path_str = self._name
            if final_node:
                path_str += self.get_suffix()
            return path_str
        else:
            if self._name == ():
                raise IndexError
            path_str = (self._parent_tree.get_path_string(False) +
                        self.get_separator() + self._name)
            if final_node or len(self._subtrees) == 0:
                path_str += self.get_suffix()
            return path_str


    def get_separator(self) -> str:
        """Return the string used to separate names in the string
        representation of a path from the tree root to this tree.
        """
        raise NotImplementedError


    def get_suffix(self) -> str:
        """Return the string used at the end of the string representation of
        a path from the tree root to this tree.
        """
        raise NotImplementedError



class FileSystemTree(TMTree):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _name attribute stores the *name* of the folder or file, not its full
    path. E.g., store 'assignments', not '/Users/Diane/csc148/assignments'

    The data_size attribute for regular files is simply the size of the file,
    as reported by os.path.getsize.
    """

    def __init__(self, path: str) -> None:
        """Store the file tree structure contained in the given file or folder.

        Precondition: <path> is a valid path for this computer.
        """
        name = os.path.basename(path)
        subtree_lst = []

        # if path is a file or an empty folder
        if not os.path.isdir(path) or os.listdir(path) == []:
            TMTree.__init__(self, name, [], os.path.getsize(path))
        else:
            for filename in os.listdir(path):
                subitem = os.path.join(path, filename)
                item = FileSystemTree(subitem)
                subtree_lst.append(item)
            TMTree.__init__(self, name, subtree_lst)


    def get_separator(self) -> str:
        """Return the file separator for this OS.
        """
        return os.sep

    def get_suffix(self) -> str:
        """Return the final descriptor of this tree.
        """
        if len(self._subtrees) == 0:
            return ' (file)'
        else:
            return ' (folder)'




if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'math', 'random', 'os', '__future__'
        ]
    })
