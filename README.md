# PyXtremIO
PyXtremIO is a python library that can be used to facilitate storage automation of Dell EMC's XtremIO. It uses ReST API to make call to XtremIO's XMS server for storage automation. Portion of this code is adapted from https://github.com/ciarams87/PyU4V. You may get XtremIO XMS's ReST API documentation from https://support.emc.com website.  

# What Is Supported?
PyXtremIO supports XMS 4.x and 6.0.X
* Current Features:
  * Storage Allocation
  * Storage Deallocation
  * Snapshot Management
* Potential Future Features:
  * Performance Metrics Gathering
  * Alert Management
  * Inventory Discovery

 
# How To Install This Library?
  Please run following command to install this library. (You will need GIT CLI & pip3(or pip) installed on your server.)
  * $ cd SOME_DIRECTORY (Directory that you want to install this program)
  * $ git clone https://URL
  ```
  cd /AnyNewDictory
  git clone https://github.com/chiragadm/PyXtremIO
  sudo pip3 install .
    
  ```

  # Setting Up PyXtremIO.yaml File For Tracking Logging:
  Once this library is installed, you will have an option to create PyXtremIO.yaml file that contains configuration settings to enable rotational logs. Upon appropriate setting in the yaml file, log files will retain any informational or error logs.
  Please find following example of PyXtremIO.yaml file.
  ```
  cat PyXtremIO.yaml
  ---
  version: 1
  disable_existing_loggers: False
  formatters:
      simple:
          format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
  handlers:
      console:
          class: logging.StreamHandler
          level: DEBUG
          formatter: simple
          stream: ext://sys.stdout
  
      info_file_handler:
          class: logging.handlers.RotatingFileHandler
          level: INFO
          formatter: simple
          filename: /tmp/PyXtremIO_info.log
          maxBytes: 10485760 # 10MB
          backupCount: 20
          encoding: utf8
  
      error_file_handler:
          class: logging.handlers.RotatingFileHandler
          level: ERROR
          formatter: simple
          filename: /tmp/PyXtremIO_errors.log
          maxBytes: 10485760 # 10MB
          backupCount: 20
          encoding: utf8
  
  loggers:
      PyXtremIO:
          level: DEBUG
          handlers: [console, info_file_handler, error_file_handler]
          #handlers: [console]
          propagate: no
  
  root:
      level: INFO
      handlers: [console, info_file_handler, error_file_handler]  
  ```
  
  You may put this yaml file in direcotry of your choice. By default, this library looks for environment variable called PYXTREMIO_LOG_CFG. 
  This environment variable should contains full path of your PyXtremIO.yaml file. If this environment variable is not set, library will check
  PyXtremIO.yaml file in our working directory. At last if this file do not exists there, library will use default logging method. This default 
  method will not log your events.  
  
# How To Use This Library?
As of now, this library has close to 90+ methods you can call. However, I have listed most useful methods in "testing" directory. 
Please find following file lists that demonstrate use of this hand few useful methods.
```
File List:
01_allocation_storage_new_server.py
02_add_new_storage_to_existing_ig.py
03_add_existing_storage_new_server.py
04_add_existing_storag_existing_server.py
05_remove_volumes_from_server.py
06_generate_snapshot.py
07_remove_snapshot.py

```
  