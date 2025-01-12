import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import MyApp, DataWindow


import unittest
import sqlite3
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt


app = QApplication([])

class TestMyApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])
        cls.window = MyApp()
        cls.window.show()
        cls.window.init_db()

    @classmethod
    def tearDownClass(cls):
        cls.window.conn.close()

    def setUp(self):
        self.window.is_recording = False
        self.window.last_cpu = None
        self.window.last_ram = None
        self.window.last_disk = None

        self.window.cursor.execute("DELETE FROM stats")
        self.window.conn.commit()

    def test_ui_elements(self):
        """Проверка, что все элементы интерфейса присутствуют"""
        self.assertTrue(self.window.cpu_label.isVisible())
        self.assertTrue(self.window.ram_label.isVisible())
        self.assertTrue(self.window.rom_label.isVisible())
        self.assertTrue(self.window.record_button.isVisible())
        self.assertTrue(self.window.view_button.isVisible())

    def test_database_connection(self):
        """Проверка подключения к базе данных"""
        self.assertIsInstance(self.window.conn, sqlite3.Connection)
        self.assertTrue(self.window.cursor.execute("SELECT 1"))

    def test_toggle_recording(self):
        """Проверка включения и выключения записи"""
        self.assertFalse(self.window.is_recording)
        self.window.toggle_recording()
        self.assertTrue(self.window.is_recording)
        self.window.toggle_recording()
        self.assertFalse(self.window.is_recording)

    def test_record_data(self):
        """Проверка записи данных в базу"""
        
        self.window.record_data(25.5, 8.0, 50.0)
        self.window.cursor.execute("SELECT * FROM stats")
        rows = self.window.cursor.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertAlmostEqual(rows[0][1], 25.5)
        self.assertAlmostEqual(rows[0][2], 8.0)
        self.assertAlmostEqual(rows[0][3], 50.0)

    def test_update_stats(self):
        """Проверка обновления данных"""
        
        self.window.update_stats()

        self.assertIn("ЦП:", self.window.cpu_label.text())
        self.assertIn("ОЗУ:", self.window.ram_label.text())
        self.assertIn("Диск:", self.window.rom_label.text())

    def test_show_data(self):
        """Проверка открытия окна с данными"""
        
        self.window.show_data()
        self.assertIsInstance(self.window.data_window, DataWindow)
        self.assertTrue(self.window.data_window.isVisible())

    def test_data_window_load(self):
        """Проверка загрузки данных в DataWindow"""
        
        self.window.record_data(30.0, 7.5, 40.0)
        self.window.show_data()

        table = self.window.data_window.table
        self.assertEqual(table.rowCount(), 1)
        self.assertEqual(table.item(0, 1).text(), "30.0")
        self.assertEqual(table.item(0, 2).text(), "7.5")
        self.assertEqual(table.item(0, 3).text(), "40.0")


if __name__ == "__main__":
    unittest.main()
