# LICENSE
#
# This file is part of pSysmon.
#
# If you use pSysmon in any program or publication, please inform and
# acknowledge its author Stefan Mertl (info@stefanmertl.com).
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

name = "tracedisplay"
version = "0.1.1"
author = "Stefan Mertl"
minPsysmonVersion = "0.0.1"
description = "The tracedisplay package."
website = "http://www.stefanmertl.com"


def nodeFactory():
    from tracedisplay import TraceDisplay

    nodeTemplates = []

    # Create a pSysmon collection node template and add it to the package.
    options = {}

    myNodeTemplate = TraceDisplay(name = 'tracedisplay',
                                  mode = 'editable',
                                  category = 'Display',
                                  tags = ['development'],
                                  options = options
                                  )

    nodeTemplates.append(myNodeTemplate)

    return nodeTemplates


def pluginFactory():
    ''' Provide some plugins.
    '''
    from plugins import SelectStation, SelectChannel, Zoom, SeismogramPlotter, DemoPlotter, ProcessingStack, SpectrogramPlotter

    pluginTemplates = []

    ########################################################
    # The select station options plugin
    myPluginTemplate = SelectStation(name = 'select station',
                                     category = 'view',
                                     tags = ['station', 'view', 'select'],
                                     nodeClass = 'TraceDisplay'
                                     )
    pluginTemplates.append(myPluginTemplate)



    ########################################################
    # The select channel options plugin
    myPluginTemplate = SelectChannel(name = 'select channel',
                                     category = 'view',
                                     tags = ['channel', 'view', 'select'],
                                     nodeClass = 'TraceDisplay'
                                     )
    pluginTemplates.append(myPluginTemplate)



    ########################################################
    # The plot seismogram addon plugin.
    myPluginTemplate = SeismogramPlotter(name = 'plot seismogram',
                            category = 'visualize',
                            tags = None,
                            nodeClass = 'TraceDisplay'
                            )
    pluginTemplates.append(myPluginTemplate)



    ########################################################
    # The demo plotter addon plugin.
    myPluginTemplate = DemoPlotter(name = 'demo plotter',
                            category = 'visualize',
                            tags = None,
                            nodeClass = 'TraceDisplay'
                            )
    pluginTemplates.append(myPluginTemplate)

    
    ########################################################
    # The spectrogram plotter addon plugin.
    myPluginTemplate = SpectrogramPlotter(name = 'spectrogram plotter',
                                          category = 'visualize',
                                          tags = None,
                                          nodeClass = 'TraceDisplay'
                                         )
    pluginTemplates.append(myPluginTemplate)


    ########################################################
    # The the zoom interactive plugin.
    myPluginTemplate = Zoom(name = 'zoom',
                            category = 'view',
                            tags = None,
                            nodeClass = 'TraceDisplay'
                            )
    pluginTemplates.append(myPluginTemplate)


    ########################################################
    # The processing stack GUI options plugin.
    myPluginTemplate = ProcessingStack(name = 'processing stack',
                                       category = 'proc',
                                       tags = ['process data'],
                                       nodeClass = 'TraceDisplay'
                                       )
    pluginTemplates.append(myPluginTemplate)


    return pluginTemplates



def processingNodeFactory():
    ''' Provide some processing nodes.
    '''
    from processingNodes import Detrend, FilterBandPass, FilterLowPass

    procNodeTemplates = []

    ########################################################
    # Detrend a timeseries.
    options = {}
    options['method'] = 'constant'

    myProcNodeTemplate = Detrend(name = 'detrend',
                                 mode = 'editable',
                                 category = 'test',
                                 tags = ['remove', 'mean'],
                                 options = options,
                                 )

    procNodeTemplates.append(myProcNodeTemplate)



    ########################################################
    # Bandpass filter.
    options = {}
    options['freqmin'] = 1
    options['freqmax'] = 15
    options['zerophase'] = False
    options['corners'] = 4

    myProcNodeTemplate = FilterBandPass(name = 'bandpass filter',
                                        mode = 'editable',
                                        category = 'frequency',
                                        tags = ['filter', 'bandpass'],
                                        options = options,
                                       )

    procNodeTemplates.append(myProcNodeTemplate)


    ########################################################
    # Bandpass filter.
    options = {}
    options['freq'] = 10
    options['zerophase'] = False
    options['corners'] = 4

    myProcNodeTemplate = FilterLowPass(name = 'lowpass filter',
                                        mode = 'editable',
                                        category = 'frequency',
                                        tags = ['filter', 'lowpass'],
                                        options = options,
                                       )
    procNodeTemplates.append(myProcNodeTemplate)

    return procNodeTemplates
