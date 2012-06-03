

import logging
import time
import wx
import wx.lib.graphics
from wx.lib.stattext import GenStaticText as StaticText
from wx.lib.pubsub import Publisher as pub
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import wx.lib.scrolledpanel as scrolled
from matplotlib.figure import Figure
import numpy as np


class TdViewAnnotationPanel(wx.Panel):
    '''
    The view annotation area.

    This area can be used to plot anotations for the view. This might be 
    some statistic values (e.g. min, max), the axes limits or some 
    other custom info.
    '''
    def __init__(self, parent, size=(50,-1), color=None):
        wx.Panel.__init__(self, parent, size=size)
        self.SetBackgroundColour(color)


	# Create a test label.
        label = StaticText(self, wx.ID_ANY, "view annotation area", (20, 10))
        font = wx.Font(6, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL)
        label.SetFont(font)

	# Add the label to the sizer.
	sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(label, 1, wx.EXPAND|wx.ALL, border=0)
	self.SetSizer(sizer)

        #print label.GetAlignment()


class PlotPanel(wx.Panel):
    """
    The PlotPanel
    """
    def __init__( self, parent, color=None, dpi=None, **kwargs ):
        # initialize Panel
        if 'id' not in kwargs.keys():
            kwargs['id'] = wx.ID_ANY
        if 'style' not in kwargs.keys():
            kwargs['style'] = wx.NO_FULL_REPAINT_ON_RESIZE
        wx.Panel.__init__( self, parent, **kwargs )
        self.SetMinSize((100, 40))

        # initialize matplotlib stuff
        self.figure = Figure(None, dpi=dpi, facecolor='white')
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.canvas.SetMinSize((30, 10))
        self.SetBackgroundColour('blue')

	# Add the canvas to the sizer.
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.EXPAND)
        self.SetSizer(self.sizer)

        self.canvas.Bind(wx.EVT_SET_FOCUS, self.onSetFocus)
        self.Bind(wx.EVT_SET_FOCUS, self.onSetFocus2)
        self.canvas.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)

        #self.canvas.Disable()
        #self.Disable()

    def onSetFocus(self, event):
        print "Canvas got Focus"
        print "Event should propagate: %s" % event.ShouldPropagate()
        #event.ResumePropagation(1)
        event.Skip()

    def onSetFocus2(self, event):
        print "PlotPanel got Focus"
    
    def onKeyDown(self, event):
        print "Propagating keyDown in plotPanel"
        event.ResumePropagation(1)
        event.Skip()


    def SetColor( self, rgbtuple=None ):
        """Set figure and canvas colours to be the same."""
        if rgbtuple is None:
            rgbtuple = wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ).Get()
        clr = [c/255. for c in rgbtuple]
        self.figure.set_facecolor( clr )
        self.figure.set_edgecolor( clr )
        self.canvas.SetBackgroundColour( wx.Colour( *rgbtuple ) )
        self.canvas.Refresh()



class TdView(wx.Panel):
    '''
    The tracedisplay view container.
    '''
    def __init__(self, parent=None, id=wx.ID_ANY, parentViewport=None, name=None):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour('green')

        self.plotCanvas = PlotPanel(self, color=(255,255,255))
        self.annotationArea = TdViewAnnotationPanel(self, color='gray80')

        self.SetMinSize(self.plotCanvas.GetMinSize())

        sizer = wx.GridBagSizer(0,0)
        sizer.Add(self.plotCanvas, pos=(0,0), flag=wx.ALL|wx.EXPAND, border=0)
        sizer.Add(self.annotationArea, pos=(0,1), flag=wx.ALL|wx.EXPAND, border=1)
	sizer.AddGrowableRow(0)
	sizer.AddGrowableCol(0)
	self.SetSizer(sizer)

        self.name = name

        self.parentViewport = parentViewport

        # Create the view data axes.
        #self.dataAxes = self.plotCanvas.figure.add_axes([0.1,0.1,0.8,0.8])
        self.dataAxes = self.plotCanvas.figure.add_axes([0,0,1,1])
        
        self.Bind(wx.EVT_ENTER_WINDOW, self.onEnterWindow)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.onLeaveWindow)
        self.Bind(wx.EVT_SET_FOCUS, self.onSetFocus)
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)

        #self.Bind(wx.EVT_SIZE, self._onSize)
    
    def draw(self):
        ''' Draw the canvas to make the changes visible.
        '''
        self.plotCanvas.canvas.draw()
    
    
    def onEnterWindow(self, event):
        print "Entered view."
        #self.plotCanvas.SetColor((0,255,255))
        self.SetBackgroundColour('blue')
        self.Refresh()
    
    def onLeaveWindow(self, event):
        print "Entered view."
        self.SetBackgroundColour('green')
        self.Refresh()

    def onSetFocus(self, event):
        print "view got focus."

    def onKeyDown(self, event):
        event.ResumePropagation(1)
        event.Skip()

    def _onSize( self, event ):
        event.Skip()
        #print "view resize"
        #print "view size: " + str(self.GetSize())
        #print "view parent: " + str(self.GetParent())
        #print "view parent size: " + str(self.GetParent().GetSize())
        #self.annotationArea.Resize()
        self.plotCanvas.Resize()


class TdSeismogramView(TdView):
    '''
    A standard seismogram view.

    Display the data as a timeseries.
    '''

    def __init__(self, parent=None, id=wx.ID_ANY, parentViewport=None, name=None, lineColor=(1,0,0)):
        TdView.__init__(self, parent=parent, id=id, parentViewport=parentViewport, name=name)

        # The logging logger instance.
        loggerName = __name__ + "." + self.__class__.__name__
        self.logger = logging.getLogger(loggerName)

        self.t0 = None
	self.lineColor = [x/255.0 for x in lineColor]

        self.line = None


    def plot(self, trace):

        start = time.clock()
        #endTime = trace.stats.starttime + (trace.stats.npts * 1/trace.stats.sampling_rate)
        timeArray = np.arange(0, trace.stats.npts)
        timeArray = timeArray * 1/trace.stats.sampling_rate
        timeArray = timeArray + trace.stats.starttime.timestamp
        #timeArray = np.arange(trace.stats.starttime.timestamp, endTime.timestamp, 1/trace.stats.sampling_rate)
        stop = time.clock()
        self.logger.debug('Prepared data (%.5fs)', stop - start)

        # Check if the data is a ma.maskedarray
        if np.ma.count_masked(trace.data):
            timeArray = np.ma.array(timeArray[:-1], mask=trace.data.mask)


        self.t0 = trace.stats.starttime

        #start = time.clock()
        #self.dataAxes.clear()
        #stop = time.clock()
        #self.logger.debug('Cleared axes (%.5fs)', stop - start)

        start = time.clock()
        print trace.stats.npts
        print timeArray.shape
        print trace.data.shape
        if not self.line:
            self.line, = self.dataAxes.plot(timeArray, trace.data, color=self.lineColor)
        else:
            self.logger.debug('Updating line %s', self.line)
            self.line.set_xdata(timeArray)
            self.line.set_ydata(trace.data)
        stop = time.clock()
        self.logger.debug('Plotted data (%.5fs)', stop -start)

        start = time.clock()
        self.dataAxes.set_frame_on(False)
        self.dataAxes.get_xaxis().set_visible(True)
        self.dataAxes.get_yaxis().set_visible(False)
        yLim = np.max(np.abs(trace.data))
        self.logger.debug('ylim: %f', yLim)
        self.dataAxes.set_ylim(bottom = -yLim, top = yLim)
        stop = time.clock()
        self.logger.debug('Adjusted axes look (%.5fs)', stop - start)

        self.logger.debug('time limits: %f, %f', timeArray[0], timeArray[-1])


    def setYLimits(self, bottom, top):
        ''' Set the limits of the y-axes.
        '''
        self.dataAxes.set_ylim(bottom = bottom, top = top)


    def setXLimits(self, left, right):
        ''' Set the limits of the x-axes.
        '''
        self.logger.debug('Set limits: %f, %f', left, right)
        self.dataAxes.set_xlim(left = left, right = right)


class TdChannelAnnotationArea(wx.Panel):

    def __init__(self, parent=None, id=wx.ID_ANY, label="channel name", bgColor="white", color="indianred", penColor="black"):
        wx.Panel.__init__(self, parent=parent, id=id, style=wx.FULL_REPAINT_ON_RESIZE)
        self.SetMinSize((40, -1))

        self.bgColor = bgColor
        self.label = label
        self.color = color
        self.penColor = penColor

	self.SetBackgroundColour(self.bgColor)

        self.Bind(wx.EVT_PAINT, self.OnPaint)


    def OnPaint(self, event):
        #print "OnPaint"
        event.Skip()
        dc = wx.PaintDC(self)
        gc = self.makeGC(dc)
        self.draw(gc)

    def makeGC(self, dc):
        try:
            gc = wx.GraphicsContext.Create(dc)
        except NotImplementedError:
            dc.DrawText("This build of wxPython does not support the wx.GraphicsContext "
                        "family of classes.",
                        25, 25)
            return None
        return gc

    def draw(self, gc):
        #print "drawing"
        winSize = self.GetClientSize()
        width = winSize[0]
        height = winSize[1]

        # Define the drawing  pen.
        penSize = 2;
        pen = wx.Pen(self.penColor, penSize)
        pen.SetJoin(wx.JOIN_ROUND)

        # Define the filling brush.
        brush = wx.Brush(self.color)

        # Define the font styles.
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        #font.SetWeight(wx.BOLD)
        gc.SetFont(font)

        path = gc.CreatePath()
        path.MoveToPoint(width, penSize/2.0)
        path.AddLineToPoint(3/4.0*width, penSize/2.0)
        path.MoveToPoint(3/4.0*width, penSize/2.0)
        path.AddLineToPoint(3/4.0*width, height-penSize/2.0)
        path.MoveToPoint(3/4.0*width, height-penSize/2.0)
        path.AddLineToPoint(width, height-penSize/2.0)
        path.CloseSubpath()

        path1 = gc.CreatePath()
        path1.AddRectangle(3/4.0*width, penSize/2.0, width/4.0, height-penSize/2.0)

        gc.SetPen(pen)
        gc.SetBrush(brush)
        gc.FillPath(path1)
        gc.DrawPath(path)

        newPos =  height/2

        #print winSize
        #print newPos
        gc.PushState()
        gc.Translate(width/4.0, newPos)
        gc.Rotate(np.radians(-90))
        w, h = gc.GetTextExtent(self.label)
        #print w
        gc.DrawText(self.label, -w/2.0, -h/2.0)
        #gc.DrawPath(path1)
        gc.PopState()

class TdChannel(wx.Panel):
    '''
    The channel panel.

    The channel panel may hold 1 to more TdViews.
    '''

    def __init__(self, parent=None, id=wx.ID_ANY, parentViewPort=None, name='channel name', color='black'):
        wx.Panel.__init__(self, parent=parent, id=id)

        # The viewPort containing the channel.
        self.parentViewPort = parentViewPort

        # The channel's name.
        self.name = name

        # The channel's color.
        self.color = color

        # A dictionary containing the views of the channel.
        self.views = {}

        self.SetBackgroundColour('white')

        self.annotationArea = TdChannelAnnotationArea(self, id=wx.ID_ANY, label=self.name, color=color)
        self.sizer = wx.GridBagSizer(0,0)
	self.sizer.Add(self.annotationArea, pos=(0,0), span=(1,1), flag=wx.ALL|wx.EXPAND, border=0)
        self.sizer.AddGrowableCol(1)
        self.SetSizer(self.sizer)

    def addView(self, view):
        view.Reparent(self)
        self.views[view.name] = view
	
        if self.views:
	    self.sizer.Add(view, pos=(len(self.views)-1,1), flag=wx.ALL|wx.EXPAND, border=0)
            self.sizer.AddGrowableRow(len(self.views)-1)
	    self.sizer.SetItemSpan(self.annotationArea, (len(self.views), 1))

            channelSize = self.views.itervalues().next().GetMinSize()
            channelSize[1] = channelSize[1] * len(self.views) 
            self.SetMinSize(channelSize)
	self.SetSizer(self.sizer)


    def hasView(self, viewName):
        ''' Check if the channel already contains the view.
        
        Parameters
        ----------
        viewName : String
            The name of the view to search.
        '''
        return self.views.get(viewName, None)









class TdStation(wx.Panel):
    '''
    The station panel.

    The station panel may hold 1 to more TdChannels.
    '''

    def __init__(self, parent=None, id=wx.ID_ANY, parentViewPort=None, name=None, network=None, location=None, color='black'):
        wx.Panel.__init__(self, parent=parent, id=id)

        # The viewPort containing the channel.
        self.parentViewPort = parentViewPort

        # The name of the station.
        self.name = name

        # The network of the station.
        self.network = network

        # The location of the station.
        self.location = location

        # The channel's color.
        self.color = color

        # A dictionary containing the views of the channel.
        self.channels = {}

        self.SetBackgroundColour('white')

        self.annotationArea = TdStationAnnotationArea(self, id=wx.ID_ANY, label=self.name, color=color)
        self.sizer = wx.GridBagSizer(0,0)
	self.sizer.Add(self.annotationArea, pos=(0,0), span=(1,1), flag=wx.ALL|wx.EXPAND, border=0)
        self.sizer.AddGrowableCol(1)
        self.SetSizer(self.sizer)

    def addChannel(self, channel):
        channel.Reparent(self)
        self.channels[channel.name] = channel
	if self.channels:
	    self.sizer.Add(channel, pos=(len(self.channels)-1,1), flag=wx.TOP|wx.BOTTOM|wx.EXPAND, border=1)
            self.sizer.AddGrowableRow(len(self.channels)-1)
	    self.sizer.SetItemSpan(self.annotationArea, (len(self.channels), 1))

            stationSize = self.channels.itervalues().next().GetMinSize()
            stationSize[1] = stationSize[1] * len(self.channels) 
            self.SetMinSize(stationSize)
	self.SetSizer(self.sizer)



    def hasChannel(self, channelName):
        ''' Check if the station already contains a channel.

        Parameters
        ----------
        channelName : String
            The name of the channel to search.
        '''
        return self.channels.get(channelName, None)





class TdDatetimeInfo(wx.Panel):
    def __init__(self, parent=None, id=wx.ID_ANY, bgColor="orchid", penColor="black"):
        wx.Panel.__init__(self, parent=parent, id=id, style=wx.FULL_REPAINT_ON_RESIZE)
        self.SetMinSize((-1, 30))
        self.SetMaxSize((-1, 30))

        # The logging logger instance.
        loggerName = __name__ + "." + self.__class__.__name__
        self.logger = logging.getLogger(loggerName)

        self.startTime = None
        self.endTime = None

        self.SetBackgroundColour(bgColor)

        self.Bind(wx.EVT_PAINT, self.onPaint)

    def onPaint(self, event):
        #print "OnPaint"
        event.Skip()
        dc = wx.PaintDC(self)
        gc = self.makeGC(dc)
        self.draw(gc)

    def makeGC(self, dc):
        try:
            gc = wx.GraphicsContext.Create(dc)
        except NotImplementedError:
            dc.DrawText("This build of wxPython does not support the wx.GraphicsContext "
                        "family of classes.",
                        25, 25)
            return None
        return gc

    def draw(self, gc):
        self.logger.debug('Draw datetime')
        winSize = self.GetClientSize()
        width = winSize[0]
        height = winSize[1]


        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetWeight(wx.BOLD)
        gc.SetFont(font)
        if self.startTime:
            gc.Translate(80, height/2.0)
            gc.DrawText(str(self.startTime), 0, 0)


    def setTime(self, startTime, endTime):

        # TODO: Add a check for the correct data type.
        self.startTime = startTime
        self.endTime = endTime



class TdStationAnnotationArea(wx.Panel):

    def __init__(self, parent=None, id=wx.ID_ANY, label="station name", bgColor="white", color="indianred", penColor="black"):
        wx.Panel.__init__(self, parent=parent, id=id, style=wx.FULL_REPAINT_ON_RESIZE)
        self.SetMinSize((40, -1))

        self.bgColor = bgColor
        self.label = label
        self.color = color
        self.penColor = penColor

	self.SetBackgroundColour(self.bgColor)

        self.Bind(wx.EVT_PAINT, self.OnPaint)


    def OnPaint(self, event):
        #print "OnPaint"
        event.Skip()
        dc = wx.PaintDC(self)
        gc = self.makeGC(dc)
        self.draw(gc)

    def makeGC(self, dc):
        try:
            gc = wx.GraphicsContext.Create(dc)
        except NotImplementedError:
            dc.DrawText("This build of wxPython does not support the wx.GraphicsContext "
                        "family of classes.",
                        25, 25)
            return None
        return gc

    def draw(self, gc):
        #print "drawing"
        winSize = self.GetClientSize()
        width = winSize[0]
        height = winSize[1]

        # Define the drawing  pen.
        penSize = 2;
        pen = wx.Pen(self.penColor, penSize)
        pen.SetJoin(wx.JOIN_ROUND)

        # Define the filling brush.
        brush = wx.Brush(self.color)

        # Define the font styles.
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetWeight(wx.BOLD)
        gc.SetFont(font)

        path = gc.CreatePath()
        path.MoveToPoint(width, penSize/2.0)
        path.AddLineToPoint(3/4.0*width, penSize/2.0)
        path.MoveToPoint(3/4.0*width, penSize/2.0)
        path.AddLineToPoint(3/4.0*width, height-penSize/2.0)
        path.MoveToPoint(3/4.0*width, height-penSize/2.0)
        path.AddLineToPoint(width, height-penSize/2.0)
        path.CloseSubpath()

        path1 = gc.CreatePath()
        path1.AddRectangle(3/4.0*width, penSize/2.0, width/4.0, height-penSize/2.0)

        gc.SetPen(pen)
        gc.SetBrush(brush)
        gc.FillPath(path1)
        gc.DrawPath(path)

        newPos =  height/2

        #print winSize
        #print newPos
        gc.PushState()
        gc.Translate(width/4.0, newPos)
        gc.Rotate(np.radians(-90))
        w, h = gc.GetTextExtent(self.label)
        #print w
        gc.DrawText(self.label, -w/2.0, -h/2.0)
        #gc.DrawPath(path1)
        gc.PopState()



class TdViewPort(scrolled.ScrolledPanel):
    '''
    The tracedisplay viewport.

    This panel holds the :class:`~psysmon.packages.tracedisplay.TdStation` objects.
    '''

    def __init__(self, parent=None, id=wx.ID_ANY):
        scrolled.ScrolledPanel.__init__(self, parent=parent, id=id, style=wx.FULL_REPAINT_ON_RESIZE)
        
        # The logging logger instance.
        loggerName = __name__ + "." + self.__class__.__name__
        self.logger = logging.getLogger(loggerName)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        self.SetBackgroundColour('red')

        self.SetupScrolling()

        # The list of stations controlled by the viewport.
        self.stations = [] 
        
        # Message subsiptions
        pub.subscribe(self.onStationMsg, ('tracedisplay', 'display', 'station'))


    def onStationMsg(self, msg):
        if msg.topic == ('tracedisplay', 'display', 'station', 'hide'):
            self.removeStation(msg.data)



    def addStation(self, station, position=None):
        '''
        Add a TdStation object to the viewport.

        :param self: The object pointer.
        :type self: :class:`~psysmon.packages.tracedisplay.TdViewPort`
        :param station: The station to be added to the viewport.
        :type station: :class:TdStation
        :param position: The position where to add the station. If none, the station is added to the bottom.
        :type position: Integer
        '''
        station.Reparent(self)
        self.stations.append(station)

        #self.sizer.Add(station, 1, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=5)
        viewPortSize = self.stations[-1].GetMinSize()
        viewPortSize[1] = viewPortSize[1] * len(self.stations) + 100 
        #self.SetMinSize(viewPortSize)
        self.SetupScrolling()



    def hasStation(self, stationName):
        ''' Check if the viewport already contains a station.

        Parameters
        ----------
        stationName : String
            The name of the station.
        '''
        stationsFound = [x for x in self.stations if x.name == stationName]
        if len(stationsFound) == 1:
            return stationsFound[0]
        else:
            return stationsFound
        #return self.stations.get(stationName, None)



    def sortStations(self, snl=[]):
        ''' Sort the stations according to the list given by snl.

            Parameters
            ----------
            snl : Tuple of Stringssnl=[]
                The order how to sort the stations. (station, network, location).
        '''
        for curStation in self.stations:
            curStation.Hide()
            self.sizer.Detach(curStation)


        for curSnl in snl:
            statFound = [x for x in self.stations if x.name == curSnl[0]]
            if statFound:
                self.sizer.Add(statFound[0], 1, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=5)
                statFound[0].Show()



    def removeStation(self, snl):
        ''' Remove a station from the viewport.

        This destroys the instance of the station.

        Parameters
        ----------
        station : :class:`TdStation`
            The station object which should be removed.
        '''
        for curSnl in snl:
            statFound = [x for x in self.stations if x.name == curSnl[0]]
            if statFound:
                statFound = statFound[0]
                self.stations.remove(statFound)
                self.sizer.Remove(statFound)
                self.rearrangeStations()

        self.sizer.Layout()


    def rearrangeStations(self):
        ''' Rearrange the stations in the viewport.

        '''

        for curStation in self.stations:
            #curStation.Hide()
            self.sizer.Hide(curStation)
            self.sizer.Detach(curStation)


        for curStation in self.stations:
            self.sizer.Add(curStation, 1, flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=5)
            curStation.Show()




