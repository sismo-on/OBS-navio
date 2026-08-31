from obspy import read, read_inventory
from obspy.signal import PPSD
import numpy as np
import matplotlib.pyplot as plt
from obspy.signal.spectral_estimation import get_nhnm, get_nlnm

network = "BM"
station = "IPAN"
channel = "Z"

path_to_inv = "/home/andre/Documents/pos_doc/codes/OBS-navio/data/BM/BM.IPAN.Z.dataless"
inv = read_inventory(path_to_inv)

NOISE_MODEL_FILE = "noise_models.npz"
noise_max = get_nhnm()
noise_min = get_nlnm()

months = ["2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09"]
fig, axes = plt.subplots(3, 4, figsize=(25, 14))
labels = ["Oct/2025", "Nov/2025", "Dec/2025", "Jan/2026", "Feb/2026", "Mar/2026", "Apr/2026", "May/2026", "Jun/2026", "Jul/2026", "Aug/2026", "Sep/2026"]

for n, month in enumerate(months):
    ax = axes[n//4, n%4]
    path_to_data = "/home/andre/Documents/pos_doc/codes/OBS-navio/data/%s/%s/*%s*%s*"%(network, station, month, channel)
    try:
        st = read(path_to_data)
    except:
        continue
    tr = st[0]

    ppsd = PPSD(tr.stats, metadata=inv)

    for i in range(len(st)):
        ppsd.add(st[i])

    ppsd.calculate_histogram()
    data = ppsd.current_histogram
    xedges = ppsd.period_xedges
    yedges = ppsd.db_bin_edges

    X, Y = np.meshgrid(xedges, yedges)
    im = ax.pcolormesh(
        X,
        Y,
        data.T,
        cmap="viridis",
        shading="auto"
    )

    ax.set_xscale("log")
    ax.grid(True, which="both", alpha=0.3)
    ax.set_xlim([0.01, 120])

    ax.set_ylabel("Amplitude [$m^2/s^4/Hz$] [dB]")
    ax.set_xlabel("Period [s]")

    ax.set_title(labels[n])

    ax.plot(noise_max[0], noise_max[1], '0.4', linewidth=2)
    ax.plot(noise_min[0], noise_min[1], '0.4', linewidth=2)

plt.suptitle("%s.%s.%s"%(network, station, channel))
plt.tight_layout()
plt.show()
