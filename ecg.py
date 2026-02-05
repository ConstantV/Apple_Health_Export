import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

FILE = "ecg_2022-08-11.csv"
FS = 512  # Hz

raw = pd.read_csv(FILE, dtype=str)

# Pak rijen waar kolom 1 (Name) numeriek is -> echte samples
v = pd.to_numeric(raw.iloc[:, 0], errors="coerce").dropna().astype(float).to_numpy()

# Zet om van µV naar mV (optioneel maar fijn)
v_mv = v / 1000.0

# Bandpass filter (ECG)
low, high = 0.5, 40.0
b, a = butter(3, [low/(FS/2), high/(FS/2)], btype="bandpass")
vf = filtfilt(b, a, v_mv)

t = np.arange(len(vf)) / FS

# Zoom: 6 seconden is goed leesbaar
start_s = 3
window_s = 5
i0 = int(start_s * FS)
i1 = int((start_s + window_s) * FS)

plt.figure(figsize=(14, 4))
plt.plot(t[i0:i1], vf[i0:i1], linewidth=1.0)
plt.xlabel("Time (s)")
plt.ylabel("ECG (mV)")
plt.title("Apple Watch ECG (filtered 0.5–40 Hz, zoom)")
plt.grid(True, linewidth=0.3, alpha=0.6)
plt.tight_layout()
plt.show()
