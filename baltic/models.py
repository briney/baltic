#!/usr/bin/env python
# filename: models.py
#
# Inspiration: https://github.com/evogytis/baltic
# License: GNU General Public License v3.0 (https://opensource.org/licenses/GPL-3.0)
#


from typing import Union, Literal


class BaseTreeObject:
    """
    docstring for BaseTreeObject
    """

    def __init__(self):
        self._name = None
        self._branch_type = None
        self._length = None
        self._width = None
        self._height = None
        self._absolute_time = None
        self._parent = None
        self._traits = {}
        self._index = None
        self._x = None
        self._y = None

    @property
    def name(self) -> Union[str, None]:
        """
        object name
        """
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def branch_type(self) -> Union[str, None]:
        """
        Options are 'node' or 'leaf'
        """
        return self._branch_type

    @branch_type.setter
    def branch_type(self, branch_type: Literal["node", "leaf"]):
        self._branch_type = branch_type

    @property
    def length(self) -> float:
        """
        branch length
        """
        return self._length

    @length.setter
    def length(self, length: float):
        self._length = length

    @property
    def width(self) -> Union[float, int, None]:
        """
        branch width
        """
        return self._width

    @width.setter
    def width(self, width: float):
        self._width = width

    @property
    def height(self) -> Union[float, int, None]:
        """
        height, set by traversing the tree, which adds up branch lengths along the way
        """
        return self._height

    @height.setter
    def height(self, height: float):
        self._height = height

    @property
    def absolute_time(self):
        """
        branch end point in absolute time, once calibrations are done
        """
        return self._absolute_time

    @absolute_time.setter
    def absolute_time(self, absolute_time):
        self._absolute_time = absolute_time

    @property
    def parent(self):
        """
        reference to parent object
        """
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    @property
    def traits(self) -> dict:
        """
        dictionary that will contain annotations from the tree string, e.g. {'posterior':1.0}
        """
        return self._traits

    @traits.setter
    def traits(self, traits: dict):
        self._traits = traits

    @property
    def index(self) -> Union[float, int, None]:
        """
        index of the character designating this object in the tree string 
        it's a unique identifier for every object in the tree
        """
        return self._index

    @index.setter
    def index(self, index: int):
        self._index = index

    @property
    def x(self) -> Union[float, int, None]:
        """
        X coordinate of the object, once draw_tree() is called
        """
        return self._x

    @x.setter
    def x(self, x: float):
        self._x = x

    @property
    def y(self) -> Union[float, int, None]:
        """
        Y coordinate of the object, once draw_tree() is called
        """
        return self._y

    @y.setter
    def y(self, y: float):
        self._y = y

    def is_leaflike(self):
        return False

    def is_leaf(self):
        return False

    def is_node(self):
        return False


class Node(BaseTreeObject):
    """
    docstring for Node
    """

    def __init__(self):
        super(Node, self).__init__()
        self.branch_type = "node"
        self.length = 0.0  ## branch length, recovered from string
        self.children = []  ## a list of descendent branches of this node
        self.child_height = None  ## the youngest descendant tip of this node
        ## contains references to all tips of this node
        self.leaves = set()  ## is a set of tips that are descended from it

    def is_node(self):
        return True


class Leaf(BaseTreeObject):
    """
    docstring for Leaf
    """

    def __init__(self):
        super(Leaf, self).__init__()
        self.branchType = "leaf"

    def is_leaflike(self):
        return False

    def is_leaf(self):
        return True

    def is_node(self):
        return False


class Clade(BaseTreeObject):
    """
    docstring for Clade
    """

    def __init__(self, name: str):
        super(Clade, self).__init__()
        self.name = name  ## the pretend tip name for the clade
        self.branch_type = "leaf"  ## clade class poses as a leaf
        self.subtree = None
        self.leaves = None
        self.length = 0.0
        self.width = 1
        ## refers to the height of the highest tip in the collapsed clade
        self.last_height = None
        ## refers to the absolute time of the highest tip in the collapsed clade
        self.last_absolute_time = None

    def is_leaflike(self):
        return True


class Reticulation(BaseTreeObject):
    """
    reticulation class (recombination, conversion, reassortment)
    """

    def __init__(self, name):
        super(Reticulation, self).__init__()
        self.name = name
        self.branch_type = "leaf"
        self.length = 0.0
        self.height = 0.0
        self.width = 0.5
        self.target = None

    def is_leaflike(self):
        return True

