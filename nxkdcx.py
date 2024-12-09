import numpy as np
import matplotlib.pyplot as plt

# Parámetros
T = 1.0  # Periodo del símbolo
fs = 1000  # Frecuencia de muestreo
N = int(T * fs)  # Número de muestras
t = np.linspace(0, T, N)  # Vector de tiempo
Es = 1.0  # Energía del símbolo
N0 = 0.1  # Densidad espectral de potencia del ruido
s = np.sqrt(Es / T) * np.ones(N)  # Señal del símbolo

# Ruido blanco gaussiano
n = np.sqrt(N0 / 2) * np.random.randn(N)

# Señal recibida
r = s + n

# Filtro adaptado (matched filter)
h = np.flip(s)
y = np.convolve(r, h, mode='same') / fs

# Cálculo de SNR
snr_input = Es / (N0 / 2)
snr_output = (Es ** 2) / (np.var(y - s) * N0 / 2)

# Gráficos
plt.figure(figsize=(12, 8))

plt.subplot(3, 1, 1)
plt.plot(t, s, label='Señal Original $s(t)$')
plt.title('Señal Original $s(t)$')
plt.xlabel('Tiempo [s]')
plt.ylabel('Amplitud')
plt.grid(True)
plt.legend()

plt.subplot(3, 1, 2)
plt.plot(t, r, label='Señal Recibida $r(t) = s(t) + n(t)$')
plt.title('Señal Recibida $r(t) = s(t) + n(t)$')
plt.xlabel('Tiempo [s]')
plt.ylabel('Amplitud')
plt.grid(True)
plt.legend()

plt.subplot(3, 1, 3)
plt.plot(t, y[:N], label='Salida del Filtro Adaptado $y(T)$')
plt.title('Salida del Filtro Adaptado $y(T)$')
plt.xlabel('Tiempo [s]')
plt.ylabel('Amplitud')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()

print(f'SNR de entrada: {snr_input:.2f}')
print(f'SNR de salida: {snr_output:.2f}')
