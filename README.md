# EPL Toolset

EPL stands for extract-pandas-load. A package to make oracle-python ETL script development easier. Working with cx_oracle and pandas can be overly cumbersome when only simple functionals are needed. This package try to make this interactions with need less boilerplate code. Meant to work with python 3.6

### Installation
epltoolset is avaialbe on pypi and can easier installed with use of pip.
```shell
pip install epltoolset
```

### Creating Credential Files
The package provides a simple to use script to generate credential files. These credentials are then stored in a json format.
```shell
manage-oracle-creds
```
The format for the credential files is a follows if instead you want to edit them directly.
```json
{
    "<cred_set_name>": {
        "HOST": "<host>",
        "PORT": <port>,
        "SID": "<sid>",
        "USERNAME": "<username>",
        "PASSWORD": "<password>",
    },
    "<cred_set_name>":{
        ...
    }
    ...
}
```

### Importing for Use
The main class is the PdConnection Class. There is also a credentials class that is utilized by PdConnection class, but it is not needed to be imported unless finer control is needed.
```python
from epltoolset import Credentials, PdConnection
```

## Using the PdConnection class

#### Instantiating object
Connection object can be created and then viability of object can be checked through methods
```python
# Instantiate a connection object
cn = PdConnection(cred_set="TEST_SPOT", cred_file='.connectcreds.creds')

# Check everything is in order
if cn.cred_file_exists():
    print("Specified Credential File Exists")
if cn.cred_set_exists():
    print("Specified Credential File Exists")
cn.load_cred_set()
if cn.can_connect():
    print("Tested that connection Possible")
```

```shell
Specified Credential File Exists
Specified Credential File Exists
Tested that connection Possible
```

Chaining of methods can also be used to instantiate and load credentials, or chain many other methods together.

```python
cn = PdConnection(cred_set="TEST_SPOT").load_cred_set()
```

#### Querying oracle table in to a dataframe
It is possible to take a sql query directly to a pandas dataframe without worrying about the cx_oralce connection that is needed to make this possible.
```python
df = cn.sql_to_dataframe(sql="SELECT * FROM example_table_rr")
print(df.head())
```

```shell
FAVORITE_PASTRY MEMBERDATE  PERSONID  SCORE
0          muffin  23-NOV-15         1    3.2
1           scone  13-SEP-12         2    2.3
2           bagel  03-FEB-16         3    1.2
3           donut  01-DEC-05         4    0.4
4         cookies  05-NOV-17         5    4.0
```

#### Placing a dataframe into an oracle table
After doing any operations that are needed then same connection object can be used to then place the dataframe back into the database. If the table already exists then the table create will fail, unless it is specified to drop it.

```python
cn.df_to_table(df, "example_table_post_trans_rr", drop_existing=True)
```

#### Some other stuff
Generic sql can be executed as well
```python
cn.execute_sql(some_sql_string)
```
Other functions can be used for finer control of the connection, although not necessary since connections will be closed and opened if needed by the individuals methods.
```python
cn.make_connection()
cn.close_connection()
cn.is_connected()
```
Attributes of the connection object can be accessed directly if needed to change the function. Some of these can also be set at instantiation, or can be left to default values.
```python
cn.cred_set      # To maybe change the database or schema with same file
cn.fetch_size    # integer that can affect querying performance
self.creds       # epltoolset.Credentials, loaded by method
self.conn        # cx_Oracle.Connection, can be kept open between uses
```
