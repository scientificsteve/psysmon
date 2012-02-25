'''
Created on May 17, 2011

@author: Stefan Mertl
'''

import unittest
import psysmon
import logging
from psysmon.core.base import Base
from psysmon.core.waveserver import WaveServer
import psysmon.core.gui as psygui
import os
import copy


class EditGeometryDlgTestCase(unittest.TestCase):
    """
    Test suite for psysmon.packages.geometry.editGeometry.EditGeometryDlg
    """
    def setUp(self):
        # Configure the logger.
        logger = logging.getLogger('psysmon')
        logger.setLevel(psysmon.logConfig['level'])
        logger.addHandler(psysmon.getLoggerHandler())

        # Get the pSysmon base directory.
        psyBaseDir = '/home/stefan/01_gtd/04_aktuelleProjekte/pSysmon/01_src/psysmon/lib/psysmon/'
        psyBaseDir = os.path.dirname(psyBaseDir)

        # Initialize the pSysmon base object.
        self.psyBase = Base(psyBaseDir)
        #psyBase.scan4Package()

        # Load the pSysmon test project.
        path = "/home/stefan/01_gtd/04_aktuelleProjekte/pSysmon/03_pSysmonProjects/test/test.ppr"
        self.psyBase.loadPsysmonProject(path)

        # Quest for the user and the database password.
        self.psyBase.project.setActiveUser('stefan','')

        # Load the database structure of the project packages.
        self.psyBase.project.loadDatabaseStructure(self.psyBase.packageMgr.packages)


        # Create the project waveserver.
        waveserver = WaveServer('sqlDB', self.psyBase.project)
        self.psyBase.project.addWaveServer('psysmon database', waveserver)
        
        self.project = self.psyBase.project

        
    def tearDown(self):
        print "\n\nEs war sehr schoen - auf Wiederseh'n.\n"

    def testDlg(self):
        self.project.waveserver['psysmon database'].getWaveform(station=['SITA', 'ALBA'])

#def suite():
#    suite = unittest.makeSuite(EditGeometryDlgTestCase, 'test')
#    return suite

def suite():
    tests = ['test']
    # return unittest.TestSuite(map(EditGeometryDlgTestCase, tests))
    return unittest.makeSuite(EditGeometryDlgTestCase, 'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

