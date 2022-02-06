#Cat-relay
## About
Cat-relay is a Ham/SWL utility, written in Python3. It synchronizes frequency between SDR++ and RUMlogNG logging software, 
so SDR++ can act as a panadapter for your radio.

## Supported platforms and software
Although Cat-relay is platform independent, the main use case is running SDR++ with RUMlogNG on MacOS. 
It may work with other SDR software that are compatible with Hamlib/Rigctl, or other logging software that uses Dxlab Commander 
commands. At this moment, no software other than SDR++ and RUMlogNG is tested, including Dxlab Commander. 

##  How is works
Cat-relay reads frequencies from SDR++ and RUMlogNG every 50ms (configurable), and synchronizes them if either of them changes.
It also synchronizes mode from SDR++ to RUMlogNG. (I haven't found a way to read mode from RUMlogNG yet).

## Prerequisites
- CAT control needs to be correctly configured in RUMlogNG
- "DxLab Suite Commander" needs to be set to "Start" in RUMLogNG
- "Rigctl Server" needs to be configured to run in SDR++
- Correct IP addresses for RUMlogNG and SDR++ need to be set in config.yml unless you run everything on the same computer
- Correct ports need to be set in config.yml, unless you happened to have the same ports as mine

## Dependencies
Cat-relay uses only one 3rd party library (pyyaml). To install it, open a terminal, go to the folder that contains cat-relay, 
and run following command:

```pip3 install -r requirements.txt```

## How to run
Open a terminal, go to the folder that contains cat-relay, and run following command:

```python3 listen.py```

Don't close the terminal window, you can minimize it if you'd like to.

## How to quit
Open the terminal window that cat-relay is running in and press Ctrl+C.