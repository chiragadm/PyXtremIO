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

 
* # How To Install This Library?
  Please run following command to install this library. (You will need GIT CLI & pip3(or pip) installed on your server.)
  * $ cd SOME_DIRECTORY (Directory that you want to install this program)
  * $ git clone https://URL
  ```
  cd /AnyNewDictory
  git clone https://github.com/chiragadm/PyXtremIO
  sudo pip3 install .
    
  ```

  # Setting up configuration file (fabview.cfg):
  Once the program is installed in directory as per above instruction, now it is time to configure the settings file.
  You will need to put the core switches information as per following. (Core switches are the switches that are connected to all other switches in your fabric)
  
  For example, I have two fabrics in my environment. Each fabric has one core switch. 
  * Fabric A core switch name is coreA.
  * Fabric B core switch name is coreB.
  
  With above example, my settings file (fabview.cfg) will look like below.
  Setting file is located in etc directory under your install directory.
  * $ cd SOME_DIRECTORY/etc
  * $ cat fabview.cfg
    ```
    [Fabric_Config]
    SWITCH: coreA,coreB
    SW_USER:
    SW_PASSWORD:
    ```