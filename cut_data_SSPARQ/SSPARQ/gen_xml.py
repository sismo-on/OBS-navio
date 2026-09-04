from obspy.clients.fdsn import Client
import os

stations = os.listdir("MSEED")

client = Client("RSBR")

if not os.path.isdir("XML"):
    os.mkdir("XML")

for station in stations:
    net, sta = station.split(".")
    inv = client.get_stations(network=net, station=sta, channel="*", location="*", level="response")
    inv.write("XML/%s.xml"%station, format="STATIONXML")
    print("Saved XML file for %s."%station)
