import unittest
import os
from data import Data
from people import Staff


class PeopleTest(unittest.TestCase):
    """Test for Pople (Staff and People)"""

    def setUp(self):
        self.data = Data()

    def test_create_fellow(self):
        """
        Assert that a user can add a new fellow
        """
        fellows = self.data.fetch_data("fellows", False)
        self.assertEqual(0, len(fellows))

        self.data.create_living_spaces(['woodwing', 'westwing', 'eastwing'])

        new_fellow = self.data.create_fellow("John", "Kariuki", "y")
        self.assertTrue(new_fellow)

        fellows = self.data.fetch_data("fellows", False)
        self.assertEqual(1, len(fellows))

    def test_create_staff(self):
        """
        Assert that a user can add a new staff member
        """
        staff = self.data.fetch_data("staff", False)
        self.assertEqual(0, len(staff))

        new_staff = self.data.create_staff('Dej', 'Loaf')
        self.assertTrue(new_staff)

        staff = self.data.fetch_data("staff", False)
        self.assertEqual(1, len(staff))

        self.data.create_office_spaces(['camelot', 'midgar'])
        new_staff = self.data.create_staff('Dej', 'Loaf')
        self.assertTrue(new_staff)

        staff = self.data.fetch_data("staff", False)
        self.assertEqual(2, len(staff))

    def test_reallocate_staff(self):
        """
        Assert that a fellow can be reallocated to another office space
        """
        self.data.create_office_spaces(['camelot'])
        self.data.create_staff('John', 'Kariuki')

        staff = Staff()
        invalid_id = staff.reallocate(
            {'<person_identifier>': 10, '<new_room_name>': 'camelot'})
        self.assertEqual('No staff by the provided staff id 10', invalid_id)

        invalid_allocation = staff.reallocate(
            {'<person_identifier>': 1, '<new_room_name>': 'camelot'})
        self.assertEqual(
            'John Kariuki already belongs in camelot', invalid_allocation)

        invalid_office = staff.reallocate(
            {'<person_identifier>': 1, '<new_room_name>': 'imaginaryroom'})
        self.assertEqual(
            'No office space by that name. Please try again', invalid_office)

        self.data.create_office_spaces(['midgar'])
        valid_allocation = staff.reallocate(
            {'<person_identifier>': 1, '<new_room_name>': 'midgar'})
        self.assertEqual(
            'John Kariuki is now residing in midgar', valid_allocation)

    def tearDown(self):
        """Delete the test database"""
        if os.path.exists('room_alloc.db'):
            os.remove('room_alloc.db')

if __name__ == '__main__':
    unittest.main()
