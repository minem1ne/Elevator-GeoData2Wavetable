# Elevator-GeoData2Wavetable
a simple python tool which transforms OpenTopography API Elevation Data to a Wavetable usable in Serum, Vital, Abletons Wavetable etc.


<table>
<tr>
<td width="50%">

![Elevation Plot](pictures/Plot.png)

</td>
<td width="50%">

![Vital Wavetable](pictures/vital.png)

</td>
</tr>
</table>


# Usage  

the simplest way to use this, is to download a prebuild app from the Tag page.

or run the code yourself:

```bash
pip install -r requirements.txt

python elevator_ui.py
```

The Coordinates can easily be copied from google maps in the correct format by right clicking on the map and clicking the coordinates.

![Elevator UI](pictures/UI.png)

# Import Wavetables

## Vital:
Frame Size: 2048 
drag the wav file on the oscillator.
## Ableton Wavetable
Frame Size: 1024
drag the wav file won the wavetable.
activate "Raw" mode (above the wavetable visual)
## Serum
Frame Size: 2048
drag the wav file on the oscillator.
use FFT 2028
## Bitwig
Frame Size 1048

# OpenTopography API

This tool uses the OpenTopography API to get the elevation data. It's accuracy is about 30m.

The API is free for non-commercial use, but you technicaly need an API Key. The tool will function without one and will use a default trial key. If the trial key stops working you can get a free key at https://opentopography.org/ if you click on "MyOpenTopo" and register an account.

# Installation & Build

if you want to build the a standallone app, you can use the following commands:

```bash
# create venv
python3 -m venv venv
source venv/scripts/activate

# install requirements
pip install -r requirements.txt
pip install pyinstaller

# build binary with dependantcies
pyinstaller --onefile --windowed \
  --collect-submodules=rasterio --collect-data=rasterio \
  --collect-submodules=rioxarray --collect-data=rioxarray \
  elevator_ui.py
