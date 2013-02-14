'''
Created on May 17, 2011

@author: Stefan Mertl
'''

import unittest
import psysmon
import logging
import os

from obspy.core.utcdatetime import UTCDateTime

from psysmon.core.test_util import create_psybase
from psysmon.core.test_util import create_empty_project
from psysmon.core.test_util import create_full_project
from psysmon.core.test_util import drop_project_database_tables
from psysmon.core.test_util import remove_project_filestructure

from psysmon.packages.geometry.db_inventory import DbInventory
from psysmon.packages.geometry.db_inventory import DbNetwork
from psysmon.packages.geometry.db_inventory import DbStation
from psysmon.packages.geometry.db_inventory import DbSensor
from psysmon.packages.geometry.db_inventory import DbSensorParameter

from psysmon.packages.geometry.inventory import Network
from psysmon.packages.geometry.inventory import Station
from psysmon.packages.geometry.inventory import Recorder
from psysmon.packages.geometry.inventory import Sensor
from psysmon.packages.geometry.inventory import SensorParameter

class DbInventoryTestCase(unittest.TestCase):
    """
    Test suite for psysmon.packages.geometry.editGeometry.EditGeometryDlg
    """
    @classmethod
    def setUpClass(cls):
        cls.psybase = create_psybase()
        cls.project = create_empty_project(cls.psybase)
        #cls.full_project = create_full_project(cls.psybase)
        print "In setUpClass...\n"


    @classmethod
    def tearDownClass(cls):
        print "dropping database tables...\n"
        drop_project_database_tables(cls.project)
        print "removing temporary file structure....\n"
        remove_project_filestructure(cls.project)
        print "removing temporary base directory....\n"
        os.removedirs(cls.project.base_dir)
        print "....finished cleaning up.\n"


    def setUp(self):
        # Configure the logger.
        logger = logging.getLogger('psysmon')
        logger.setLevel('DEBUG')
        logger.addHandler(psysmon.getLoggerHandler())


    def tearDown(self):
        print "Es war sehr schoen - auf Wiederseh'n.\n"


    def test_add_network(self):
        print "test_add_network\n"
        db_inventory = DbInventory('test', self.project)

        # Add a network to the db_inventory.
        net_2_add = Network(name = 'XX', description = 'A test network.')
        added_network = db_inventory.add_network(net_2_add)
        self.assertIsInstance(added_network, DbNetwork)
        self.assertEqual(len(db_inventory.networks), 1)

        # Add the same network again. This should return a None value.
        added_network = db_inventory.add_network(net_2_add)
        self.assertIsNone(added_network)
        self.assertEqual(len(db_inventory.networks), 1)

        # Add a network with two stations.
        net_2_add = Network(name = 'YY', description = 'A test network.')
        added_network = db_inventory.add_network(net_2_add)
        # Add a station to the XX network.
        stat_2_add = Station(name = 'AAA',
                             network = 'YY',
                             location = '00',
                             x = 0,
                             y = 0,
                             z = 0,
                             coord_system = 'epsg:4316')
        added_station = db_inventory.add_station(stat_2_add)
        self.assertEqual(len(added_network.stations), 1)
        self.assertEqual(len(added_network.geom_network.stations), 1)
        self.assertEqual(added_network.stations[0], added_station)

        # Add a station to the XX network.
        stat_2_add = Station(name = 'BBB',
                             network = 'YY',
                             location = '00',
                             x = 0,
                             y = 0,
                             z = 0,
                             coord_system = 'epsg:4316')
        added_station = db_inventory.add_station(stat_2_add)
        self.assertEqual(len(added_network.stations), 2)
        self.assertEqual(len(added_network.geom_network.stations), 2)
        self.assertEqual(added_network.stations[1], added_station)




    def test_remove_network(self):
        print "test_remove_network\n"
        db_inventory = DbInventory('test', self.project)

        # Add a network to the db_inventory.
        net_2_add = Network(name = 'XX', description = 'A test network.')
        added_network_1 = db_inventory.add_network(net_2_add)
        self.assertIsInstance(added_network_1, DbNetwork)
        self.assertEqual(len(db_inventory.networks), 1)

        net_2_add = Network(name = 'YY', description = 'A second test network.')
        added_network_2 = db_inventory.add_network(net_2_add)
        self.assertIsInstance(added_network_2, DbNetwork)
        self.assertEqual(len(db_inventory.networks), 2)

        # Remove the networks from the inventory.
        removed_network = db_inventory.remove_network('XX')
        self.assertEqual(len(db_inventory.networks), 1)
        self.assertIsInstance(removed_network, DbNetwork)
        self.assertEqual(added_network_1, removed_network)
        self.assertEqual(added_network_2, db_inventory.networks[0])

        removed_network = db_inventory.remove_network('YY')
        self.assertEqual(len(db_inventory.networks), 0)
        self.assertIsInstance(removed_network, DbNetwork)
        self.assertEqual(added_network_2, removed_network)


    def test_add_station(self):
        print "test_add_network\n"
        db_inventory = DbInventory('test', self.project)

        # Add a network to the db_inventory.
        net_2_add = Network(name = 'XX', description = 'A test network.')
        added_network_1 = db_inventory.add_network(net_2_add)
        self.assertIsInstance(added_network_1, DbNetwork)
        self.assertEqual(len(db_inventory.networks), 1)

        net_2_add = Network(name = 'YY', description = 'A second test network.')
        added_network_2 = db_inventory.add_network(net_2_add)
        self.assertIsInstance(added_network_2, DbNetwork)
        self.assertEqual(len(db_inventory.networks), 2)

        # Add a station to the XX network.
        stat_2_add = Station(name = 'AAA',
                             network = 'XX',
                             location = '00',
                             x = 0,
                             y = 0,
                             z = 0,
                             coord_system = 'epsg:4316')
        added_station = db_inventory.add_station(stat_2_add)
        self.assertIsInstance(added_station, DbStation)
        self.assertEqual(len(added_network_1.stations), 1)


        # Add a station to the YY network.
        stat_2_add = Station(name = 'AAA',
                             network = 'YY',
                             location = '00',
                             x = 0,
                             y = 0,
                             z = 0,
                             coord_system = 'epsg:4316')
        added_station = db_inventory.add_station(stat_2_add)
        self.assertIsInstance(added_station, DbStation)
        self.assertEqual(len(added_network_2.stations), 1)


    def test_remove_station(self):
        print "test_remove_network\n"
        db_inventory = DbInventory('test', self.project)

        # Add a network to the db_inventory.
        net_2_add = Network(name = 'XX', description = 'A test network.')
        added_network_1 = db_inventory.add_network(net_2_add)

        net_2_add = Network(name = 'YY', description = 'A second test network.')
        added_network_2 = db_inventory.add_network(net_2_add)

        # Add a station to the XX network.
        stat_2_add = Station(name = 'AAA',
                             network = 'XX',
                             location = '00',
                             x = 0,
                             y = 0,
                             z = 0,
                             coord_system = 'epsg:4316')
        added_station_1 = db_inventory.add_station(stat_2_add)

        # Add a station to the YY network.
        stat_2_add = Station(name = 'AAA',
                             network = 'YY',
                             location = '00',
                             x = 0,
                             y = 0,
                             z = 0,
                             coord_system = 'epsg:4316')
        added_station_2 = db_inventory.add_station(stat_2_add)

        removed_station = db_inventory.remove_station(('AAA', 'XX', '00'))
        self.assertEqual(removed_station, added_station_1)
        self.assertEqual(len(added_network_1.stations), 0)
        self.assertEqual(len(added_network_1.geom_network.stations), 0)

        removed_station = db_inventory.remove_station(('AAA', 'YY', '00'))
        self.assertEqual(removed_station, added_station_2)
        self.assertEqual(len(added_network_2.stations), 0)
        self.assertEqual(len(added_network_2.geom_network.stations), 0)


    def test_add_recorder(self):
        db_inventory = DbInventory('test', self.project)

        rec_2_add = Recorder(serial = 'AAAA', type = 'test recorder')
        added_recorder = db_inventory.add_recorder(rec_2_add)
        self.assertEqual(len(db_inventory.recorders), 1)
        self.assertEqual(db_inventory.recorders[0], added_recorder)

        # Add the same recorder again. This should return none.
        added_recorder = db_inventory.add_recorder(rec_2_add)
        self.assertIsNone(added_recorder)

        # Add a recorder with a sensor.
        rec_2_add = Recorder(serial = 'BBBB', type = 'test recorder')
        sensor_2_add = Sensor(serial = 'AAAA',
                              type = 'test sensor',
                              rec_channel_name = '001',
                              channel_name = 'HHZ',
                              label = 'AAAA-001-HHZ') 

        parameter_2_add = SensorParameter(sensor_id = sensor_2_add.id,
                                         gain = 1,
                                         bitweight = 2,
                                         bitweight_units = 'bw_units',
                                         sensitivity = 3,
                                         sensitivity_units = 'sens_units',
                                         start_time = UTCDateTime('1976-06-20'),
                                         end_time = UTCDateTime('2012-06-20'))
        sensor_2_add.add_parameter(parameter_2_add)
        rec_2_add.add_sensor(sensor_2_add)

        added_recorder = db_inventory.add_recorder(rec_2_add)
        self.assertEqual(len(db_inventory.recorders), 2)
        self.assertEqual(db_inventory.recorders[1], added_recorder)
        self.assertEqual(len(db_inventory.recorders[1].sensors), 1)
        self.assertIsInstance(db_inventory.recorders[1].sensors[0], DbSensor)
        self.assertEqual(len(db_inventory.recorders[1].geom_recorder.sensors), 1)
        self.assertEqual(len(added_recorder.sensors[0].parameters), 1)
        self.assertIsInstance(added_recorder.sensors[0].parameters[0], DbSensorParameter)
        self.assertEqual(len(added_recorder.geom_recorder.sensors[0].parameters), 1)



    def test_load_network(self):
        db_inventory = DbInventory('test', self.project)

        # Add a network to the db_inventory.
        net_2_add = Network(name = 'XX', description = 'A test network.')
        added_network = db_inventory.add_network(net_2_add)
        self.assertIsInstance(added_network, DbNetwork)
        self.assertEqual(len(db_inventory.networks), 1)

        db_inventory.update_db()
        db_inventory.close()

        db_inventory_load = DbInventory('test', self.project)
        db_inventory_load.load_networks()
        db_inventory_load.close()



    '''
    def test_update_db(self):
        db_inventory = DbInventory('test', self.project)

        # Add a network to the db_inventory.
        net_2_add = Network(name = 'XX', description = 'A test network.')
        added_network = db_inventory.add_network(net_2_add)

        db_inventory.update_db()
    '''
   
    ''' 
    def test_load_inventory(self):
        print "test_load_inventory\n"
        db_inventory = DbInventory('test', self.project)
        print "load()\n"
        db_inventory.load()
        print "close()\n"
        db_inventory.close()
    ''' 

def suite():
#    tests = ['testXmlImport']
#    return unittest.TestSuite(map(InventoryTestCase, tests))
    return unittest.makeSuite(DbInventoryTestCase, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')

