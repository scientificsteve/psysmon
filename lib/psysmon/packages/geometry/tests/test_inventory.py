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

import unittest

from obspy.core.utcdatetime import UTCDateTime
import logging
import os

import psysmon
from psysmon.packages.geometry.inventory import Inventory
from psysmon.packages.geometry.inventory import Network
from psysmon.packages.geometry.inventory import Station
from psysmon.packages.geometry.inventory import Recorder
from psysmon.packages.geometry.inventory import Channel
from psysmon.packages.geometry.inventory import RecorderStream
from psysmon.packages.geometry.inventory import Sensor
from psysmon.packages.geometry.inventory import SensorParameter
from psysmon.packages.geometry.inventory import TimeBox

class InventoryTestCase(unittest.TestCase):
    """
    Test suite for psysmon.packages.geometry.editGeometry.EditGeometryDlg
    """

    @classmethod
    def setUpClass(cls):
        # Configure the logger.
        cls.logger = logging.getLogger('psysmon')
        cls.logger.setLevel('DEBUG')
        cls.logger.addHandler(psysmon.getLoggerHandler())

        cls.data_path = os.path.dirname(os.path.abspath(__file__))
        cls.data_path = os.path.join(cls.data_path, 'data')

    def setUp(self):
        pass

    def tearDown(self):
        print "Es war sehr schoen - auf Wiederseh'n.\n"

    def test_station_creation(self):
        ''' Test the creation of a station.
        '''
        station = Station(name = 'TEST',
                          location = 'test site',
                          x = 10,
                          y = 20,
                          z = 30)

        self.assertEqual(station.name, 'TEST')
        self.assertEqual(station.location, 'test site')
        self.assertEqual(station.x, 10)
        self.assertEqual(station.y, 20)
        self.assertEqual(station.z, 30)
        self.assertIsNone(station.id)
        self.assertEqual(station.channels, [])
        self.assertEqual(station.parent_inventory, None)
        self.assertFalse(station.has_changed)


    def test_add_station_to_inventory(self):
        inventory = Inventory('inventory_name')

        network1 = Network(name = 'XX')
        network2 = Network(name = 'YY')

        station1 = Station(name = 'station1_name',
                           network = 'XX',
                           location = 'station1_location',
                           x = 10,
                           y = 20,
                           z = 30)

        station2 = Station(name = 'station2_name',
                           network = 'YY',
                           location = 'station2_location',
                           x = 10,
                           y = 20,
                           z = 30)

        station3 = Station(name = 'station3_name',
                           network = 'ZZ',
                           location = 'station3_location',
                           x = 10,
                           y = 20,
                           z = 30)

        inventory.add_network(network1)
        inventory.add_network(network2)
        inventory.add_station(station1)
        inventory.add_station(station2)
        inventory.add_station(station3)

        self.assertIs(station1.parent_inventory, inventory)
        self.assertIs(station2.parent_inventory, inventory)
        self.assertIsNone(station3.parent_inventory)

        self.assertIs(station1.parent_network, network1)
        self.assertIs(station2.parent_network, network2)
        self.assertIsNone(station3.parent_network)



    def test_add_network_to_inventory(self):
        inventory = Inventory('inventory_name')

        network1 = Network(name = 'XX')
        network2 = Network(name = 'YY')

        station1 = Station(name = 'station1_name',
                           location = 'station1_location',
                           x = 10,
                           y = 20,
                           z = 30)

        # The network name should be overwritten when added to the network.
        station2 = Station(name = 'station2_name',
                           network = 'AA',
                           location = 'station2_location',
                           x = 10,
                           y = 20,
                           z = 30)
        network1.add_station(station1)
        network2.add_station(station2)

        inventory.add_network(network1)
        inventory.add_network(network2)

        self.assertEqual(len(inventory.networks), 2)
        self.assertTrue(network1 in inventory.networks)
        self.assertTrue(network2 in inventory.networks)
        self.assertEqual(station2.network, 'YY')

        # Add a new station to the network which already was added to a
        # network.
        # This should add the new station only to the inventory station list.
        station3 = Station(name = 'station3_name',
                           network = 'YY',
                           location = 'station3_location',
                           x = 10,
                           y = 20,
                           z = 30)

        network2.add_station(station3)




    def test_remove_network_from_inventory(self):
        inventory = Inventory('inventory_name')

        network1 = Network(name = 'XX')
        network2 = Network(name = 'YY')
        network3 = Network(name = 'ZZ')

        inventory.add_network(network1)
        inventory.add_network(network2)
        inventory.add_network(network3)
        self.assertEqual(len(inventory.networks), 3)

        cur_net = inventory.remove_network(name = 'YY')
        self.assertEqual(len(inventory.networks), 2)
        self.assertEqual(cur_net, network2)
        self.assertTrue(network2 not in inventory.networks)

        cur_net = inventory.remove_network(name = 'AA')
        self.assertIsNone(cur_net)
        self.assertEqual(len(inventory.networks), 2)





    def test_add_sensor_to_inventory(self):
        inventory = Inventory('inventory_name')

        sensor1 = Sensor(serial = 'sensor1_name',
                         type = 'sensor1_type',
                         component = 'sensor1_component')

        sensor2 = Sensor(serial = 'sensor2_name',
                         type = 'sensor2_type',
                         component = 'sensor2_component')

        sensor3 = Sensor(serial = 'sensor3_name',
                         type = 'sensor3_type',
                         component = 'sensor3_component')

        inventory.add_sensor(sensor1)
        inventory.add_sensor(sensor2)
        inventory.add_sensor(sensor3)

        self.assertEqual(sensor1.parent_inventory, inventory)
        self.assertEqual(sensor2.parent_inventory, inventory)
        self.assertEqual(sensor3.parent_inventory, inventory)

        self.assertEqual(len(inventory.sensors), 3)
        self.assertTrue(sensor1 in inventory.sensors)
        self.assertTrue(sensor2 in inventory.sensors)
        self.assertTrue(sensor3 in inventory.sensors)



    def test_inventory_get_methods(self):
        inventory = Inventory('inventory_name')

        network1 = Network(name = 'XX',
                           type = 'db')
        network2 = Network(name = 'YY',
                           type = 'xml')
        network3 = Network(name = 'ZZ',
                           type = 'xml')

        station1 = Station(name = 'station1_name',
                           location = 'station1_location',
                           x = 10,
                           y = 20,
                           z = 30)

        station2 = Station(name = 'station2_name',
                           location = 'station2_location',
                           x = 10,
                           y = 20,
                           z = 30)

        station3 = Station(name = 'station3_name',
                           location = 'station3_location',
                           x = 10,
                           y = 20,
                           z = 30)

        station4 = Station(name = 'station4_name',
                           location = 'station4_location',
                           x = 10,
                           y = 20,
                           z = 30)

        network1.add_station(station1)
        network2.add_station(station2)
        network2.add_station(station3)
        network3.add_station(station4)

        inventory.add_network(network1)
        inventory.add_network(network2)
        inventory.add_network(network3)

        # Test getting networks.
        cur_net = inventory.get_network()
        self.assertEqual(len(cur_net), 3)
        cur_net = inventory.get_network(name = 'XX')
        self.assertEqual(cur_net[0], network1)
        cur_net = inventory.get_network(name = 'YY')
        self.assertEqual(cur_net[0], network2)
        cur_net = inventory.get_network(name = 'ZZ')
        self.assertEqual(cur_net[0], network3)
        cur_net = inventory.get_network(type = 'db')
        self.assertEqual(cur_net[0], network1)
        cur_net = inventory.get_network(type = 'xml')
        self.assertEqual(len(cur_net), 2)
        self.assertTrue(network2 in cur_net)
        self.assertTrue(network3 in cur_net)
        cur_net = inventory.get_network(name = 'XX', type = 'db')
        self.assertEqual(cur_net[0], network1)
        cur_net = inventory.get_network(name = 'YY', type = 'xml')
        self.assertEqual(cur_net[0], network2)


        # Test getting stations.
        cur_stat = inventory.get_station()
        self.assertEqual(len(cur_stat), 4)




    def test_add_channel_to_station(self):
        station = Station(name = 'station_name',
                          location = 'station_location',
                          x = 10,
                          y = 20,
                          z = 30)

        channel_2_add = Channel(name = 'channel_name')

        station.add_channel(channel_2_add)

        self.assertEqual(len(station.channels), 1)
        self.assertEqual(station.channels[0], channel_2_add)



    def test_add_stream_to_recorder(self):
        recorder = Recorder(serial = 'AAAA', type = 'test recorder')

        stream1 = RecorderStream(name = 'stream1_name',
                                 label = 'stream1_label')
        recorder.add_stream(stream1)

        self.assertEqual(len(recorder.streams), 1)
        self.assertIs(recorder.streams[0], stream1)

        stream2 = RecorderStream(name = 'stream2_name',
                                 label = 'stream2_label')
        recorder.add_stream(stream2)

        self.assertEqual(len(recorder.streams), 2)
        self.assertIs(recorder.streams[1], stream2)

        stream3 = RecorderStream(name = 'stream3_name',
                                 label = 'stream3_label')
        recorder.add_stream(stream3)

        self.assertEqual(len(recorder.streams), 3)
        self.assertIs(recorder.streams[2], stream3)

        # Remove the streams.
        popped_stream = recorder.pop_stream(name = 'stream2_name')
        self.assertEqual(len(recorder.streams), 2)
        self.assertIs(popped_stream[0], stream2)

        popped_stream = recorder.pop_stream(name = 'stream1_name')
        self.assertEqual(len(recorder.streams), 1)
        self.assertIs(popped_stream[0], stream1)

        popped_stream = recorder.pop_stream(label = 'stream3_label')
        self.assertEqual(len(recorder.streams), 0)
        self.assertIs(popped_stream[0], stream3)



    def test_get_stream_from_recorder(self):
        recorder = Recorder(serial = 'AAAA', type = 'test recorder')

        stream_2_add = RecorderStream(name = 'stream1_name',
                                      label = 'stream1_label')
        recorder.add_stream(stream_2_add)

        stream_2_add = RecorderStream(name = 'stream2_name',
                                      label = 'stream2_label')

        recorder.add_stream(stream_2_add)

        self.assertEqual(len(recorder.streams), 2)

        cur_stream = recorder.get_stream(name = 'stream1_name')
        self.assertEqual(len(cur_stream), 1)
        self.assertEqual(cur_stream[0].name, 'stream1_name')
        self.assertEqual(cur_stream[0].label, 'stream1_label')


    def test_get_sensor_from_stream(self):
        stream = RecorderStream(name = 'stream1_name',
                                label = 'stream1_label')

        sensor1 = Sensor(serial = 'sensor1_serial',
                         type = 'sensor1_type',
                         component = 'sensor1_component')

        sensor2 = Sensor(serial = 'sensor2_serial',
                         type = 'sensor2_type',
                         component = 'sensor2_component')

        start_time1 = UTCDateTime('2014-01-01')
        end_time1 = UTCDateTime('2014-02-01')
        stream.sensors.append(TimeBox(sensor1, start_time1, end_time1))

        start_time2 = UTCDateTime('2014-03-01')
        end_time2 = UTCDateTime('2014-04-01')
        stream.sensors.append(TimeBox(sensor2, start_time2, end_time2))

        cur_sensor = stream.get_sensor(start_time = UTCDateTime('2014-01-01'))
        self.assertEqual(len(cur_sensor), 2)
        self.assertEqual(cur_sensor[0], TimeBox(sensor1, start_time1, end_time1))
        self.assertEqual(cur_sensor[1], TimeBox(sensor2, start_time2, end_time2))

        cur_sensor = stream.get_sensor(start_time = UTCDateTime('2014-02-01'))
        self.assertEqual(len(cur_sensor), 1)
        self.assertEqual(cur_sensor[0], TimeBox(sensor2, start_time2, end_time2))

        cur_sensor = stream.get_sensor(start_time = UTCDateTime('2014-04-01'))
        self.assertEqual(len(cur_sensor), 0)


        cur_sensor = stream.get_sensor(end_time = UTCDateTime('2014-03-15'))
        self.assertEqual(len(cur_sensor), 2)
        self.assertEqual(cur_sensor[0], TimeBox(sensor1, start_time1, end_time1))
        self.assertEqual(cur_sensor[1], TimeBox(sensor2, start_time2, end_time2))

        cur_sensor = stream.get_sensor(end_time = UTCDateTime('2014-02-15'))
        self.assertEqual(len(cur_sensor), 1)
        self.assertEqual(cur_sensor[0], TimeBox(sensor1, start_time1, end_time1))

        cur_sensor = stream.get_sensor(end_time = UTCDateTime('2014-01-01'))
        self.assertEqual(len(cur_sensor), 0)


        cur_sensor = stream.get_sensor(start_time = UTCDateTime('2013-12-01'),
                                       end_time = UTCDateTime('2014-05-01'))
        self.assertEqual(len(cur_sensor), 2)
        self.assertEqual(cur_sensor[0], TimeBox(sensor1, start_time1, end_time1))
        self.assertEqual(cur_sensor[1], TimeBox(sensor2, start_time2, end_time2))

        cur_sensor = stream.get_sensor(start_time = UTCDateTime('2013-12-01'),
                                       end_time = UTCDateTime('2014-02-15'))
        self.assertEqual(len(cur_sensor), 1)
        self.assertEqual(cur_sensor[0], TimeBox(sensor1, start_time1, end_time1))

        cur_sensor = stream.get_sensor(start_time = UTCDateTime('2014-01-05'),
                                       end_time = UTCDateTime('2014-01-06'))
        self.assertEqual(len(cur_sensor), 1)
        self.assertEqual(cur_sensor[0], TimeBox(sensor1, start_time1, end_time1))

        cur_sensor = stream.get_sensor(start_time = UTCDateTime('2014-01-05'),
                                       end_time = UTCDateTime('2014-03-06'))
        self.assertEqual(len(cur_sensor), 2)
        self.assertEqual(cur_sensor[0], TimeBox(sensor1, start_time1, end_time1))
        self.assertEqual(cur_sensor[1], TimeBox(sensor2, start_time2, end_time2))

        cur_sensor = stream.get_sensor(start_time = UTCDateTime('2014-01-05'),
                                       end_time = UTCDateTime('2014-03-06'),
                                       serial = 'sensor2_serial',
                                       type = 'sensor2_type')
        self.assertEqual(len(cur_sensor), 1)
        self.assertEqual(cur_sensor[0], TimeBox(sensor2, start_time2, end_time2))


    def test_add_sensor_to_stream(self):
        inventory = Inventory('inventory_name')
        recorder1 = Recorder(serial = 'rec1_serial',
                             type = 'rec1_type')

        stream1 = RecorderStream(name = 'stream1_name',
                               label = 'stream1_label')
        recorder1.add_stream(stream1)
        inventory.add_recorder(recorder1)

        sensor1 = Sensor(serial = 'sensor1_serial',
                         type = 'sensor1_type',
                         component = 'sensor1_component')
        inventory.add_sensor(sensor1)

        cur_starttime = UTCDateTime('1976-06-20')
        cur_endtime = UTCDateTime('2014-06-20')
        stream1.add_sensor(sensor_serial = 'sensor1_serial',
                           sensor_component = 'sensor1_component',
                           start_time = cur_starttime,
                           end_time = cur_endtime)

        self.assertEqual(len(stream1.sensors), 1)
        self.assertEqual(stream1.sensors[0], TimeBox(sensor1, cur_starttime, cur_endtime))



#def suite():
#    suite = unittest.makeSuite(EditGeometryDlgTestCase, 'test')
#    return suite

def suite():
#    tests = ['testXmlImport']
#    return unittest.TestSuite(map(InventoryTestCase, tests))
    return unittest.makeSuite(InventoryTestCase, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')

