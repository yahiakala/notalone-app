"""Test onboarding process. Need to be logged in as a user with no auth privileges."""
import unittest
import anvil.server
import time


class TestNewApplicant(unittest.TestCase):
    """Test basic chatbot functionality"""
    def setUp(self):
        # Code to run before each test method
        print("Setting up before the test")

    def tearDown(self):
        # Code to run after each test method
        print("Cleaning up after the test")

    def test_book_interview(self):
        pass

    def test_try_get_users(self):
        _ = anvil.server.call('get_users')