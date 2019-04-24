<h2> Setup </h2>

```git pull https://github.com/STEELISI/SENSS.git```

```cd SENSS/Setup```

Requirements for running SENSS Client
- mysqldb
- apache2
- php5, ensure that the file_upload flag is set to 1 in php.ini file. 

```python setup.py```

The setup will prompt for:
- type of installation which can be either for client or server
- mysqldb password
- root password (required to install dependencies and access the apache2 files)

