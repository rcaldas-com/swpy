# SWPY
## Automate maintenance in managed Switches with Python and Telnet

I wrote this from the need to update the firmware and enable the ssh module of 100+ Extreme Networks Switches in a park of 900+ Switches (in most Enterasys A2,B3,B5,C5... models). 

The initial project was to update the Radius authentication setting of the 900+ switches to our new Radius server in a batch, that original code will be mixed with this one by the time.

### What's working?
For now it can:
* Update Extreme Switch firmware.
* Enable Extreme SSH Module.
* Update Extreme Radius configuration.
* Simultaneous runing with multiprocessing.

### Bash script to generate input file

I create a Bash script to read a .csv file (input.csv) exported from Netsight tool with the list of all switches and their informations.

The script filter the .csv list in other file (input.all) with just "IP,Model_Name" format, fixing null entries that some models (HP and Dell) reproduces in the file exported from NetSight.

The bash script also separate the Enterasys models and Extreme models in files (input.en and input.ex), these files are used to update the Radius server in all switches that have the same sintax commands. All of this will be ported to the Python program soon and the bash eliminated.

### Input file

The Pyhton program use the list of all switchs filtered (input.all), it have the format:
```
$ cat input.all
172.24.204.10,X430-24t
172.24.204.11,B5G124-24P2
172.24.204.20,X430-24t
172.24.204.21,C5G124-24P2
172.24.204.30,X430-24t
...
```
### Runing
With 'model', 'lastv' and 'img' set in .py file:

`$ ./attfirmware.py input.all`

Then it:
* Find for the selected model.
* Login with radius.
  - If can't login with Radius profile it try to update radius config with a local adm login (set 'useradm').
* Check if host have the last firmware version (set 'lastv' and 'img' file)
* Check if host have SSH module enabled.
* Reboot if necessary

To download firmware from switch I configure a light TFTP server on localhost.



##### TODO:
* Filter .csv in Python
* Fix model selection, maybe with dictionary
* Insert Enterasys comands to Radius
* TFTP Documentation

