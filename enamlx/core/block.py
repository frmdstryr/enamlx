"""
Created on Apr 15, 2017

@author: jrm
"""
from atom.api import ForwardInstance
from enaml.core.declarative import Declarative, d_


class Block(Declarative):
    """An object which dynamically insert's its children into another block's parent object.

    The 'Block' object is used to cleanly and easily insert it's children
    into the children of another object. The 'Object' instance assigned to the
    'object' property of the 'Block' will be parented with the parent of
    the 'Include'. Creating an 'Include' with no parent is a programming
    error.

    """

    #: The Block to which this blocks children should be inserted into
    block = d_(ForwardInstance(lambda: Block))

    def initialize(self):
        """A reimplemented initializer.

        This method will add the include objects to the parent of the
        include and ensure that they are initialized.

        """
        super(Block, self).initialize()
        if self.block:
            self.block.parent.insert_children(self.block, self.children)

    def _observe_block(self, change):
        """A change handler for the 'objects' list of the Include.

        If the object is initialized objects which are removed will be
        unparented and objects which are added will be reparented. Old
        objects will be destroyed if the 'destroy_old' flag is True.

        """
        if self.is_initialized:
            if change["type"] == "update":
                old_block = change["oldvalue"]
                old_block.parent.remove_children(old_block, self.children)
                new_block = change["value"]
                new_block.parent.insert_children(new_block, self.children)
