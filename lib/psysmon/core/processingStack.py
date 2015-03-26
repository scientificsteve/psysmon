# LICENSE
#
# This file is part of pSysmon.
#
# If you use pSysmon in any program or publication, please inform and
# acknowledge its author Stefan Mertl (stefan@mertl-research.at).
#
# pSysmon is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
The pSysmon processingStack module.

:copyright:
    Mertl Research GmbH

:license:
    GNU General Public License, Version 3 
    (http://www.gnu.org/licenses/gpl-3.0.html)

This module contains the pSysmon processingStack system.
'''

import copy
from psysmon.core.preferences_manager import PreferencesManager
from psysmon.core.guiBricks import PrefEditPanel

class ProcessingStack:
    ''' The ProcessingStack class.

    The processing stack handles the editing and execution of the processing nodes.
    Processing nodes can be added to the stack. The position in the stack can be 
    changed. 
    When executing the processing stack, each processing node contained in the stack 
    is executed from top to bottom. 
    The processing stack takes care about passing the correct data to the processingNode
    and to pass the processed data to the next processing node.
    '''
    def __init__(self, name, project, nodes = None):
        ''' The constructor

        '''
        # The name of the processing stack.
        self.name = name

        # The list of the processing nodes contained in the processing
        # stack.
        if nodes is None:
            self.nodes = []
        else:
            self.nodes = nodes

        # The current project.
        self.project = project


    @property
    def geometry_inventory(self):
        ''' The geometry inventory of the parent project.
        '''
        return self.project.geometry_inventory


    def __getitem__(self, index):
        ''' Get a node at a given position of the processing stack.

        Parameters
        ----------
        index : Integer
            The index of the collection node to get from the nodes list.
        '''
        return self.nodes[index]


    def addNode(self, nodeTemplate, position = -1):
        ''' Add a node to the processing stack.

        Insert a node before a specified position in the processing stack.
        If the position is set to -1, the node is appended at the end of the stack.

        Parameters
        ----------
        node : :class:`~psysmon.core.processingStack.ProcessingNode`
            The node to be added to the collection.
        position : Integer
            The position in the stack before which the node should be inserted.
        '''
        node = copy.deepcopy(nodeTemplate)
        node.parentStack = self
        if position==-1:
            self.nodes.append(node)
        else:
            self.nodes.insert(position, node)


    def popNode(self, position):
        ''' Remove a node from the stack.

        Parameters
        ----------
        position : Integer
            The position of the node which should be removed.
        '''
        if len(self.nodes) > 0:
            return self.nodes.pop(position)


    def editNode(self, position):
        ''' Edit a node.

        Edit the node at a given position in the stack. This is done by 
        calling the :meth:`~psysmon.core.processingStack.ProcessingNode.edit()` 
        method of the according instance.

        Parameters
        ----------
        position : Integer
            The position in the stack of the node to edit.
        '''
        self.nodes[position].edit()



    def execute(self, stream):
        ''' Execute the stack.

        Parameters
        ----------

        stream : :class:`obspy.core.Stream`
            The data to process.
        '''
        for curNode in self.nodes:
            curNode.clear_results()
            if curNode.isEnabled():
                curNode.execute(stream)


    def clear_results(self):
        ''' Clear the results of all processing nodes.
        '''
        for cur_node in self.nodes:
            cur_node.clear_results()





class ProcessingNode:
    ''' The ProcessingNode class.

    The processing node gets data from the processing stack, does some computation with 
    this data and returns the processed data to the processing stack.
    The type of data needed has to be defined by the ProcessingNode. Currently the processing 
    of obspy Stream objects is supported.
    The return value has to be of the same type as the data passed to the processing node.
    '''
    # The class to which the processing node is assigned to.
    # User *common* for nodes which can be used by every class.
    # Nodes with a specified nodeClass usually depend on some special 
    # variables which have to be passed to them using the variable kwargs 
    # argument.
    nodeClass = 'common'

    def __init__(self, name, mode, category, tags, enabled = True, docEntryPoint=None, parentStack=None):
        ''' The constructor

        '''
        # The name of the stack node.
        self.name = name

        # The mode of the stack node (editable, uneditable).
        self.mode = mode

        # The category of the stack node.
        self.category = category

        # The tags assigned to the stack node.
        self.tags = tags

        # The result of the processing node.
        self.results = {}

        # The preferences of the stack node.
        self.pref_manager = PreferencesManager()

        # The entry point of the documentation of the node.
        self.docEntryPoint = docEntryPoint

        # The parent stack holding the stack node.
        self.parentStack = parentStack

        # The enabled state of the node.
        self.enabled = enabled


    def isEnabled(self):
        ''' Check the enabled state of the node.

        '''
        return self.enabled



    def toggleEnabled(self):
        ''' Toggle the enabled state of the node.

        '''
        self.enabled = not self.enabled




    def getEditPanel(self, parent):
        ''' The method to build and return the edit panel for the processing 
        stack GUI.

        '''
        return PrefEditPanel(pref = self.pref_manager,
                             parent = parent)



    def execute(self, stream):
        ''' Execute the stack node.

        Parameters
        ----------
        stream : :class:`obspy.core.Stream`
            The data to process.
        '''
        assert False, 'execute must be defined'


    def update_pref_manager(self, pref_manager):
        ''' Update the existing preferences manager with the one passed as an argument.

        This is used when loading a psysmon project. The preference items are created
        during the instance initialization of the processing nodes.
        The values saved in the project file are not updated. The update is done
        using this method.
        '''
        self.pref_manager.update(pref_manager)



    def add_result(self, name, scnl, value, res_type = 'value',
                   custom_class = None):
        ''' Add a result.

        Parameters
        ----------
        result : object
            The result to add to the processing node results.

        res_type : String
            The type of the result to add. ('value', 'custom')

        custom_class : class inhereted from :class:`ProcessingResult`
            The custom class of a result of kind 'custom'.
        '''
        if name not in self.results.keys():
            if res_type == 'value':
                self.results[name] = ValueResult(name = name,
                                                 origin_name = self.name,
                                                 origin_pos = self.parentStack.nodes.index(self),
                                                 res_type = res_type)
            else:
                raise ValueError('The result of type %s is not supported.' % res_type)

        if self.results[name].type != res_type:
            raise ValueError("The type %s of the existing results doesn't match the type %s of the result to add." % (self.results[name].type, res_type))

        self.results[name].add_value(scnl = scnl, value = value)


    def clear_results(self):
        ''' Remove the results.
        '''
        self.results = {}


    def get_result_names(self):
        ''' Get the available result names.

        '''
        return list(set([x.name for x in self.results]))




class ResultBag(object):
    ''' A container holding results.
    '''

    def __init(self):
        ''' Initialize the instance.
        '''
        # A dictionary with the resource_ids as keys.
        self.results = {}


    def add_result(self, resource_id, result):
        ''' Add a result computed for a certain resource.
        '''
        if resource_id not in self.results.keys():
            self.results[resource_id] = {}

        result_id = (result.origin_name, result.origin_pos, result.name)
        self.results[resource_id][result_id] = result



class Result(object):
    ''' A result of a processing node.

    Processing nodes can produce results which are than stored in the
    processing stack for further use.
    The origin is a unique identifier of the processing node which created
    the result.
    When executing a processing stack several times in a loop, e.g when
    processing a list of events, the results of each loop can be
    added to an existing result of the same origin.
    '''

    def __init__(self, name, origin_name, origin_pos, res_type = None):
        ''' Initialize the instance.
        '''
        # The name of the result.
        self.name = name

        # The node which created the result.
        self.origin_name = origin_name

        # The position of the origin node in the stack.
        self.origin_pos = origin_pos

        # The result data.
        self.values = {}

        # The type of the result.
        self.type = res_type


    def add_value(self, scnl, value):
        ''' Add a value to the result.
        '''
        self.values[scnl] = value


    def get_as_list(self, scnl = None):
        ''' Get the results as a list.

        Parameters
        ----------
        scnl : List of tuples
            The SCNL codes for which to get the results.
            If scnl is None, all results are returned.

        Returns
        -------
        A list of results in the order of the scnl list.
        '''
        assert False, 'get_as_list must be defined'





class ValueResult(Result):
    ''' A result representing a single value.

    '''
    def __init__(self, **kwargs):
        ''' Initialize the instance.

        '''
        Result.__init__(self, **kwargs)


    def get_as_list(self, scnl = None):
        ''' Get the results as a list.

        Parameters
        ----------
        scnl : List of tuples
            The SCNL codes for which to get the results.
            If scnl is None, all results are returned.

        Returns
        -------
        A list of results in the order of the scnl list.
        '''
        if scnl is None:
            scnl = self.values.keys()

        return scnl, [self.values[key] for key in scnl]

