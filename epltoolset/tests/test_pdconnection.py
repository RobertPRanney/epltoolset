"""
FILE: test_pdconection.py
AUTHOR: Robert Ranney
DESCR: Test that the class for pandas cx_oralce connections does all that it is
       supposed to do. This test is predicated on having access to an Oracle
       database, al there has to be a connection defined called test_conn.
"""

import unittest
import json

import cx_Oracle
import pandas as pd

from epltoolset.pdConnection import PdConnection, Credentials


create_test_table_sql = """CREATE TABLE epl_test (
    PERSONID int,
    LASTNAME varchar(255),
    FIRSTNAME varchar(255),
    AGE float
)"""

drop_test_table_sql = """DROP TABLE epl_test"""

insert_record1_sql = """INSERT INTO epl_test
VALUES (1, 'robert', 'ranney', 29.3)
"""

insert_record2_sql = """INSERT INTO epl_test
VALUES (2, 'bugs', 'bunny', 35.8)
"""

query_test_table_sql = """SELECT * FROM epl_test"""




class TestInstantiationFunctionality(unittest.TestCase):
    """Test that intialization of Connections work"""
    def setUp(self):
        """Run before tests"""
        pass


    def tearDown(self):
        """Run after Tests"""
        pass


    def test_can_initialize_empty(self):
        """Make sure object initialization works with empty params"""
        obj = PdConnection()
        self.assertIsNotNone(obj)
        self.assertIsInstance(obj, PdConnection)


    def test_can_initialize(self):
        """Make sure initialized object works"""
        obj = PdConnection(cred_set='test', cred_file='test', fetch_size=50)
        self.assertIsNotNone(obj)
        self.assertIsInstance(obj, PdConnection)
        self.assertEqual(obj.cred_set, 'test')
        self.assertEqual(obj.cred_file, 'test')
        self.assertEqual(obj.fetch_size, 50)


class TestSimpleFunctionality(unittest.TestCase):
    """Simple functions that check files"""
    def setUp(self):
        """Run Before Tests"""
        pass


    def tearDown(self):
        """Run After Tests"""
        pass


    def test_cred_file_exists(self):
        """make sure this return proper True False under right circumstances"""
        obj = PdConnection(cred_file='not_a_file.creds')
        actual = obj.cred_file_exists()
        self.assertFalse(actual)

        obj = PdConnection(cred_file='epltoolset/.connectcreds.creds')
        actual = obj.cred_file_exists()
        self.assertTrue(actual)


    def test_cred_set_exists(self):
        """Make sure can tell when and when cred sets are not there"""
        obj = PdConnection(cred_file='epltoolset/.connectcreds.creds')
        obj.cred_set = 'NOT_CREDS'
        actual = obj.cred_set_exists()
        self.assertFalse(actual)

        obj.cred_set = "TEST_SPOT"
        actual = obj.cred_set_exists()
        self.assertTrue(actual)


    def test_all_cred_sets_in_file(self):
        """Make sure a nice list is returned"""
        obj = PdConnection(cred_file='epltoolset/.connectcreds.creds')
        actual = obj.all_cred_sets_in_file()
        self.assertIsNotNone(actual)
        self.assertIsInstance(actual, list)
        self.assertTrue(len(actual) > 0)


    def test_load_cred_set(self):
        """Make sure that creds can get loaded correctly"""
        obj = PdConnection(cred_file='epltoolset/.connectcreds.creds',
                           cred_set='TEST_SPOT')
        self.assertIsNone(obj.creds)
        returned = obj.load_cred_set()
        self.assertIsInstance(returned, PdConnection)

        self.assertIsInstance(obj.creds, Credentials)



class TestConnectionFunctions(unittest.TestCase):
    """Make sure connections things can work"""
    def setUp(self):
        """Run Before Tests"""
        self.widget = PdConnection(cred_file='epltoolset/.connectcreds.creds',
                           cred_set='TEST_SPOT').load_cred_set()


    def tearDown(self):
        """Run After Tests"""
        self.widget = None


    def test_can_connect(self):
        """make sure test connect works"""
        actual = self.widget.can_connect()
        self.assertTrue(actual)

        # Alter credenrtials to fail connection attempt
        self.widget.creds.password = 'bad_password'
        actual = self.widget.can_connect()
        self.assertFalse(actual)


    def test_make_and_close_connection(self):
        """Make sure connections function returns cx Oracle connection"""
        # Connect and test state
        returned = self.widget.make_connection()
        self.assertIsInstance(returned, PdConnection)
        self.assertIsNotNone(self.widget.conn)
        self.assertIsInstance(self.widget.conn, cx_Oracle.Connection)
        self.assertTrue(self.widget.is_connected())

        # End connection and test state
        returned = self.widget.close_connection()
        self.assertIsInstance(returned, PdConnection)
        self.assertIsNone(self.widget.conn)
        self.assertFalse(self.widget.is_connected())


class TestExecuteFunctions(unittest.TestCase):
    """Make sure arbitrary sql can run"""
    def setUp(self):
        """Run Before Tests"""
        self.widget = PdConnection(cred_file='epltoolset/.connectcreds.creds',
                           cred_set='TEST_SPOT').make_connection()


    def tearDown(self):
        """Run After Tests"""
        self.widget = None


    def test_execute_sql(self):
        """Execute some Queries, if it returns then it worked"""
        returned = self.widget.execute_sql(create_test_table_sql)
        self.assertIsInstance(returned, PdConnection)

        returned = self.widget.execute_sql(drop_test_table_sql)
        self.assertIsInstance(returned, PdConnection)


class TestCrudFunctions(unittest.TestCase):
    """Make sure querying works properly"""
    def setUp(self):
        """Run Before Tests"""
        self.widget = PdConnection(cred_file='epltoolset/.connectcreds.creds',
                           cred_set='TEST_SPOT').make_connection()
        self.widget.execute_sql(create_test_table_sql, keep_open=True)
        self.widget.execute_sql(insert_record1_sql, keep_open=True)
        self.widget.execute_sql(insert_record2_sql)


    def tearDown(self):
        """Run After Tests"""
        try:
            self.widget.execute_sql(drop_test_table_sql)
        except:
            pass
        self.widget = None


    def test_sql_to_dataframe(self):
        """Make sure sql statement can execute and make a dataframe"""
        df = self.widget.sql_to_dataframe(query_test_table_sql)
        self.assertIsNotNone(df)
        self.assertIsInstance(df, pd.DataFrame)
        row_count, col_count = df.shape
        self.assertEqual(row_count, 2)
        self.assertEqual(col_count, 4)

        columns = df.columns
        self.assertEqual(4, len(columns))


    def test_ddl_string_from_df(self):
        """Make sure a proper string can get generated"""
        df = self.widget.sql_to_dataframe(query_test_table_sql)
        sql = self.widget.ddl_string_from_df(df, 'epl_test')
        self.assertIsInstance(sql, str)
        self.assertEqual(sql, create_test_table_sql)


    def test_insert_bind_string_from_df(self):
        """make sure proper string created"""
        expected = 'INSERT INTO test (PERSONID, LASTNAME, FIRSTNAME, AGE) values (:1, :2, :3, :4)'
        df = self.widget.sql_to_dataframe(query_test_table_sql)
        actual = self.widget.insert_bind_string_from_df(df, 'test')

        self.assertEqual(expected, actual)


    def test_df_to_table(self):
        """make sure a dataframe can create a new tables"""
        df = self.widget.sql_to_dataframe(query_test_table_sql)
        self.widget.df_to_table(df, 'epl_test2')
        self.widget.execute_sql("DROP TABLE epl_test2")
