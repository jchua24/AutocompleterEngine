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

    #store sum value of leaves in this tree
    _leaf_total: int

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

        self._leaf_total = 0

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

            #empty prefix case
            if prefix == []:
                self._search_val = []
            else:
                self._search_val = [prefix[0]]

            self.weight = weight  # starting weight that will be updated
            # sort subtrees
            self.sort_subtrees()
            self._leaf_total += weight

        common_prefix = self._search_val

        if len(prefix) == len(common_prefix):

            value_duplicate = False
            # check to see if the value has already been inserted into the tree
            for subtree in self.subtrees:
                if subtree.value == common_prefix:
                    leaf_exists, leaf_index, value_duplicate = False, -1, True

                    #for loop
                    for subtree_index in range(len(subtree.subtrees)):
                        if subtree.subtrees[subtree_index].is_leaf() and \
                                subtree.subtrees[subtree_index].value == value:
                            leaf_index, leaf_exists = subtree_index, True

                    if leaf_exists and leaf_index != -1:
                        # first case: value already inserted into tree
                        # update weight of final prefix sequence
                        subtree._leaf_total += weight
                        subtree.subtrees[leaf_index].weight += weight
                        subtree.subtrees[leaf_index]._leaf_total += weight
                        subtree._update_weights()
                        # if subtree._weight_type == "sum":
                        #     subtree.weight = subtree._leaf_total
                        # elif subtree._weight_type == "average":
                        #     subtree.weight = subtree._leaf_total / len(subtree)
                        self.sort_subtrees()
                        break
                    else:
                        # second case: prefixes are the same but no leaf
                        # create leaf
                        subtree._leaf_total += weight

                        #create new leaf tree and add it
                        # leaf = SimplePrefixTree(self._weight_type)
                        # leaf.value = value
                        # leaf.weight = weight
                        # leaf._leaf_total = weight
                        leaf = self._final_leaf(value, weight, prefix)
                        subtree.subtrees.append(leaf)

                        subtree._update_weights()
                        # if subtree._weight_type == "sum":
                        #     subtree.weight = subtree._leaf_total
                        # elif subtree._weight_type == "average":
                        #     subtree.weight = subtree._leaf_total / len(subtree)
                        self.sort_subtrees()

                        break

                elif subtree._prefix_list == []:
                    #empty prefix list case
                    if subtree.value == value:
                        #duplicate found
                        value_duplicate = True
                        subtree._leaf_total += weight
                        subtree.weight += weight

            if not value_duplicate:

                if prefix == []:
                    #inserting into root case

                    # create tree for actual value
                    # value_tree = SimplePrefixTree(self._weight_type)
                    # value_tree.value = value
                    # value_tree.weight = weight
                    # value_tree._leaf_total = weight
                    value_tree = self._final_leaf(value, weight, prefix)

                    # store the value of this leaf's prefix
                    self.subtrees.append(value_tree)
                    self.sort_subtrees()
                else:

                    # create tree for the last prefix sequence
                    # final_prefix = SimplePrefixTree(self._weight_type)
                    # final_prefix.value = prefix
                    # final_prefix.weight = weight
                    # final_prefix._leaf_total = weight
                    final_prefix = self._new_tree(prefix, weight)

                    self.subtrees.append(final_prefix)
                    # sort subtrees
                    self.sort_subtrees()
                    value_tree = self._final_leaf(value, weight, prefix)

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

                    subtree.weight += weight
                    subtree._leaf_total += weight

                    # sort subtrees
                    self.sort_subtrees()

                    # RECURSIVE STEP - update common prefix and call insert
                    subtree._search_val = prefix[0: len(common_prefix) + 1]
                    subtree.insert(value, weight, prefix)
                    break

            # duplicate not found - common-prefix is not in the tree already
            if not duplicate_found:
                # create tree for this prefix

                prefix_tree = self._new_tree\
                    (prefix[0: len(common_prefix)], weight)
                # prefix_tree = SimplePrefixTree(self._weight_type)
                # prefix_tree.value = prefix[0: len(common_prefix)]
                # prefix_tree.weight = weight  # has same weight as original value
                #
                # prefix_tree._leaf_total = weight
                # INSERT
                self.subtrees.append(prefix_tree)
                # sort subtrees
                self.sort_subtrees()

                # RECURSIVE STEP - update common prefix and call insert again
                prefix_tree._search_val = prefix[0: len(common_prefix) + 1]
                prefix_tree.insert(value, weight, prefix)
        # update weights of all trees and subtrees

        self._update_weights()
        self.sort_subtrees()

    def _new_tree(self, prefix, weight) -> SimplePrefixTree:
        """create a new simple prefix tree with specifications"""
        final_prefix = SimplePrefixTree(self._weight_type)
        final_prefix.value = prefix
        final_prefix.weight = weight
        final_prefix._leaf_total = weight
        return final_prefix

    def _final_leaf(self, value, weight, prefix) -> SimplePrefixTree:
        """create a final leaf with just the value in it"""
        value_tree = SimplePrefixTree(self._weight_type)
        value_tree.value = value
        value_tree.weight = weight
        value_tree._leaf_total = weight
        value_tree._prefix_list = prefix
        return value_tree

    def _update_weights(self) -> None:
        """ Update Weights of self """

        if self._weight_type == "sum":
            self.weight = self._leaf_total
        elif self._weight_type == "average":
            self.weight = self._leaf_total / len(self)

    def sort_subtrees(self) -> None:
        """Sort the subtrees of the SimplePrefixTree in decreasing order."""
        is_sorted = False

        while not is_sorted:
            is_sorted = True
            for index in range(len(self.subtrees) -1):
                #check to see if a swap needs to be made
                if self.subtrees[index].weight < self.subtrees[index+1].weight:
                    is_sorted = False
                    temp = self.subtrees[index]
                    self.subtrees[index] = self.subtrees[index + 1]
                    self.subtrees[index + 1] = temp

    def _remove_empty(self) -> None:
        """
        Remove empty trees from this tree
        """
        if self.value == [] and len(self) == 0:
            self.weight = 0
        elif self.value == []:
            for item in self.subtrees:
                if item.weight == 0:
                    self.subtrees.remove(item)

        for subtree in self.subtrees:
            # if self._weight_type == "average" and len(subtree) == 0:
            if len(subtree) == 0:
                self.subtrees.remove(subtree)
            else:
                subtree._remove_empty()


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
            elif self._prefix_list is not None and \
                    self._prefix_list[0: len(prefix)] == prefix and \
                    self.is_leaf():
                return [(self.value, self.weight)]
            elif self.subtrees == []:
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
            elif self._prefix_list is not None and \
                        self._prefix_list[0: len(prefix)] == prefix and \
                    self.is_leaf() and limit >= 1:
                return [(self.value, self.weight)]
            elif self.subtrees == []:
                return []
            else:
                for subtree in self.subtrees:
                    to_add = subtree.autocomplete\
                        (prefix, limit - len(return_values))

                    if len(to_add) + len(return_values) < limit:
                        return_values += to_add
                    else:
                        return_values += to_add[0: limit - len(return_values)]
                        break
                return_values = sorted(return_values, key=lambda tup: (-tup[1]))

                return return_values

    def remove(self, prefix: List) -> None:
        """ Remove all values that match the given prefix.
        Uses a helper function to find the weight of the desired item in order
        remove it, but also update the weights more efficiently
        """

        item_weight = self._find_weight(prefix)

        if item_weight != 0.0:
            if not self.is_leaf():
                self._prefix_list = self.value

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
                if self.value == []:
                    self._leaf_total -= item_weight

                for subtree in self.subtrees:
                    if not subtree.is_leaf():
                        subtree._prefix_list = list(subtree.value)

                    if subtree._prefix_list is not None and \
                    subtree._prefix_list == \
                            prefix[0: len(subtree._prefix_list)]:
                        # update leaf total values so weights can be calculated
                        # after
                        subtree._leaf_total -= item_weight
                        subtree.remove(prefix)
                        # don't go into the other subtrees afterwards
                        break

                # need to calculate weights here, after recursion
                if self._weight_type == "sum":
                    self.weight = self._leaf_total
                else:
                    #weight type is average
                    length = len(self)
                    if length != 0:
                    # length decreases by 1 because the leaf will be removed
                        self.weight = self._leaf_total / (length)

        self._remove_empty()
        self.sort_subtrees()

    def _find_weight(self, prefix: List) -> float:
        """ find the weight of the leaf value that matches this prefix
        """
        self._prefix_list = list(self.value)

        if self.is_empty():
            pass
        elif self._prefix_list is not None and \
                self._prefix_list[0: len(prefix)] == prefix:
            #return the weight of the item, multiplied by # of leaves
            if self._weight_type == "sum":
                return self.weight
            else:
                return self.weight * len(self)
        else:
            for subtree in self.subtrees:
                subtree._prefix_list = list(subtree.value)

                if subtree._prefix_list is not None and \
                        subtree._prefix_list == \
                        prefix[0: len(subtree._prefix_list)]:
                    return subtree._find_weight(prefix)
        #if prefix is not in the tree
        return 0.0


################################################################################
# CompressedPrefixTree (Task 6)
################################################################################
class CompressedPrefixTree(SimplePrefixTree):
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

    # new private attributes
    _weight_type: str
    # used in the insert function
    _search_val: List[Any]
    # store the prefix lists of the leaf values
    _prefix_list: Optional[List[Any]]


    # store sum value of leaves in this tree
    _leaf_total: int

    def __init__(self, weight_type: str) -> None:

        SimplePrefixTree.__init__(self, weight_type)

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """DOCSTRING"""

        if self.value == []:
            #case for when the root is empty and/or when the tree is empty
            self.insert_normal(value, weight, prefix)
        else:

            temp = self._copy()

            self.subtrees = [temp]
            self.value = []
            self.insert_normal(value, weight, prefix)



    def insert_normal(self, value: Any, weight: float, prefix: List) -> None:
        """DOCSTRING """
        if self.value == []:
            self._leaf_total += weight
            self.weight = self._leaf_total  #starting weight will be updated
            # sort subtrees
            self.sort_subtrees()

        duplicate_found = False
        if prefix == []:
            max_len = 1
            tree = self
            self._leaf_total -= weight
        else:
            max_len = 0
            tree = None
            for subtree in self.subtrees:
                # find subtree with longest common prefix
                if subtree.is_leaf():
                    i = CompressedPrefixTree._pt_of_diff(self, prefix)
                    if i > max_len:
                        max_len = i
                        tree = subtree
                else:
                    i = CompressedPrefixTree._pt_of_diff(subtree, prefix)
                    if i > max_len:
                        max_len = i
                        tree = subtree
        if max_len > 0:
            duplicate_found = True
            common_prefix = prefix[:max_len]

            if tree.value == prefix:

                leaf_exists, same_leaf = False, False
                leaf_index = -1
                leaf_value = []

                # for loop
                for tree_index in range(len(tree.subtrees)):
                    if tree.subtrees[tree_index].is_leaf():
                        leaf_index = tree_index
                        leaf_exists = True
                        leaf_value.append(tree.subtrees[tree_index])
                for val in leaf_value:
                    if val.value == value:
                        same_leaf = True
                        break
                if (not same_leaf) and leaf_exists:
                    # same prefix sequence and the values are different
                    # new value tree
                    tree._leaf_total += weight
                    leaf = CompressedPrefixTree(self._weight_type)
                    #leaf.value = value
                    leaf.value, leaf.weight, leaf._leaf_total,\
                    leaf._prefix_list = value, weight, weight, prefix
                    #leaf._prefix_list = prefix
                    tree.subtrees.append(leaf)

                    if self._weight_type == "sum":
                        tree.weight = tree._leaf_total
                    elif self._weight_type == "average":
                        tree.weight = tree._leaf_total / len(tree)

                elif leaf_exists and (leaf_index != -1):
                    # value already inserted into tree - only update weight
                    # update weight of final prefix sequence

                    tree.weight += weight
                    tree._leaf_total += weight
                    i = tree.subtrees.index(val)
                    tree.subtrees[i].weight += weight
                    tree.subtrees[i]._leaf_total += weight

                    if self._weight_type == "sum":
                        tree.weight = tree._leaf_total
                    elif self._weight_type == "average":
                        tree.weight = tree._leaf_total / len(tree)

                    self.sort_subtrees()

                else:
                    # prefixes are the same but no leaf, create leaf
                    tree._leaf_total += weight

                    # create new leaf tree and add it
                    leaf = CompressedPrefixTree(self._weight_type)
                    leaf.value = value
                    leaf.weight = weight
                    leaf._leaf_total = weight
                    leaf._prefix_list = prefix
                    tree.subtrees.append(leaf)

                    if self._weight_type == "sum":
                        tree.weight = tree._leaf_total
                    elif self._weight_type == "average":
                        tree.weight = tree._leaf_total / len(tree)

                    tree.sort_subtrees()
                    self.sort_subtrees()

            elif self.value == common_prefix:
                duplicate_found = False

            elif tree.value == common_prefix:
                tree.weight += weight
                tree._leaf_total += weight
                tree.insert_normal(value, weight, prefix)
                tree.sort_subtrees()

            elif tree.is_leaf():
                duplicate_found = False
            else:
                if duplicate_found:
                    # create tree for common prefix
                    prefix_tree = CompressedPrefixTree(self._weight_type)
                    prefix_tree.value = common_prefix
                    prefix_tree.weight = weight + tree.weight
                    prefix_tree._leaf_total = weight + tree._leaf_total

                    # prefix_tree._prefix_list = prefix #TODO ADDED
                    self.subtrees.append(prefix_tree)
                    self.subtrees.remove(tree)
                    self.sort_subtrees()

                    prefix_tree.subtrees.append(tree)

                    if common_prefix != prefix:
                        # create tree with the rest of prefix and a value tree
                        new_tree = self._final_prefix(weight, prefix, value)
                        prefix_tree.subtrees.append(new_tree)
                    else:
                        # just create a value tree
                        value_tree = CompressedPrefixTree(self._weight_type)
                        value_tree.value = value
                        value_tree.weight, value_tree._leaf_total = \
                            weight, weight
                        value_tree._prefix_list = prefix
                        prefix_tree.subtrees.append(value_tree)

                    # update weights of all trees and subtrees
                    if self._weight_type == "sum":
                        prefix_tree.weight = prefix_tree._leaf_total
                    elif self._weight_type == "average":
                        prefix_tree.weight = prefix_tree._leaf_total /\
                                             len(prefix_tree)

                    prefix_tree.sort_subtrees()

        # duplicate not found - insert a compressed tree
        if not duplicate_found:
            prefix_tree = self._final_prefix(weight, prefix, value)
            self.subtrees.append(prefix_tree)
            self.sort_subtrees()

        # update weights of all trees and subtrees
        if self._weight_type == "sum":
            self.weight = self._leaf_total
        elif self._weight_type == "average":
            self.weight = self._leaf_total / len(self)
        self.sort_subtrees()

        if self.value == [] and len(self.subtrees) == 1 and \
                not self.subtrees[0].is_leaf():
            self.value, self.weight, self.subtrees = self.subtrees[0].value, \
                                                     self.subtrees[0].weight, \
                                                     self.subtrees[0].subtrees

    def _copy(self) -> CompressedPrefixTree:
        """Returns an identical copy of """
        new_tree = CompressedPrefixTree(self._weight_type)
        new_tree.value = self.value
        new_tree.weight = self.weight
        new_tree._leaf_total = self._leaf_total
        new_tree._weight_type = self._weight_type

        new_subtrees = []

        for subtree in self.subtrees:
            new_subtrees.append(subtree)

        new_tree.subtrees.extend(new_subtrees)
        # print("new tree is")
        # print(new_tree)
        return new_tree

    def _final_prefix(self, weight: float, prefix: List, value: Any) \
            -> CompressedPrefixTree:
        """Create a new Compressed Prefix Tree with a value tree as subtree"""
        prefix_tree = CompressedPrefixTree(self._weight_type)
        prefix_tree.value = prefix
        prefix_tree.weight, prefix_tree._leaf_total = weight, weight

        # create tree for actual value
        value_tree = CompressedPrefixTree(self._weight_type)
        value_tree.value = value
        value_tree.weight, value_tree._leaf_total = weight, weight
        value_tree._prefix_list = prefix

        # add the created tree to the subtrees of parent
        prefix_tree.subtrees.append(value_tree)
        return prefix_tree


    @staticmethod
    def _pt_of_diff(subtree: CompressedPrefixTree, prefix: List) -> int:
        i = 0
        while i < len(prefix) and i < len(subtree.value):
            if prefix[i] == subtree.value[i]:
                i += 1
            else:
                return i
        return i

    def remove(self, prefix: List) -> None:
        """ Remove all values that match the given prefix.
        Uses a helper function to find the weight of the desired item in order
        remove it, but also update the weights more efficiently
        """

        item_weight = self._find_weight(prefix)

        if item_weight != 0.0:
            if not self.is_leaf():
                self._prefix_list = self.value
            else:
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
                if self.value == []:
                    self._leaf_total -= item_weight

                for subtree in self.subtrees:
                    if not subtree.is_leaf():
                        subtree._prefix_list = list(subtree.value)

                    if not subtree.is_leaf() and \
                            subtree._prefix_list is not None and \
                            subtree._prefix_list \
                            == prefix[0: len(subtree._prefix_list)]:
                        # update leaf total values
                        subtree._leaf_total -= item_weight
                        subtree.remove(prefix)
                        # don't go into the other subtrees afterwards
                        break
                    elif not subtree.is_leaf() and \
                            subtree._prefix_list is not None \
                            and subtree._prefix_list[0: len(prefix)] == prefix:
                        subtree.weight = 0.0
                        subtree.value = []
                        subtree.subtrees = []
                        break

                # need to calculate weights here, after recursion occurs
                if self._weight_type == "sum":
                    self.weight = self._leaf_total
                else:
                    # weight type is average
                    if len(self) != 0:
                        self.weight = self._leaf_total / len(self)

        self._remove_empty()
        self.sort_subtrees()
        if self.value == [] and len(self.subtrees) == 1 and \
                not self.subtrees[0].is_leaf():
            self.value, self.weight, self.subtrees = self.subtrees[0].value, \
                                                     self.subtrees[0].weight, \
                                                     self.subtrees[0].subtrees
    def _find_weight(self, prefix: List) -> float:
        """ find the weight of the first value that has prefix list as a prefix
        """
        self._prefix_list = list(self.value)

        if self.is_empty():
            pass
        elif self._prefix_list is not None and \
                self._prefix_list[0: len(prefix)] == prefix:
            # return the weight of the item, multiplied by # of leaves
            if self._weight_type == "sum":
                return self.weight
            else:
                length = len(self)
                return self.weight * length
        else:
            for subtree in self.subtrees:
                subtree._prefix_list = list(subtree.value)

                if not subtree.is_leaf() and subtree._prefix_list \
                        is not None and subtree._prefix_list ==\
                        prefix[0: len(subtree._prefix_list)]:
                    return subtree._find_weight(prefix)

                elif not subtree.is_leaf() and subtree._prefix_list \
                        is not None and \
                        subtree._prefix_list[0: len(prefix)] == prefix:
                    return subtree._find_weight(prefix)

        # if prefix is not in the tree
        return 0.0


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'max-nested-blocks': 4
    })


    # #TODO test 5
    test_tree = CompressedPrefixTree('sum')
    #tree.insert('ROOT LEAF', 17, [])
    test_tree.insert('hey', 3, ['h', 'e', 'y'])
    test_tree.insert('heyhey', 4, ['h', 'e', 'y', 'h', 'e', 'y'])

    test_tree.insert('h', 2, ['h'])

    test_tree.insert('cat', 4, ['c', 'a', 't'])



    # tree.remove(['c', 'a', 't'])
    # tree.remove(['c', 'a', 't'])
    #
    # tree.remove(['h'])
    #
    #
    # tree.insert('fob', 5, list('fob'))
    # tree.remove(list('f'))
    #tree.insert('h', 2, ['h'])

    #tree.remove(['h'])
    print(test_tree)
