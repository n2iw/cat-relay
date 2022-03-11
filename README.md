#Cat-relay

## About
Cat-relay is a tool to change your SDR into a band scope/panadapter
for your radio. It does this by synchronizing the frequencies and modes
of your SDR software and your radio transceiver.

## Supported platforms and software
Cat-relay is written in Python3 and can run on Mac, Windows and Linux. However, the main use case is running SDR++ 
(cross-platform) with RUMlogNG or Flrig on MacOS or DXLab Commander on Windows. 

Cat-relay may work with other SDR software if the SDR provides a
Hamlib/Rigctl compatible TCP server. Cat-relay should work with other
logging software and rig control software if they provide one of two interfaces:

* A DXLab Commander compatible TCP server. RUMlogNG provides one of
  these if it is controlling the radio itself.
* A rig control server that uses an XML/RPC interface such as Flrig.

At this moment, only SDR++, RUMlogNG, DXLab Commander, and Flrig are
tested. MacLoggerDX will also work, except changing modes on SDR is not supported by MacLoggerDX. 


##  How is works
Cat-relay can work with two
different types of transceiver-computer setups (see figure below):

1. **Logger-controlled radio:** A logging software app like DXLabs Commander or
   RUMlogNG connects directly to the transceiver using a CAT
   interface. The logger interacts with all other applications wanting
   to control the radio.
2. **Server-controlled radio:** A rig control server app like Flrig connects to the
radio using a CAT interface. All other programs wishing to control the
transceiver talk to the rig control server.

![Cat-relay configurations](resources/cat-relay configurations.png
 "Cat-relay configurations diagram")

You can configure which configuration you are using in the file config.yml through the setting of the variable LOGGER_MODE. At present, it can have three possible values:

1. **`dxlab`:** Set LOGGER_MODE to `dxlab` to run cat-relay in a logger-controlled radio configuration.
2. **`flrig`:** Set LOGGER_MODE to `flrig` to run cat-relay in a server-controlled radio configuration.
3. **`wb:`** The value `wb` appears to configure cat-relay to interact with an undocumented/unsupported N1MM+ configuration.

Cat-relay reads frequencies and modes from SDR and the application
controlling your transceiver every 50ms (configurable), and synchronizes them if either
of them changes. Cat-relay, SDR, logging software, and Flrig can run on the same computer or different computers in the same local
network.

## 1. Logger-controlled Radio Configuration
### Mode mapping
Most common modes are supported in both SDR++ and RUMlogNG/DXLab Commander/Flrig therefore should work properly, e.g., CW, USB, LSB, AM and FM. 
Some modes are only supported in one or the other. For example, my radio (TS-590SG) reports RTTY mode, which SDR++ 
doesn't support. Following mapping and limitation is implemented. It suits my needs. I believe it will also be acceptable 
for other users.

- RTTY mode (from radio) will be mapped to USB mode
- WFM mode (from SDR++) will be mapped to FM mode
- RAW mode (from SDR++) will not be supported
- DSB mode (from SDR++) will not be supported

### Prerequisites
- Transceiver CAT control needs to be correctly configured in Flrig
- RUMLogNG. If you are using DXLab Commander, it's enabled by 
  default. You can change port (52002) by clicking "Net Serv" button in "General" tab.
- "Rigctl Server" needs to be configured to run in SDR++
- A correct IP address for Flrig must be set in config.yml unless you run everything on 
  the same computer
- Correct ports need to be set in config.yml, unless you happened to have the same ports as mine

### Settings
Example RUMlogNG settings 

![RUMlogNG settings](resources/RUMlogNG-settings.png "RUMlogNG settings")

Example DXLab Commander settings 

![Commander settings](resources/DXLab-Commander-settings.png "RUMlogNG settings")

Example SDR++ settings

![SDR++ settings](resources/SDR++-settings.png "SDR++ settings") 

## 2. Server-Controlled Radio Configuration
### Mode mapping
Most common modes are supported in both SDR++ and RUMlogNG/DXLab Commander/Flrig therefore should work properly, e.g., CW, USB, LSB, AM and FM. 
Some modes are only supported in one or the other. For example, my radio (TS-590SG) reports RTTY mode, which SDR++ 
doesn't support. Following mapping and limitation is implemented. It suits my needs. I believe it will also be acceptable 
for other users.

- RTTY mode (from radio) will be mapped to USB mode
- WFM mode (from SDR++) will be mapped to FM mode
- RAW mode (from SDR++) will not be supported
- DSB mode (from SDR++) will not be supported

### Prerequisites
- Transceiver CAT control needs to be correctly configured in RUMlogNG/DXLab Commander
- "DxLab Suite Commander" needs to be set to "Start" in RUMLogNG. If you are using DXLab Commander, it's enabled by 
  default. You can change port (52002) by clicking "Net Serv" button in "General" tab.
- "Rigctl Server" needs to be configured to run in SDR++
- Correct IP addresses for RUMlogNG/DXLab Commander and SDR++ need to be set in config.yml unless you run everything on 
  the same computer
- Correct ports need to be set in config.yml, unless you happened to have the same ports as mine

### Settings
Example RUMlogNG settings 

![RUMlogNG settings](resources/RUMlogNG-settings.png "RUMlogNG settings")

Example DXLab Commander settings 

![Commander settings](resources/DXLab-Commander-settings.png "RUMlogNG settings")

Example SDR++ settings

![SDR++ settings](resources/SDR++-settings.png "SDR++ settings") 


## Dependencies
Cat-relay uses only one 3rd party libraries (pyyaml). To install it, open a terminal, go to the folder that contains cat-relay, 
and run following command:

```pip3 install -r requirements.txt```

## How to run
Open a terminal, go to the folder that contains cat-relay, and run following command:

```python3 listen.py```

Don't close the terminal window, you can minimize it if you'd like to.

## How to quit
Open the terminal window that cat-relay is running in and press Ctrl+C.
