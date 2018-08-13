"""
FILE: pdConnection.py
AUTHOR: Robert Ranney
DESCR: Object to abstract management of cx_Oracle to dataframe and visa
       versa. Simplify connection and dataframe creation, querying, loading.
       Seperate object to abstact away credentials as well used by
       connection object.
USAGE: from pdConnection import PdConnection
"""

# STANDARD IMPORT STATEMENTS
import os
import re
import json

# THIRD PARTY IMPORT STATEMENTS
import cx_Oracle
import pandas as pd


# CONSTANT DECLARATIONS
DEFAULT_FETCH_SIZE = 250000

# MAPPINGS
PD_TO_ORACLE_TYPES = {
    'int64': 'int',
    'object': 'varchar2(255)',
    'float64': 'number',
    'datetime64[ns]': 'date'
}


# LOCAL CLASS DEFINTIONS
class Credentials(object):
    """
    DESCR: object to handle crednentials data structure, allows them to be
           accessed as atributes and allows some simple helper functions.
    """

    def __init__(self, host='', port=None, sid='', username='', password=''):
        """
        DESCR: initialize object with same things cx_Oracle wants
        INPUT: host - str - which networked machine holds database
               port - int - port on host for db
               sid - str - name of database
               username - str - log in name
               password - str - password associated with username
        OUTPUT: self, inherited method output
        """
        # Initiliaze all creds, default to empty to fill in later
        self.host = host
        self.port = port
        self.sid = sid
        self.username = username
        self.password = password


    def is_complete(self):
        """
        DESCR: check is all credential attributes are filled in
        INPUT: None
        OUTPUT: bool - True is all attributes filled in
        """
        # Iterate over attrivbutes and check one by one
        for attr, value in self.__dict__.items():
            if value == '' or value is None:
                return False
            return True


    def attrs(self):
        """
        DESCR: Return dictionary of attributes for connections
        INPUT: None
        OUTPUT: dict - attributes as dictionary
        """
        # More explicit that accessing directly
        return self.__dict__


    def __str__(self):
        """
        DESCR: Pretty Print of connection defintion
        INPUT: None
        OUTPUT: str - attributes spread over new lines
        """
        creds_string = f"Host: {self.host}\n" \
                       f"Port: {self.port}\n" \
                       f"SID: {self.sid}\n" \
                       f"Username: {self.username}\n" \
                       f"Password: {self.password}\n"
        return creds_string


class PdConnection(object):
    """
    The PdConnection Class is used to abstract away some of the cx_Oracle and
    pandas functioning
    """

    def __init__(self, cred_set=None, cred_file='.connectcreds.creds',
                 fetch_size=DEFAULT_FETCH_SIZE):
        """
        DESCR: Initialize the object with the bare minimum needed to start a
               connection, connection is actually initialize by other methods.
        INPUT: cred_set - str - name of credential set to look for in file
               cred_file - str - relative or absolute path to file with creds
               fetch_size - int - rows per sql fetch operation
        OUTPUT: self, inherited
        """
        # Set the passed in attributes
        self.cred_set = cred_set
        self.cred_file = cred_file
        self.fetch_size = fetch_size

        # Set attributes that are loaded later to None
        self.creds = None          # Credentials object loaded by load_cred_set
        self.conn = None           # cx_oracle connection


    def cred_file_exists(self):
        """
        DESCR: Check that the file attribute acutally exists
        INPUT: None
        OUTPUT: bool - True if attribute is a file
        """
        return os.path.isfile(self.cred_file)


    def cred_set_exists(self):
        """
        DESCR: Make sure that within the cred dictionary the name connection
               is real.
        INPUT: None
        OUTPUT: bool - False if file doesn't exist or set not in file
        """
        # Don't want to fail for file being wrong
        if not self.cred_file_exists:
            return False

        # Open file and make sure set is in there
        with open(self.cred_file, 'r') as in_json:
            all_creds = json.load(in_json)
        return self.cred_set in all_creds


    def all_cred_sets_in_file(self):
        """
        DESCR: Open file and list all cred names
        INPUT: None
        OUTPUT: list - list of cred set names
        """
        # Make sure file exists
        if not self.cred_file_exists():
            return []

        with open(self.cred_file, 'r') as in_json:
            cred_dict = json.load(in_json)

        return list(cred_dict.keys())


    def load_cred_set(self):
        """
        DESCR: read in a specific set of creds and save as an attribute
        INPUT: None
        OUTPUT: self - for chaining
        """
        # report lack of existing file
        if not self.cred_file_exists:
            print(f"Cred File: {self.cred_file} does not exist")
            return self

        # report lack of proper cred set
        if not self.cred_set_exists:
            print(f"Cred Set: {self.cred_set} does not exist")
            return self

        # open credential file and read into Cred object
        with open(self.cred_file, 'r') as in_json:
            cred_dict = json.load(in_json)[self.cred_set]
        self.creds = Credentials(host=cred_dict['HOST'],
                                 port=cred_dict['PORT'],
                                 sid=cred_dict['SID'],
                                 username=cred_dict['USERNAME'],
                                 password=cred_dict['PASSWORD'])
        return self


    def can_connect(self):
        """
        DESCR: See if a connection is possible with provided creds
               Not helpful for troublshooting since errors thrown away
        INPUT: None
        OUTPUT: bool - True is no errors on connection else False
        """
        if self.creds is None:
            print(f"Credentials Not Loaded")
            return False

        # Package into dsn for simpler use
        dsn = cx_Oracle.makedsn(self.creds.host,
                                self.creds.port,
                                self.creds.sid)

        # Test connection, if errors arise they can be checked elsewhere
        try:
            conn = cx_Oracle.connect(self.creds.username,
                                     self.creds.password,
                                     dsn)
            test_conn = conn.ping()
            if test_conn is None:
                return True
        except:
            return False


    def make_connection(self):
        """
        DESCR: Establish a connection as an attribute
        INPUT: None
        OUPUT: self
        """
        # Load creds is implied if not done yet
        if self.creds is None:
            self.load_cred_set()

        # Don't let connections pile up
        if self.conn is not None:
            self.conn.close()

        # Package into dsn for simpler use
        dsn = cx_Oracle.makedsn(self.creds.host, self.creds.port, self.creds.sid)
        self.conn = cx_Oracle.connect(self.creds.username, self.creds.password, dsn)
        return self


    def is_connected(self):
        """
        DESCR: check if object has an active connection
        INPUT: None
        OUTPUT: bool - True is connection is not None
        """
        return self.conn is not None


    def close_connection(self):
        """
        DESCR: if there is a connection close it and reset to None
        INPUT: None
        OUTPUT: self
        """
        # Don't want to try and close None
        if self.conn is None:
            return self
        # Close and reset
        self.conn.close()
        self.conn = None
        return self


    def execute_sql(self, sql, keep_open=False):
        """allow the connection to execute and arbitrary sql"""
        # Make sure we have a connection before using it
        if self.conn is None:
            self.make_connection()

        # Execute the query
        cursor = self.conn.cursor()
        cursor.execute(sql)

        # commit sql statement
        self.conn.commit()

        # Clean up cursor and maybe connection
        cursor.close()
        if not keep_open:
            self.close_connection()

        return self


    def sql_to_dataframe(self, sql, keep_open=False):
        """
        DESCR: given a query pull the resulting results into a dataframe
        INPUT: sql - str - Oracle standard sql query
               keep_open - bool - if True do not close connection
        OUTPUT: pd.DataFrame - cols and data from fetch
        """
        # Make sure we have a connection before trying to use it
        if self.conn is None:
            self.make_connection()

        # Make cursor and make some adjustments
        cursor = self.conn.cursor()
        cursor.arraysize = self.fetch_size

        # Execute the query
        cursor.execute(sql)

        # Pull the fnished query into a dataframe
        columns = [x[0] for x in cursor.description]
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=columns)

        # Cleanup up curosr, and maybe connection
        cursor.close()
        if not keep_open:
            self.close_connection()

        return df


    def df_to_table(self, df, table_name, keep_open=False, drop_existing=False,
                    subset=None):
        """
        DESCR: given a dataframe insert it into an oracle table
        INPUT: df - pd.DataFrame - dataframe to turn into table
               table_name - str - name of new table
               keep_open - bool - if false close connection
        OUTPUT: self
        """
        # Get Rid of existing table if needed
        if drop_existing:
            try:
                self.execute_sql(f"DROP TABLE {table_name}")
            except:
                pass

        # Create the table
        sql = self.ddl_string_from_df(df, table_name)
        self.execute_sql(sql)

        # Insert into table
        sql = self.insert_bind_string_from_df(df, table_name)
        # Make sure we have a connection before trying to use it
        if self.conn is None:
            self.make_connection()
        cursor = self.conn.cursor()
        cursor.prepare(sql)

        insert_values = df.values.tolist()
        cursor.executemany(None, insert_values)
        self.conn.commit()

        return self


    @staticmethod
    def ddl_string_from_df(df, table_name):
        """
        DESCR: from a dataframe generate a string for table creation
        INPUT: df - pd.DataFrame - used to generate the string
               table_name - str - what table to use in the string name
        OUTPUT: str - ready to execute sql string
        """
        sql = f"CREATE TABLE {table_name} (\n"

        for col_name, dtype  in df.dtypes.items():
            oracle_type = PD_TO_ORACLE_TYPES[dtype.name]
            sql += f"    {col_name} {oracle_type},\n"
        sql = sql[:-2] + "\n)"
        return sql


    @staticmethod
    def insert_bind_string_from_df(df, table_name, subset=None):
        """
        DESCR: from a dataframe generate a string usable for insert statements
        INPUT: df - pd.DataFrame - used to generate the string
               table_name - str - what table to use in the string name
        OUTPUT: str - ready to execute sql string
        """
        if subset is None:
            subset = df.columns.tolist()
        col_str = ', '.join(subset)

        val_str = ', '.join([f":{str(x+1)}" for x in range(len(subset))])

        sql = f"INSERT INTO {table_name} ({col_str}) values ({val_str})"
        return sql


    def __str__(self):
        """
        DESCR: pretty print of object
        INPUT: None
        OUTPUT str - pretty version of object
        """
        # Always present stuff
        pretty_string = f"Cred File: {self.cred_file}\n"
        pretty_string += f"Cred Set: {self.cred_set}\n"

        # See if creds loaded
        if self.creds is None:
            pretty_string += f"Creds: Not Loaded\n"
        else:
            pretty_string += f"Creds: Loaded\n"

        # See if connection open
        if self.conn is None:
            pretty_string += f"Conn: Not Open\n"
        else:
            pretty_string += f"Conn: Open\n"

        return self


    def __del__(self):
        """
        DESCR: Make sure connections are closed at destruction
        INPUT: None
        OUTPUT: None
        """
        if self.conn is not None:
            self.conn.close()
        del self
