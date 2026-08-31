import pandas as pd
from obspy import read_inventory, UTCDateTime
from obspy.core.inventory import Inventory, Network, Station, Channel

df = pd.read_csv("OBS_tri.csv")
inv_ref = read_inventory("6D7-Trillium-100sps.resp")
resp = inv_ref.get_response("XX.ST001..BHZ", UTCDateTime("2016-01-01T00:00:00"))

inv_hydro = read_inventory("6D7-HTI-04-PCA-ULF-100sps.resp")
resp_hydro = inv_hydro.get_response("XX.ST001..BDH", UTCDateTime("2016-01-01T00:00:00"))

for obs in df["name"].values:
    print(obs)
    stla = df[df["name"] == obs].lat.values[0]
    stlo = df[df["name"] == obs].lon.values[0]
    stel = 0 # assigning to zero for now, must fix latter

    inv = Inventory(networks=[], source="ON")
    net = Network(stations=[], code="BM", description="OBS from RSBR-Mar proj", start_date=UTCDateTime("2025-09-25T00:00:00"))
    sta = Station(code=obs, latitude=stla, longitude=stlo, elevation=stel, creation_date=UTCDateTime())
    
    cha_Z = Channel(code="Z", latitude=stla, longitude=stlo, elevation=stel, depth=0, azimuth=0.0, dip=-90.0, location_code="", sample_rate=100)
    cha_X = Channel(code="X", latitude=stla, longitude=stlo, elevation=stel, depth=0, location_code="", sample_rate=100)
    cha_Y = Channel(code="Y", latitude=stla, longitude=stlo, elevation=stel, depth=0, location_code="", sample_rate=100)
    cha_H = Channel(code="H", latitude=stla, longitude=stlo, elevation=stel, depth=0, location_code="", sample_rate=100)
    
    cha_Z.response = resp
    cha_X.response = resp
    cha_Y.response = resp
    cha_H.response = resp_hydro
    sta.channels.append(cha_Z)
    sta.channels.append(cha_X)
    sta.channels.append(cha_Y)
    sta.channels.append(cha_H)
    net.stations.append(sta)
    inv.networks.append(net)
    
    inv.write("BM.%s.xml"%obs, format="STATIONXML")
