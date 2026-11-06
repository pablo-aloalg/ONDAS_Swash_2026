import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def plot_case_config(x, z, wave_height, wave_period, WL, save_path=None):

    g = 9.81  # gravity m/s^2
    L = g * wave_period**2 / (2 * np.pi)  # deep water wavelength

    fig, ax = plt.subplots(figsize=(10,5))

    # Water surface line: wave for first cycle, constant afterwards
    wave = np.full_like(x, WL)  # start with constant WL
    mask = x <= x[0] + L        # only modify the first wavelength
    wave[mask] = WL + (wave_height/2) * np.sin(2 * np.pi / L * (x[mask] - x[0]))

    # Fill water area below profile
    ax.fill_between(x, wave, np.min(z)-1, color='lightblue', alpha=0.3)
    
    # Plot the water line with wave
    ax.plot(x, wave, color='blue', lw=2, label='Water Level')

    # Plot profile
    ax.plot(x, z, color='black', lw=2, label='Profile')
    ax.fill_between(x, z, np.min(z)-1, color='yellow', alpha=0.5)

    # Horizontal dashed zero line
    ax.axhline(0, color='gray', linestyle='--', lw=1)

    # Labels and grid
    ax.set_xlabel('Distance (m)')
    ax.set_ylabel('Depth / Height (m)')
    ax.set_title('Case_Configuration')

    ax.legend()
    ax.set_xlim(x[0], x[-1])

    textstr = f"Hs = {wave_height:.2f} m\nWL = {WL:.2f} m\nTp = {wave_period:.2f} s"
    ax.text(
        0.02, 0.95, textstr, transform=ax.transAxes, fontsize=12,
        verticalalignment='top', bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7)
    )

    if save_path is not None:
        # Save figure to PNG and close
        plt.savefig(save_path, dpi=300)
        plt.close(fig)
    else:
        # Show the plot interactively
        plt.show()

    plt.show()

