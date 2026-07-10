from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt


Z0 = 50.0  # NanoVNA reference impedance in ohms


def load_s1p_file(file_path):
    """
    Loads a Touchstone .s1p file in this format:

    # HZ S RI R 50
    frequency_hz real(S11) imag(S11)
    """

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


def analyze_antenna(file_path, plots_dir):
    freq_hz, s11 = load_s1p_file(file_path)

    freq_mhz = freq_hz / 1e6
    gamma_mag = np.abs(s11)

    s11_db = 20 * np.log10(gamma_mag)
    vswr = (1 + gamma_mag) / (1 - gamma_mag)
    impedance = Z0 * (1 + s11) / (1 - s11)

    best_index = np.argmin(s11_db)

    best_freq_mhz = freq_mhz[best_index]
    best_s11_db = s11_db[best_index]
    best_vswr = vswr[best_index]
    best_impedance = impedance[best_index]

    good_match = vswr < 2.0

    if np.any(good_match):
        low_freq = freq_mhz[good_match][0]
        high_freq = freq_mhz[good_match][-1]
        bandwidth = high_freq - low_freq
    else:
        low_freq = None
        high_freq = None
        bandwidth = None

    file_stem = Path(file_path).stem

    print()
    print("NanoVNA Antenna Characterization Report")
    print("--------------------------------------")
    print(f"File: {file_path}")
    print(f"Best match frequency: {best_freq_mhz:.3f} MHz")
    print(f"Best S11: {best_s11_db:.2f} dB")
    print(f"Minimum VSWR: {best_vswr:.3f}")
    print(
        f"Impedance at best match: "
        f"{best_impedance.real:.2f} "
        f"{'+' if best_impedance.imag >= 0 else '-'} "
        f"j{abs(best_impedance.imag):.2f} ohms"
    )

    if bandwidth is not None:
        print(f"VSWR < 2 range: {low_freq:.3f} MHz to {high_freq:.3f} MHz")
        print(f"VSWR < 2 bandwidth: {bandwidth:.3f} MHz")
    else:
        print("No VSWR < 2 region found.")

    # Save text report
    report_path = plots_dir / f"{file_stem}_report.txt"

    with open(report_path, "w") as report:
        report.write("NanoVNA Antenna Characterization Report\n")
        report.write("--------------------------------------\n")
        report.write(f"File: {file_path}\n")
        report.write(f"Best match frequency: {best_freq_mhz:.3f} MHz\n")
        report.write(f"Best S11: {best_s11_db:.2f} dB\n")
        report.write(f"Minimum VSWR: {best_vswr:.3f}\n")
        report.write(
            f"Impedance at best match: "
            f"{best_impedance.real:.2f} "
            f"{'+' if best_impedance.imag >= 0 else '-'} "
            f"j{abs(best_impedance.imag):.2f} ohms\n"
        )

        if bandwidth is not None:
            report.write(f"VSWR < 2 range: {low_freq:.3f} MHz to {high_freq:.3f} MHz\n")
            report.write(f"VSWR < 2 bandwidth: {bandwidth:.3f} MHz\n")
        else:
            report.write("No VSWR < 2 region found.\n")

    print(f"Saved report to: {report_path}")

    # Save S11 plot
    plt.figure()
    plt.plot(freq_mhz, s11_db)
    plt.axhline(-10, linestyle="--", label="-10 dB target")
    plt.scatter(best_freq_mhz, best_s11_db)
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("S11 (dB)")
    plt.title(f"S11 vs Frequency: {file_stem}")
    plt.grid(True)
    plt.legend()
    plt.savefig(plots_dir / f"{file_stem}_s11.png", dpi=300)
    plt.close()

    # Save VSWR plot
    plt.figure()
    plt.plot(freq_mhz, vswr)
    plt.axhline(2, linestyle="--", label="VSWR = 2 target")
    plt.scatter(best_freq_mhz, best_vswr)
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("VSWR")
    plt.title(f"VSWR vs Frequency: {file_stem}")
    plt.grid(True)
    plt.legend()
    plt.savefig(plots_dir / f"{file_stem}_vswr.png", dpi=300)
    plt.close()

    return {
        "file": file_stem,
        "best_freq_mhz": best_freq_mhz,
        "best_s11_db": best_s11_db,
        "best_vswr": best_vswr,
        "best_impedance": best_impedance,
        "bandwidth_mhz": bandwidth,
    }


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / "data"
    plots_dir = project_root / "plots"

    plots_dir.mkdir(exist_ok=True)

    s1p_files = sorted(data_dir.glob("*.s1p"))

    if not s1p_files:
        print("No .s1p files found in the data folder.")
    else:
        print(f"Found {len(s1p_files)} .s1p file(s).")

        results = []

        for s1p_file in s1p_files:
            result = analyze_antenna(s1p_file, plots_dir)
            results.append(result)

        print()
        print("Summary Table")
        print("-------------")
        print("File | Best Freq MHz | Best S11 dB | Min VSWR | Bandwidth MHz")
        print("-----|---------------|-------------|----------|--------------")

        for result in results:
            bandwidth_text = (
                f"{result['bandwidth_mhz']:.3f}"
                if result["bandwidth_mhz"] is not None
                else "N/A"
            )

            print(
                f"{result['file']} | "
                f"{result['best_freq_mhz']:.3f} | "
                f"{result['best_s11_db']:.2f} | "
                f"{result['best_vswr']:.3f} | "
                f"{bandwidth_text}"
            )
