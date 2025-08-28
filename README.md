## Elevator-GeoData2Wavetable
a simple python tool which transforms OpenTopography API Elevation Data to a Wavetable usable in Serum, Vital, Abletons Wavetable etc.


## Installation & Build

```bash
# create venv
python3 -m venv venv
source venv/bin/activate

# install requirements
pip install -r requirements.txt
pip install pyinstaller

# build binary with dependantcies
pyinstaller --onefile --windowed \
  --collect-submodules=rasterio --collect-data=rasterio \
  --collect-submodules=rioxarray --collect-data=rioxarray \
  ui_app.py
