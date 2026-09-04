import pandas as pd
from obspy import read, read_events, UTCDateTime, read_inventory
from obspy.geodetics import gps2dist_azimuth, kilometers2degrees
from obspy.taup import TauPyModel
import os
from glob import glob

def quakeml_to_dataframe(quakeml_file):
    # Read the QuakeML file using ObsPy
    catalog = read_events(quakeml_file)

    entries = []

    for event in catalog:
        # Extract basic event information
        origin = event.preferred_origin() or event.origins[0]
        magnitude = event.preferred_magnitude() or event.magnitudes[0]

        if event.focal_mechanisms:
            fm = event.focal_mechanisms[0]
            if fm.moment_tensor:
                mt = fm.moment_tensor.tensor
                moment_tensor = [
                    mt.m_rr,
                    mt.m_tt,
                    -mt.m_pp,  # Mff = -Mpp
                    mt.m_rt,
                    -mt.m_rp,  # Mrf = -Mrp
                    -mt.m_tp   # Mtf = -Mtp
                ]

            # Append event data to entries list
            entries.append({
                'time': origin.time.datetime,
                'latitude': origin.latitude,
                'longitude': origin.longitude,
                'depth': origin.depth / 1000,  # Convert from m to km
                'mag': magnitude.mag,
                'magType': magnitude.magnitude_type,
                'moment tensor': moment_tensor})
        else:
            # Append event data to entries list
            entries.append({
                'time': origin.time.datetime,
                'latitude': origin.latitude,
                'longitude': origin.longitude,
                'depth': origin.depth / 1000,  # Convert from m to km
                'mag': magnitude.mag,
                'magType': magnitude.magnitude_type})

    # Convert to DataFrame
    df = pd.DataFrame(entries)
    return df

def mkdir(folder):
    if not os.path.isdir(folder):
        os.mkdir(folder)

def trim_event(args):
    window_len = 150

    event, inv, data_path = args
    #stla, stlo = inv[0][0].latitude, inv[0][0].longitude
    stla, stlo = -22.8968, -43.2246 # trocar  isso depois
    evla, evlo, evdp = event.latitude, event.longitude, event.depth

    date = str(event.time.date())

    files = glob("%s/%s*"%(data_path, date))
    if len(files) == 0:
        return

    ot = UTCDateTime(str(event.time))

    dist, _, _ = gps2dist_azimuth(evla, evlo, stla, stlo)
    gcarc = kilometers2degrees(dist/1000)

    if 100 < gcarc < 140:
        return

    model = TauPyModel(model="iasp91")
    arrivals = model.get_travel_times(source_depth_in_km=evdp, distance_in_degree=gcarc, phase_list=["P", "PKP", "PKIKP"])

    if len(arrivals) == 0:
        return

    P_time = ot + arrivals[0].time
    win_min = P_time - window_len
    win_max = P_time + window_len
    year = ot.strftime("%Y")
    julday = ot.strftime("%j")
    hour = ot.strftime("%H")
    minute = ot.strftime("%M")
    second = ot.strftime("%S")

    for file in files:
        st = read(file)
        net = st[0].stats.network
        sta = st[0].stats.station
        cha = st[0].stats.channel
        if win_max.strftime("%j") > P_time.strftime("%j"):
            try:
                next_day = (ot+86400).date
                file2 = glob("%s/%s*%s*"%(data_path, str(next_day), cha))[0]
                st += read(file2)
                st.merge()
            except:
                pass

        st.trim(starttime=win_min, endtime=win_max)
        st.write("MSEED/%s.%s..%s.%s.%s.%s.%s.%s"%(net, sta, cha, year, julday, hour, minute, second), format="MSEED")
        print("Saved %s.%s..%s.%s.%s.%s.%s.%s"%(net, sta, cha, year, julday, hour, minute, second))


if __name__ == "__main__":
    df = quakeml_to_dataframe("NEIC_USGS_2025_2026.xml")
    mkdir("MSEED")
    data_path = "/home/andre/Documents/pos_doc/codes/OBS-navio/data/6G/IPAN"
    inv = read_inventory("/home/andre/Documents/pos_doc/codes/OBS-navio/data/6G/BM.IPAN.Z.dataless")

    inputs = []

    for event in df.itertuples(index=False):
        inputs.append([event, inv, data_path])

    for inp in inputs:
        trim_event(inp)
