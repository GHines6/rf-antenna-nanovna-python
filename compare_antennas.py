from pathlib import Path
import csv

import numpy as np
import matplotlib.pyplot as plt


Z0 = 50.0


def load_s1p_file(file_path):
    frequencies_hz = []
    s11_values = []

    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#") or line.startswith("!"):
                continue

            parts = line.split()

            if len(parts) < 3:
                continue

            frequency_hz = float(parts[0])
            s11_real = float(parts[1])
            s11_imag = float(parts[2])

            frequencies_hz.append(frequency_hz)
            s11_values.append(complex(s11_real, s11_imag))

    return np.array(frequencies_hz), np.array(s11_values)


def analyze_file(file_path):
    freq_hz, s11 = load_s1p_file(file_path)

    freq_mhz = freq_hz / 1e6
    gamma_mag = np.abs(s11)

    s11_db = 20 * np.log10(gamma_mag)
    vswr = (1 + gamma_mag) / (1 - gamma_mag)
    impedance = Z0 * (1 + s11) / (1 - s11)

    best_index = np.argmin(s11_db)

    good_match = vswr < 2.0

    if np.any(good_match):
        low_freq = freq_mhz[good_match][0]
        high_freq = freq_mhz[good_match][-1]
        bandwidth = high_freq - low_freq
    else:
        low_freq = None
        high_freq = None
        bandwidth = None

    return {
        "name": file_path.stem,
        "freq_mhz": freq_mhz,
        "s11_db": s11_db,
        "vswr": vswr,
        "best_freq_mhz": freq_mhz[best_index],
        "best_s11_db": s11_db[best_index],
        "best_vswr": vswr[best_index],
        "best_impedance": impedance[best_index],
        "bandwidth_mhz": bandwidth,
        "low_freq_mhz": low_freq,
        "high_freq_mhz": high_freq,
    }


def main():
    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / "data"
    plots_dir = project_root / "plots"

    plots_dir.mkdir(exist_ok=True)

    s1p_files = sorted(data_dir.glob("*.s1p"))

    if len(s1p_files) < 2:
        print("Need at least two .s1p files in the data folder.")
        return

    results = [analyze_file(file_path) for file_path in s1p_files]

    # Comparison S11 plot
    plt.figure()

    for result in results:
        plt.plot(result["freq_mhz"], result["s11_db"], label=result["name"])
        plt.scatter(result["best_freq_mhz"], result["best_s11_db"])

    plt.axhline(-10, linestyle="--", label="-10 dB target")
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("S11 (dB)")
    plt.title("S11 Comparison Across Antenna Measurements")
    plt.grid(True)
    plt.legend()
    plt.savefig(plots_dir / "comparison_s11.png", dpi=300)
    plt.close()

    # Comparison VSWR plot
    plt.figure()

    for result in results:
        plt.plot(result["freq_mhz"], result["vswr"], label=result["name"])
        plt.scatter(result["best_freq_mhz"], result["best_vswr"])

    plt.axhline(2, linestyle="--", label="VSWR = 2 target")
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("VSWR")
    plt.title("VSWR Comparison Across Antenna Measurements")
    plt.grid(True)
    plt.legend()
    plt.savefig(plots_dir / "comparison_vswr.png", dpi=300)
    plt.close()

    # Save summary CSV
    csv_path = plots_dir / "comparison_summary.csv"

    with open(csv_path, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)

        writer.writerow([
            "measurement",
            "best_frequency_mhz",
            "best_s11_db",
            "minimum_vswr",
            "impedance_real_ohms",
            "impedance_imag_ohms",
            "vswr_lt_2_bandwidth_mhz",
        ])

        for result in results:
            z = result["best_impedance"]

            writer.writerow([
                result["name"],
                f"{result['best_freq_mhz']:.3f}",
                f"{result['best_s11_db']:.2f}",
                f"{result['best_vswr']:.3f}",
                f"{z.real:.2f}",
                f"{z.imag:.2f}",
                f"{result['bandwidth_mhz']:.3f}" if result["bandwidth_mhz"] is not None else "N/A",
            ])

    print("Comparison complete.")
    print(f"Saved: {plots_dir / 'comparison_s11.png'}")
    print(f"Saved: {plots_dir / 'comparison_vswr.png'}")
    print(f"Saved: {csv_path}")

    print()
    print("Summary")
    print("-------")

    for result in results:
        z = result["best_impedance"]

        print(
            f"{result['name']}: "
            f"{result['best_freq_mhz']:.3f} MHz, "
            f"S11 = {result['best_s11_db']:.2f} dB, "
            f"VSWR = {result['best_vswr']:.3f}, "
            f"Z = {z.real:.2f} {'+' if z.imag >= 0 else '-'} j{abs(z.imag):.2f} ohms"
        )


if __name__ == "__main__":
    main()