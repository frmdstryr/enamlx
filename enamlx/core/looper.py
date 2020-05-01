# -*- coding: utf-8 -*-
'''
Created on Aug 29, 2015

Looper that only shows visible elements

@author: jrm
'''
from atom.api import Instance, ContainerList, List, observe
from enaml.core.looper import Looper, sortedmap, new_scope, recursive_expand
from enaml.core.declarative import d_
from enamlx.widgets.abstract_item_view import AbstractItemView

class ListLooper(Looper):
    """ A looper handles ContainerList updates """

    items = ContainerList()

    _expanded = List()

    def _observe_iterable(self, change):
        if not self.is_initialized:
            return
        elif change['type'] == 'update':
            self.refresh_items()
        elif change['type'] == 'container':
            if change['operation'] == 'append':
                self.append_items([change['item']])
            elif change['operation'] == 'extend':
                self.append_items(change['items'])
            elif change['operation'] == 'insert':
                self.insert_item(change['index'],change['item'])
            elif change['operation'] == 'remove':
                self.remove_items([change['item']])
            elif change['operation'] == 'pop':
                self.pop_item(change['index'])
            elif change['operation'] in ['reverse','sort']:
                self.refresh_items()

    def remove_items(self,old_items):
        for item in old_items:
            index = self.items.index(item)
            self.pop_item(index)

    def pop_item(self,index):
        for iteration in self.items.pop(index):
            for old in iteration:
                if not old.is_destroyed:
                    old.destroy()

    def insert_item(self,loop_index,loop_item):

        iteration = []
        self._iter_data[loop_item] = iteration
        for nodes, key, f_locals in self.pattern_nodes:
            with new_scope(key, f_locals) as f_locals:
                f_locals['loop_index'] = loop_index
                f_locals['loop_item'] = loop_item
                for node in nodes:
                    child = node(None)
                    if isinstance(child, list):
                        iteration.extend(child)
                    else:
                        iteration.append(child)

        expanded = []
        recursive_expand(sum([iteration], []), expanded)
        # Where do I insert it!
        self.parent.insert_children(self, expanded)

        self.items.insert(loop_index,iteration)

    def append_item(self,item):
        self.insert_item(len(self.items),item)

    def refresh_items(self):
        """ Refresh the items of the pattern.

        This method destroys the old items and creates and initializes
        the new items.

        """
        old_items = self.items[:]# if self._dirty else []
        old_iter_data = self._iter_data# if self._dirty else {}
        iterable = self.iterable
        pattern_nodes = self.pattern_nodes
        new_iter_data = sortedmap()
        new_items = []

        if iterable is not None and len(pattern_nodes) > 0:
            for loop_index, loop_item in enumerate(iterable):
                iteration = old_iter_data.get(loop_item)
                if iteration is not None:
                    new_iter_data[loop_item] = iteration
                    new_items.append(iteration)
                    old_items.remove(iteration)
                    continue
                iteration = []
                new_iter_data[loop_item] = iteration
                new_items.append(iteration)
                for nodes, key, f_locals in pattern_nodes:
                    with new_scope(key, f_locals) as f_locals:
                        f_locals['loop_index'] = loop_index
                        f_locals['loop_item'] = loop_item
                        for node in nodes:
                            child = node(None)
                            if isinstance(child, list):
                                iteration.extend(child)
                            else:
                                iteration.append(child)

        for iteration in old_items:
            for old in iteration:
                if not old.is_destroyed:
                    old.destroy()

        if len(new_items) > 0:
            expanded = []
            recursive_expand(sum(new_items, []), expanded)
            self._expanded = expanded
            self.parent.insert_children(self, expanded)

        self.items = new_items
        self._iter_data = new_iter_data

class ItemViewLooper(Looper):
    """ A looper that only creates the objects
    in the visible window.

    """
    item_view = d_(Instance(AbstractItemView))

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('item_view.iterable')
    def _observe_iterable(self, change):
        super(ItemViewLooper, self)._observe_iterable(change)

    def _observe_item_view(self, change):
        """ A private observer for the `window_size` attribute.

        If the iterable changes while the looper is active, the loop
        items will be refreshed.

        """
        self.iterable = self.item_view.iterable

    @observe('item_view.iterable_index','item_view.iterable_fetch_size',
             'item_view.iterable_prefetch')
    def _refresh_window(self, change):
        if change['type'] == 'update' and self.is_initialized:
            self.refresh_items()

    @observe('item_view.visible_rect')
    def _prefetch_items(self,change):
        """ When the current_row in the model changes (whether from scrolling) or
        set by the application. Make sure the results are loaded!

        """
        if self.is_initialized:
            view = self.item_view

            upper_limit = view.iterable_index+view.iterable_fetch_size-view.iterable_prefetch
            lower_limit = max(0,view.iterable_index+view.iterable_prefetch)
            offset = int(view.iterable_fetch_size/2.0)
            upper_visible_row = view.visible_rect[2]
            lower_visible_row = view.visible_rect[0]
            print("Visible rect = %s"%view.visible_rect)

            if upper_visible_row >= upper_limit:
                next_index = max(0,upper_visible_row-offset) # Center on current row
                # Going up works...
                if next_index>view.iterable_index:
                    print("Auto prefetch upper limit %s!"%upper_limit)
                    view.iterable_index = next_index
                    #view.model().reset()

            # But doewn doesnt?
            elif view.iterable_index>0 and lower_visible_row < lower_limit:
                next_index = max(0,lower_visible_row-offset) # Center on current row
                # Going down works
                if next_index<view.iterable_index:
                    print("Auto prefetch lower limit=%s, iterable=%s, setting next=%s!"%(lower_limit,view.iterable_index,next_index))
                    view.iterable_index = next_index
                    #view.model().reset()

    @property
    def windowed_iterable(self):
        """ That returns only the window """
        # Seek to offset
        effective_offset = max(0,self.item_view.iterable_index)
        for i,item in enumerate(self.iterable):
            if i<effective_offset:
                continue
            elif i>=(effective_offset+self.item_view.iterable_fetch_size):
                return
            yield item

    def refresh_items(self):
        """ Refresh the items of the pattern.

        This method destroys the old items and creates and initializes
        the new items.

        """
        old_items = self.items[:]# if self._dirty else []
        old_iter_data = self._iter_data# if self._dirty else {}
        iterable = self.windowed_iterable
        pattern_nodes = self.pattern_nodes
        new_iter_data = sortedmap()
        new_items = []

        if iterable is not None and len(pattern_nodes) > 0:
            for loop_index, loop_item in enumerate(iterable):
                iteration = old_iter_data.get(loop_item)
                if iteration is not None:
                    new_iter_data[loop_item] = iteration
                    new_items.append(iteration)
                    old_items.remove(iteration)
                    continue
                iteration = []
                new_iter_data[loop_item] = iteration
                new_items.append(iteration)
                for nodes, key, f_locals in pattern_nodes:
                    with new_scope(key, f_locals) as f_locals:
                        f_locals['loop_index'] = loop_index
                        f_locals['loop_item'] = loop_item
                        for node in nodes:
                            child = node(None)
                            if isinstance(child, list):
                                iteration.extend(child)
                            else:
                                iteration.append(child)

        # Add to old items list
        #self.old_items.extend(old_items)

        #if self._dirty:
        for iteration in old_items:
            for old in iteration:
                if not old.is_destroyed:
                    old.destroy()

        if len(new_items) > 0:
            expanded = []
            recursive_expand(sum(new_items, []), expanded)
            self.parent.insert_children(self, expanded)

        self.items = new_items# if self._dirty else new_items+old_items
        self._iter_data = new_iter_data
