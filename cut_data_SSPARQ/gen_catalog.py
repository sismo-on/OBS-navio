from obspy import UTCDateTime
from obspy.clients.fdsn import Client

client = Client("USGS")

#starttime = UTCDateTime("2025-09-25T00:00:00")
#endtime = UTCDateTime("2026-09-03T00:00:00")
starttime = UTCDateTime("2025-07-29T00:00:00")
endtime = UTCDateTime("2025-08-04T00:00:00")
minmag = 6.0

catalog = client.get_events(starttime=starttime, endtime=endtime, minmagnitude=minmag)

catalog.write("NEIC_USGS_2025_2026.xml", format="QUAKEML")
