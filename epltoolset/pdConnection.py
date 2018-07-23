import os
import json

import cx_Oracle


class Credentials(object):
    """tbd"""

    def __init__(self, host='', port='', sid='', username='', password=''):
        """tbd"""
        self.host = host
        self.port = port
        self.sid = sid
        self.username = username
        self.password = password

    def is_complete(self):
        """tbd"""
        for attr, value in self.__dict__.items():
            if value == '':
                return False
            return True

    def attrs(self):
        """tbd"""
        return self.__dict__


    def __str__(self):
        """tbd"""
        creds_string = f"Host: {self.host}\n" \
                       f"Port: {self.port}\n" \
                       f"SID: {self.sid}\n" \
                       f"Username: {self.username}\n" \
                       f"Password: {self.password}\n"
        return creds_string


class PdConnection(object):
    """tbd"""

    def __init__(self, cred_set=None, cred_file='.connectcreds.creds'):
        """tbd"""
        # Set the passed in attributes
        self.cred_set = credential_set
        self.cred_file = cred_file

        # Set attributes that are loaded later to None
        self.creds = None


    def cred_file_exists(self):
        """tbd"""
        return os.path.isfile(self.cred_file)

    def cred_set_exists(self):
        """tbd"""
        if not self.cred_file_exists:
            return False

        with open(self.cred_file, 'r') as in_json:
            all_creds = json.load(in_json)
        return self.cred_set in all_creds

    def show_all_cred_sets(self):
        """tbd"""
        pass


    def load_creds(self):
        """tbd"""
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
