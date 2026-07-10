# RF Antenna Design & Characterization — NanoVNA + Python

This project documents the design, construction, measurement, and analysis of simple RF antennas using a NanoVNA-H and Python.

The goal was to build practical antenna test setups, measure their impedance behavior, and analyze exported Touchstone `.s1p` data to determine resonance, return loss, VSWR, complex impedance, and usable bandwidth.

---

## Project Overview

I built and tested custom RF antennas using SMA connectors and solid-core wire, including:

- A two-wire dipole-style antenna
- A quarter-wave monopole-style antenna
- Soldered SMA test fixtures for NanoVNA measurement

Measurements were taken using a calibrated NanoVNA-H. Data was exported using NanoVNA-Saver as Touchstone `.s1p` files and analyzed with Python.

---

## Skills Demonstrated

- RF measurement using a NanoVNA-H
- S11 / return loss interpretation
- VSWR calculation
- Complex impedance analysis
- Smith chart interpretation
- Antenna resonance and tuning
- Touchstone `.s1p` data parsing
- Python-based RF data analysis
- Soldering SMA connectors and antenna test fixtures

---

## Hardware Used

- NanoVNA-H
- SMA cables and adapters
- SMA PCB connectors
- Solid-core wire antenna elements
- Soldering iron and solder
- Computer running NanoVNA-Saver

---

## Measurement Process

1. Calibrated the NanoVNA-H using open, short, and load standards.
2. Connected the antenna under test to Port 1.
3. Swept the target RF frequency range.
4. Measured:
   - S11
   - Return loss
   - VSWR
   - Complex impedance
5. Exported Touchstone `.s1p` files.
6. Parsed and analyzed the data using Python.

---

## Example Results

| Antenna/Test Setup | Best Match Frequency | S11 / Return Loss | VSWR | Impedance |
|---|---:|---:|---:|---:|
| Dipole-style baseline | 495.000 MHz | -28.97 dB | 1.074 | 53.07 - j2.01 Ω |
| Quarter-wave antenna | 735.000 MHz | ≈ -17.18 dB | ≈ 1.321 | TBD |

The dipole-style antenna produced a strong impedance match near 50 Ω, while the quarter-wave antenna showed a usable but less ideal match.

---

## RF Concepts

### S11 / Return Loss

S11 describes how much power is reflected back from the antenna due to impedance mismatch.

A more negative S11 value means less reflected power and better power transfer into the antenna.

Example:

- `S11 = -10 dB` means about 10% of power is reflected.
- `S11 = -20 dB` means about 1% of power is reflected.
- `S11 = -30 dB` means about 0.1% of power is reflected.

### VSWR

VSWR, or Voltage Standing Wave Ratio, is another way to describe impedance match.

Lower VSWR is better.

Common antenna guideline:

- `VSWR < 2:1` is usually considered usable.
- `VSWR ≈ 1:1` is ideal.

### Impedance

Most RF test equipment, including the NanoVNA-H, is designed around a 50 Ω system.

A good antenna match occurs when the antenna impedance is close to:

```text
50 + j0 Ω
