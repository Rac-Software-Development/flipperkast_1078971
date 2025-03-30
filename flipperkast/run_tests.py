import unittest
import sys

from tests.test_ball import TestBall
from tests.test_bumper import TestBumper
from tests.test_mqtt_client import TestMQTTClient
from tests.test_game_manager import TestGameManager
from tests.test_physics import TestPinballPhysics

def create_test_suite():
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    test_suite.addTest(loader.loadTestsFromTestCase(TestBall))
    test_suite.addTest(loader.loadTestsFromTestCase(TestBumper))
    test_suite.addTest(loader.loadTestsFromTestCase(TestMQTTClient))
    test_suite.addTest(loader.loadTestsFromTestCase(TestGameManager))
    test_suite.addTest(loader.loadTestsFromTestCase(TestPinballPhysics))
    
    return test_suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    test_suite = create_test_suite()
    result = runner.run(test_suite)
    
    if not result.wasSuccessful():
        sys.exit(1)