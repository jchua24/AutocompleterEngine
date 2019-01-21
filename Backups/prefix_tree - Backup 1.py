"""CSC148 Assignment 2: Autocompleter classes

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module Description ===
This file contains the design of a public interface (Autocompleter) and two
implementation of this interface, SimplePrefixTree and CompressedPrefixTree.
You'll complete both of these subclasses over the course of this assignment.

As usual, be sure not to change any parts of the given *public interface* in the
starter code---and this includes the instance attributes, which we will be
testing directly! You may, however, add new private attributes, methods, and
top-level functions to this file.
"""
from __future__ import annotations
from typing import Any, List, Optional, Tuple


################################################################################
# The Autocompleter ADT
################################################################################
class Autocompleter:
    """An abstract class representing the Autocompleter Abstract Data Type.
    """
    def __len__(self) -> int:
        """Return the number of values stored in this Autocompleter."""
        raise NotImplementedError

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this Autocompleter
                2) was previously inserted with the SAME prefix sequence
        """
        raise NotImplementedError

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        """
        raise NotImplementedError

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        """
        raise NotImplementedError


################################################################################
# SimplePrefixTree (Tasks 1-3)
################################################################################
class SimplePrefixTree(Autocompleter):
    """A simple prefix tree.

    This class follows the implementation described on the assignment handout.
    Note that we've made the attributes public because we will be accessing them
    directly for testing purposes.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - ("prefixes grow by 1")
      If len(self.subtrees) > 0, and subtree in self.subtrees, and subtree
      is non-empty and not a leaf, then

          subtree.value == self.value + [x], for some element x

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Any
    weight: float
    subtrees: List[SimplePrefixTree]


    #new private attributes
    _weight_type: str
    #used in the insert function
    _search_val: List[Any]
    #store the prefix lists of the leaf values
    _prefix_list: Optional[List[Any]]

    def __init__(self, weight_type: str) -> None:
        """Initialize an empty simple prefix tree.

        Precondition: weight_type == 'sum' or weight_type == 'average'.

        The given <weight_type> value specifies how the aggregate weight
        of non-leaf trees should be calculated (see the assignment handout
        for details).
        """

        self.value = []
        self.subtrees = []
        self.weight = 0.0
        self._weight_type = weight_type

        self._prefix_list = None


    def is_empty(self) -> bool:
        """Return whether this simple prefix tree is empty."""
        return self.weight == 0.0

    def is_leaf(self) -> bool:
        """Return whether this simple prefix tree is a leaf."""
        return self.weight > 0 and self.subtrees == []

    def __str__(self) -> str:
        """Return a string representation of this tree.

        You may find this method helpful for debugging.
        """
        return self._str_indented()

    def _str_indented(self, depth: int = 0) -> str:
        """Return an indented string representation of this tree.

        The indentation level is specified by the <depth> parameter.
        """
        if self.is_empty():
            return ''
        else:
            s = '  ' * depth + f'{self.value} ({self.weight})\n'
            for subtree in self.subtrees:
                s += subtree._str_indented(depth + 1)
            return s

    #added functions
    def __len__(self) -> int:
        """Return the number of values (leaves) stored in this Autocompleter."""
        if self.is_empty():
            return 0
        elif self.subtrees == []:
            return 1
        else:
            size = 0  # count the root
            for subtree in self.subtrees:
                size += len(subtree)
            return size

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this Autocompleter
                2) was previously inserted with the SAME prefix sequence
        """
        # root of the SimplePrefixTree
        if self.value == []:
            self._search_val = [prefix[0]]
            self.weight = weight  # starting weight that will be updated
            # sort subtrees
            self.sort_subtrees()

        common_prefix = self._search_val

        if len(prefix) == len(common_prefix):

            value_duplicate = False
            # check to see if the value has already been inserted into the tree
            for subtree in self.subtrees:
                if subtree.value == common_prefix:
                    # value already inserted into tree - only update weight
                    # update weight of final prefix sequence
                    subtree.weight += weight
                    # update weight of actual value
                    subtree.subtrees[0].weight += weight
                    # sort subtrees
                    self.sort_subtrees()

                    value_duplicate = True

            if not value_duplicate:
                # create tree for the last prefix sequence
                final_prefix = SimplePrefixTree(self._weight_type)
                final_prefix.value = prefix
                final_prefix.weight = weight

                self.subtrees.append(final_prefix)
                # sort subtrees
                self.sort_subtrees()

                # create tree for actual value
                value_tree = SimplePrefixTree(self._weight_type)
                value_tree.value = value
                value_tree.weight = weight

                # store the value of this leaf's prefix
                value_tree._prefix_list = prefix

                # add the created tree to the list of subtrees
                final_prefix.subtrees.append(value_tree)
                # SORT SUBTREES
                final_prefix.sort_subtrees()
        else:
            duplicate_found = False
            for subtree in self.subtrees:
                if subtree.value == common_prefix:
                    # duplicate found - common prefix already in the prefix tree
                    duplicate_found = True

                    # sort subtrees
                    self.sort_subtrees()

                    # RECURSIVE STEP - update common prefix and call insert
                    subtree._search_val = prefix[0: len(common_prefix) + 1]
                    subtree.insert(value, weight, prefix)
                    break

            # duplicate not found - common-prefix is not in the tree already
            if not duplicate_found:
                # create tree for this prefix
                prefix_tree = SimplePrefixTree(self._weight_type)
                # value of the prefix must be a list
                prefix_tree.value = prefix[0: len(common_prefix)]
                prefix_tree.weight = weight  # has same weight as original value

                # INSERT
                self.subtrees.append(prefix_tree)
                # sort subtrees
                self.sort_subtrees()

                # RECURSIVE STEP - update common prefix and call insert again
                prefix_tree._search_val = prefix[0: len(common_prefix) + 1]
                prefix_tree.insert(value, weight, prefix)
        # update weights of all trees and subtrees

        if self._weight_type == "sum":
            self.weight = self._leaf_weight()

        elif self._weight_type == "average":
            self.weight = (self._leaf_weight() / len(self))
        self.sort_subtrees()


    def sort_subtrees(self) -> None:
        """Sort the subtrees of the SimplePrefixTree in decreasing order."""
        sorted = False

        while not sorted:
            sorted = True
            for index in range(len(self.subtrees) -1):
                #check to see if a swap needs to be made
                if self.subtrees[index].weight < self.subtrees[index+1].weight:
                    sorted = False
                    temp = self.subtrees[index]
                    self.subtrees[index] = self.subtrees[index + 1]
                    self.subtrees[index + 1] = temp

    def _update_weight(self) -> None:
        """
        Update the weights of the base tree and all other subtrees
        """
        if self.value == []:
            if self._weight_type == "sum":
                self.weight = self._leaf_weight()

            elif self._weight_type == "average":
                if len(self) == 0:
                    #whole tree is empty:
                    self.weight = 0
                else:
                    self.weight = (self._leaf_weight() / len(self))

        for subtree in self.subtrees:
            if self._weight_type == "sum":
                subtree.weight = subtree._leaf_weight()

            elif self._weight_type == "average":
                if len(subtree) == 0:
                    self.subtrees.remove(subtree)
                else:
                    subtree.weight = subtree._leaf_weight() / len(subtree)

    def _leaf_weight(self) -> float:
        """Return total weight of leaves in the tree. This is a helper method
        for update weight.
        """
        if self.is_leaf():
            return self.weight
        else:
            total = 0
            for subtree in self.subtrees:
                total += subtree._leaf_weight()
            return total

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        """
        return_values = []

        if limit is None:
            if self.is_empty():
                return []
            elif self.subtrees == []:
                #if subtrees are empty, then this is a leaf
                #check to see if the leaf matches the given prefix
                if self._prefix_list is not None and \
                        self._prefix_list[0: len(prefix)] == prefix:
                    #returns list with tuple inside of it
                    return [(self.value, self.weight)]
                else:
                    return []
            else:
                for subtree in self.subtrees:
                    return_values += subtree.autocomplete(prefix, limit)

                return_values = sorted\
                    (return_values, key=lambda tup: -tup[1])
                return return_values
        else:
            if self.is_empty():
                return []
            elif self.subtrees == []:
                # if subtrees are empty, then this is a leaf
                # check to see if the leaf matches the given prefix
                if self._prefix_list is not None and \
                        self._prefix_list[0: len(prefix)] == prefix:
                    return [(self.value, self.weight)]
                else:
                    return []
            else:
                for subtree in self.subtrees:
                    to_add = subtree.autocomplete(prefix, limit)

                    if len(to_add) + len(return_values) < limit:
                        return_values += to_add
                    else:
                        return_values += to_add[0: limit - len(return_values)]
                return_values = sorted\
                    (return_values, key=lambda tup: (-tup[1]))
                return return_values

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        """
        self._prefix_list = list(self.value)
        if self.is_empty():
            pass
        elif self._prefix_list is not None and \
                self._prefix_list[0: len(prefix)] == prefix:
            # remove this whole subtree
            self.weight = 0.0
            self.value = []
            self.subtrees = []
        else:
            for subtree in self.subtrees:
                subtree._prefix_list = list(subtree.value)

                if subtree._prefix_list is not None and \
                subtree._prefix_list == prefix[0: len(subtree._prefix_list)]:
                    subtree.remove(prefix)

        #update weights of the tree and remove any empty trees remaining
        self._update_weight()

################################################################################
# CompressedPrefixTree (Task 6)
################################################################################
class CompressedPrefixTree(Autocompleter):
    """A compressed prefix tree implementation.

    While this class has the same public interface as SimplePrefixTree,
    (including the initializer!) this version follows the implementation
    described on Task 6 of the assignment handout, which reduces the number of
    tree objects used to store values in the tree.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - **NEW**
      This tree does not contain any compressible internal values.
      (See the assignment handout for a definition of "compressible".)

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Optional[Any]
    weight: float
    subtrees: List[CompressedPrefixTree]


if __name__ == '__main__':
    # import python_ta
    # python_ta.check_all(config={
    #     'max-nested-blocks': 4
    # })

    testing_tree = SimplePrefixTree("average")
    #testing_tree = SimplePrefixTree("sum")

    testing_tree.insert("chat", 2.0, ['c', 'h', 'a', 't'])

    testing_tree.insert("chm", 1.0, ['c', 'h', 'm'])

    testing_tree.insert("csc", 2.5, ['c', 's', 'c'])

    testing_tree.insert("mat", 1.0, ['m', 'a', 't'])

    testing_tree.insert("soc", 1.0, ['s', 'o', 'c'])

    testing_tree.insert("soy", 4.0, ['s', 'o', 'y'])

    testing_tree.insert("sup", 7.0, ['s', 'u', 'p'])

    # testing_tree.insert("ken", 5.0, ['k', 'e', 'n'])

    # testing_tree.insert("chat", 2.0, ['c', 'h', 'a', 't'])

    # testing_tree.insert("chaa", 4.0, ['c', 'h', 'a', 'a'])

    testing_tree.insert("csu", 7.0, ['c', 's', 'u'])

    # testing_tree.insert("chats", 5.0, ['c', 'h', 'a', 't','s'])


    #search_results = testing_tree.autocomplete([])
    #search_results = testing_tree.autocomplete(['c'], 4)
    # search_results = testing_tree.autocomplete(['c', 's'], 2)
    # search_results = testing_tree.autocomplete(['s'], 1)
    #print(search_results)

    print(testing_tree)
    #search_results = testing_tree.autocomplete([])
    #print(search_results)
    ##testing_tree.remove(['s', 'o'])
    #search_results = testing_tree.autocomplete([])
    #print(testing_tree)
    #print(search_results)
