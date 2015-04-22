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

import logging
import wx
from psysmon.core.plugins import OptionPlugin
from psysmon.core.guiBricks import PrefEditPanel
from psysmon.artwork.icons import iconsBlack16 as icons
import psysmon.core.preferences_manager as psy_pm
from obspy.core.utcdatetime import UTCDateTime
import wx.lib.mixins.listctrl as listmix
from wx.lib.stattext import GenStaticText as StaticText


class SelectEvents(OptionPlugin):
    '''

    '''
    nodeClass = 'TraceDisplay'

    def __init__(self):
        ''' Initialize the instance.

        '''
        OptionPlugin.__init__(self,
                              name = 'show events',
                              category = 'view',
                              tags = ['show', 'events']
                             )

        # Create the logging logger instance.
        loggerName = __name__ + "." + self.__class__.__name__
        self.logger = logging.getLogger(loggerName)

        self.icons['active'] = icons.pin_map_icon_16

        # Setup the pages of the preference manager.
        self.pref_manager.add_page('Select')
        self.pref_manager.add_page('Display')

        item = psy_pm.DateTimeEditPrefItem(name = 'start_time',
                                           label = 'start time',
                                           group = 'detection time span',
                                           value = UTCDateTime('2015-01-01T00:00:00'),
                                           tool_tip = 'The start time of the detection time span (UTCDateTime string format YYYY-MM-DDTHH:MM:SS).')
        self.pref_manager.add_item(pagename = 'Select',
                                   item = item)


        item = psy_pm.FloatSpinPrefItem(name = 'window_length',
                                        label = 'window length [s]',
                                        group = 'detection time span',
                                        value = 3600,
                                        limit = (0, 86400),
                                        digits = 1,
                                        tool_tip = 'The length of the time window for which events should be loaded.')
        self.pref_manager.add_item(pagename = 'Select',
                                   item = item)

        item = psy_pm.SingleChoicePrefItem(name = 'event_catalog',
                                          label = 'event catalog',
                                          group = 'event selection',
                                          value = '',
                                          limit = [],
                                          tool_tip = 'Select an event catalog for which to load the events.')
        self.pref_manager.add_item(pagename = 'Select',
                                   item = item)


        item = psy_pm.CustomPrefItem(name = 'events',
                                     label = 'events',
                                     group = 'event selection',
                                     value = [],
                                     gui_class = EventListField,
                                     tool_tip = 'The start time of the detection time span (UTCDateTime string format YYYY-MM-DDTHH:MM:SS).')
        self.pref_manager.add_item(pagename = 'Select',
                                   item = item)


        item = psy_pm.ActionItem(name = 'load_events',
                                 label = 'load events',
                                 group = 'detection time span',
                                 mode = 'button',
                                 action = self.on_load_events)
        self.pref_manager.add_item(pagename = 'Select',
                                   item = item)


        item = psy_pm.FloatSpinPrefItem(name = 'pre_et',
                                        label = 'pre event time [s]',
                                        group = 'display range',
                                        value = 5,
                                        limit = (0, 86400),
                                        digits = 1,
                                        tool_tip = 'The length of the time window to show before the event start.')
        self.pref_manager.add_item(pagename = 'Display',
                                   item = item)

        item = psy_pm.FloatSpinPrefItem(name = 'post_et',
                                        label = 'post event time [s]',
                                        group = 'display range',
                                        value = 10,
                                        limit = (0, 86400),
                                        digits = 1,
                                        tool_tip = 'The length of the time window to show after the event end.')
        self.pref_manager.add_item(pagename = 'Display',
                                   item = item)



    def buildFoldPanel(self, panelBar):
        ''' Create the foldpanel GUI.
        '''
        # Set the limits of the event_catalog field.
        self.load_catalogs()
        catalog_names = [x.name for x in self.catalogs]
        self.pref_manager.set_limit('event_catalog', catalog_names)
        if catalog_names:
            self.pref_manager.set_value('event_catalog', catalog_names[0])

        fold_panel = PrefEditPanel(pref = self.pref_manager,
                                  parent = panelBar)


        # Customize the events field.
        pref_item = self.pref_manager.get_item('events')[0]
        field = pref_item.gui_element[0]
        fold_panel.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_event_selected, field.controlElement)

        self.events_lb = field.controlElement

        return fold_panel


    def load_catalogs(self):
        ''' Load the event catalogs from the database.

        '''
        db_session = self.parent.project.getDbSession()
        try:
            cat_table = self.parent.project.dbTables['event_catalog'];
            query = db_session.query(cat_table.id,
                                     cat_table.name,
                                     cat_table.description,
                                     cat_table.agency_uri,
                                     cat_table.author_uri,
                                     cat_table.creation_time)
            self.catalogs = query.all()

        finally:
            db_session.close()


    def on_load_events(self, event):
        '''
        '''
        self.logger.debug('Loading events.')
        event_table = self.parent.project.dbTables['event']
        cat_table = self.parent.project.dbTables['event_catalog']
        db_session = self.parent.project.getDbSession()
        try:
            start_time = self.pref_manager.get_value('start_time')
            duration = self.pref_manager.get_value('window_length')
            catalog_name = self.pref_manager.get_value('event_catalog')
            query = db_session.query(event_table.id,
                                     event_table.start_time,
                                     event_table.end_time,
                                     event_table.public_id,
                                     event_table.description,
                                     event_table.agency_uri,
                                     event_table.author_uri,
                                     event_table.comment,
                                     event_table.tags).\
                                     filter(event_table.start_time >= start_time.timestamp).\
                                     filter(event_table.start_time <= (start_time + duration).timestamp).\
                                     filter(event_table.ev_catalog_id == cat_table.id).\
                                     filter(cat_table.name == catalog_name)

            events = query.all()
            pref_item = self.pref_manager.get_item('events')[0]
            field = pref_item.gui_element[0]
            field.set_events(events)


        finally:
            db_session.close()


    def on_event_selected(self, event):
        '''
        '''
        selected_row = event.m_itemIndex
        event_id = self.events_lb.GetItemText(selected_row)
        start_time = UTCDateTime(self.events_lb.GetItem(selected_row, 1).GetText())
        end_time = start_time + float(self.events_lb.GetItem(selected_row, 2).GetText())

        # Add the pre- and post event time.
        start_time -= self.pref_manager.get_value('pre_et')
        end_time += self.pref_manager.get_value('post_et')

        self.parent.displayManager.setTimeLimits(startTime = start_time,
                                                 endTime = end_time)
        self.parent.updateDisplay()



class EventListField(wx.Panel, listmix.ColumnSorterMixin):

    def __init__(self, name, pref_item, size, parent = None):
        '''
        '''
        wx.Panel.__init__(self, parent = parent, size = size, id = wx.ID_ANY)

        self.name = name

        self.pref_item = pref_item

        self.size = size

        self.label = name + ":"

        self.labelElement = None

        self.controlElement = None

        self.sizer = wx.GridBagSizer(5,5)

        # Create the field label.
        self.labelElement = StaticText(parent=self,
                                       ID=wx.ID_ANY,
                                       label=self.label,
                                       style=wx.ALIGN_LEFT)

        self.sizer.Add(self.labelElement, pos = (0,0), flag = wx.EXPAND|wx.ALL, border = 0)

        self.controlElement = EventListCtrl(parent = self, size = (200, 300),
                                            style = wx.LC_REPORT
                                            | wx.BORDER_NONE
                                            | wx.LC_SINGLE_SEL
                                            | wx.LC_SORT_ASCENDING)

        # The columns to show as a list to keep it in the correct order.
        self.columns = ['id', 'start_time', 'length', 'public_id',
                        'description', 'agency_uri', 'author_uri',
                        'comment']

        # The labels of the columns.
        self.column_labels = {'id': 'id',
                       'start_time': 'start time',
                       'length': 'length',
                       'public_id': 'public id',
                       'description': 'description',
                       'agency_uri': 'agency',
                       'author_uri': 'author',
                       'comment': 'comment'}

        # Methods for derived values.
        self.get_method = {'length': self.get_length}

        # Methods for values which should not be converted using the default
        # str function.
        self.convert_method = {'start_time': self.convert_to_isoformat}

        for k, name in enumerate(self.columns):
            self.controlElement.InsertColumn(k, self.column_labels[name])

        self.sizer.Add(self.controlElement, pos = (1,0), flag = wx.EXPAND|wx.ALL, border = 0)
        self.sizer.AddGrowableCol(0)
        self.sizer.AddGrowableRow(1)

        self.SetSizer(self.sizer)

    def __del__(self):
        self.pref_item.remove_gui_element(self)


    def set_events(self, events):
        '''
        '''
        self.controlElement.DeleteAllItems()
        for k, cur_event in enumerate(events):
            for n_col, cur_name in enumerate(self.columns):
                if cur_name in self.get_method.keys():
                    val = self.get_method[cur_name](cur_event)
                elif cur_name in self.convert_method.keys():
                    val = self.convert_method[cur_name](getattr(cur_event, cur_name))
                else:
                    val = str(getattr(cur_event, cur_name))

                if n_col == 0:
                    self.controlElement.InsertStringItem(k, val)
                else:
                    self.controlElement.SetStringItem(k, n_col, val)


    def convert_to_isoformat(self, val):
        return UTCDateTime(val).isoformat()

    def get_length(self, event):
        return str(event.end_time - event.start_time)






class EventListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    '''
    '''
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        ''' Initialize the instance.
        '''
        wx.ListCtrl.__init__(self, parent, id, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

        # Create the icons for column sorting.
        self.il = wx.ImageList(16, 16)
        self.sm_up = self.il.Add(wx.ArtProvider.GetBitmap(wx.ART_GO_UP, wx.ART_OTHER, (16,16)))
        self.sm_dn = self.il.Add(wx.ArtProvider.GetBitmap(wx.ART_GO_DOWN, wx.ART_OTHER, (16,16)))
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
