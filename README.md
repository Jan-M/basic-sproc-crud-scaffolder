basic-sproc-crud-scaffolder
=========================== 

The basic-sproc-crud-scaffolder is a **command line code generator** and the perfect accompaniment to Zalando's [Java Sproc Wrapper](https://github.com/zalando/java-sproc-wrapper). Its goal is to make interacting with your Postgres database as quick and easy as possible.

Installation
------------

Installation is very straightforward, simply clone the repository directly from GitHub to a directly of your choice:

```bash
$ git clone git://github.com/zalando/java-sproc-wrapper.git
```

Usage
-----

To get a quick, "Hello World" type view of what the script can do for you, simply run:
```bash
$ ./run.py
```

Show the command line options available:

```bash
$ ./run.py -h
```

And run against a table:
```bash
$ ./run.py --host= --port=5432 --database= --user= --table= --schema=
```

The script will create a directory called ```/output``` that contains a ```database``` and ```src``` subdirecty. The former contains a database type and all sprocs that match the table you ran the script against while the latter contains the Java domain type and persistence layer that is setup to run with Zalando's [Java Sproc Wrapper](https://github.com/zalando/java-sproc-wrapper).