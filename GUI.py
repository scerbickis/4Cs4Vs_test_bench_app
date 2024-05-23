import tkinter as tk
import serial
import logging
import struct
import matplotlib.pyplot as plt
import numpy as np
import itertools
from serial.tools import list_ports
from math import sqrt, hypot, atan2
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def round_half_up(float_number: float, precision: int = 0) -> float:

    factor = 10.0 ** precision
    if float_number >= 0:
        return int(float_number * factor + 0.5) / factor
    else:
        return int(float_number * factor - 0.5) / factor

def update_signal():

    if "harmonic_spinbox" not in globals() or\
        "signal_plots_U" not in globals(): 
            return

    signals_U = itertools.islice(signals.values(), 4)

    for signal_plot, signal_U in zip(signal_plots_U, signals_U):
        signal_plot.set_ydata(signal_U)

    canvas_signals.draw()

def plot_time_graph(frame: tk.Frame, row: int, column: int):

    global signal_plots_U, canvas_signals

    signal_plots_U = []

    # Create a figure and a subplot
    fig, ax = plt.subplots()
    fig.set_size_inches(6, 4)
    ax.set_ylim(-10, 10)
    ax.set_ylabel("Amplitude (V Pk-Pk)")
    ax.set_xlabel("Time (ms)")
    ax.grid(linewidth=0.5, color='lightgray', linestyle='--')
    ax.axhline(0, color='black', linewidth=0.5)  # Add x-axis

    signals_U = itertools.islice(signals.values(), 4)

    loop_params = zip(signals_U, colors, lines)

    for signal_U, color, line_name in loop_params:

        signal_plot, = ax.plot(t, signal_U, label = f"{line_name}", color=color)
        signal_plots_U.append(signal_plot)

    ax.legend(loc = "upper right", bbox_to_anchor=(1, 1), prop={'size': 7})

    child_window = tk.Toplevel(frame)
    child_window.title("U(t) Graph")
    
    canvas_signals = FigureCanvasTkAgg(fig, master=child_window)
    
    canvas_signals.draw()

    canvas_widget = canvas_signals.get_tk_widget()
    canvas_widget.grid(
        row=row, 
        column=column, 
        columnspan=5, 
        sticky="W",
        padx=10,
        pady=10
    )

def update_phasor():

    if not "phasors" in globals(): return

    angle_U = itertools.islice(phase_angle.values(), 3)

    angles_rad = [ np.pi * p / 180 for p in angle_U ]

    loop_params = zip(phasors, angles_rad, amplitude.values())

    aN = bN = 0

    for phasor, angle, magnitude in loop_params:

        phasor.set_UVC(
            angle, 
            magnitude
        )

        aN += magnitude * np.cos(angle)
        bN += magnitude * np.sin(angle)

    phasorN.set_UVC(
        atan2(bN, aN), # U
        hypot(aN, bN) , # V
    )


    canvas_phasors.draw_idle()

def plot_phasors(frame: tk.Frame, row: int, column: int):

    global phasors, canvas_phasors
    global phasorN

    phasors = []

    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.set_ylim(0, 10)
    # ax.set_rticks([i for i in range(0, 401, 100)])
    ax.set_xticks(np.linspace(0, 2*np.pi, 12, endpoint=False))
    ax.grid(linewidth=0.5, color='lightgray', linestyle='--')

    amplitude_U = itertools.islice(amplitude.values(), 3)
    angle_U = itertools.islice(phase_angle.values(), 3)

    angles_rad = [ np.pi * p / 180 for p in angle_U ]

    loop_params = zip(angles_rad, amplitude_U, colors)

    aN = bN = 0

    for angle, magnitude, color in loop_params:

        phasor = ax.quiver(
            0, # X
            0, # Y
            angle, # U
            magnitude , # V
            angles='xy', 
            scale_units='xy', 
            scale=1, 
            color=color,
            zorder=3
        )
        
        phasors.append(phasor)

        aN += magnitude * np.cos(angle)
        bN += magnitude * np.sin(angle)

    phasorN = ax.quiver(
            0, # X
            0, # Y
            atan2(bN, aN), # U
            hypot(aN, bN) , # V
            angles='xy', 
            scale_units='xy', 
            scale=1, 
            color=colors[-1],
            zorder = 3
        )

    child_window = tk.Toplevel(frame)
    child_window.title("Phasor Graph (U)")

    canvas_phasors = FigureCanvasTkAgg(fig, master=child_window)

    canvas_phasors.draw()

    canvas_widget = canvas_phasors.get_tk_widget()

    canvas_widget.grid(
        row=row, 
        column=column, 
        columnspan=5, 
        sticky="W",
        padx=10,
        pady=10
    )
    child_window.columnconfigure(0, weight=1)
    
def calculate_signals():

    global signals, t

    t = np.linspace(0, 20, 10000, endpoint=False)

    frequencies = [ *list(frequency.values()), 0, *list(frequency.values()), 0]

    signals = {
        "u1": [],
        "u2": [],
        "u3": [],
        "uN": [],
        "i1": [],
        "i2": [],
        "i3": [],
        "iN": []
    }

    loop_params = zip(amplitude.values(), frequencies, phase_angle.values(), signals.keys())

    yN = np.zeros_like(t)

    # Add harmonics if specified

    try: 
        step = int(harmonic_spinbox.configure('increment')[4])
        first_harmonic = int(harmonic_spinbox.configure('from')[4])
        harmonics_order = int(harmonic_spinbox.get())
    except:
        step = 1
        first_harmonic = 1
        harmonics_order = 1

    for a, f, ph, signal_key in loop_params:

        if signal_key == "uN" or signal_key == "iN":
            signals[signal_key] = yN
            yN = np.zeros_like(t)
            continue

        y = 0

        for h in range(first_harmonic, harmonics_order + 1, step):
            
            if harmonics_type_var.get() == "Non-Triplen Odd" and h % 3 == 0: continue
            y += a / h * np.sin(h * (2 * np.pi *  f / 1000  * t + ph * np.pi / 180))
        
        signals[signal_key] = y
        yN += y



def select_comport(comport):

    logging.info(f"Selected Serial port: {comport}")
    global selected_comport
    selected_comport = comport
    connect()

def connect():

    if "selected_comport" in globals():
        try:
            global ser
            ser = serial.Serial(selected_comport, baudrate=115200)
            logging.info(f"Connected to {selected_comport}")
        except serial.SerialException as e:
            logging.error(f"Could not connect to {selected_comport}: {e}")
    else:
        logging.error("No COM port selected")

def menu(root: tk.Tk):

    menubar = tk.Menu(root)
    comport_menu = tk.Menu(menubar, tearoff=0)
    comports = list_ports.comports()

    for comport in comports:
        comport_menu.add_command(
            label=comport.device, 
            command=lambda c=comport.device: select_comport(c)
        )

    graphs_menu = tk.Menu(menubar, tearoff=0)
    graphs_menu.add_command(
        label="U(t)", 
        command=lambda: plot_time_graph(frame_signal_plot, row=0, column=0)
    )
    graphs_menu.add_command(
        label="I(t)"
    )
    graphs_menu.add_command(
        label="Phasors",
        command=lambda: plot_phasors(frame_phasor_plot, row=0, column=0)
    )

    menubar.add_cascade(label="Connect to Test Bench", menu=comport_menu)
    menubar.add_cascade(label="Graphs", menu=graphs_menu)


    root.config(menu=menubar)


def update(value: str, parameter_id: int, type: str, phase_id: int, type_changed = False):

    packet = bytes([0x53, parameter_id])
    if parameter_id != 0x48:
        packet += bytes([phase_id])
    
    if type == "U":
        packet += bytes([0x55]) # ASCII code for 'U'
        units = "V"
    elif type == "I":
        packet += bytes([0x49]) # ASCII code for 'I'
        units = "A"
    
    signal_id = f"{type.casefold()}{phase_id}"

    match parameter_id:
        # 0x41 is the ASCII code for 'A' (A - amplitude)
        case 0x41:
            amplitude[signal_id] = int(value)
            update_rms_values()

            if type == "U":
                DAC_rms = rms_values[signal_id] / voltage_sensor_coefficient
                DAC_amplitude = amplitude[signal_id] / voltage_sensor_coefficient
            elif type == "I":
                DAC_rms = rms_values[signal_id] / current_sensor_coefficient
                DAC_amplitude = amplitude[signal_id] / current_sensor_coefficient

            packet += int(round_half_up(DAC_amplitude * 6553.5 )).to_bytes(2)    
            logging.info(
                f"Packet: {packet.hex('|')} - "
                f"DAC Amplitude: {round_half_up(DAC_amplitude, 3)} {units} - "
                f"DAC RMS: {round_half_up(DAC_rms, 3)} {units}"
            )

        # 0x46 is the ASCII code for 'F' (F - frequency)
        case 0x46:
            frequency[phase_id] = int(value)
            update_rms_values()
            packet += int(round_half_up(float(value) * 5.32)).to_bytes(2)
            logging.info(
                f"Packet: {packet.hex('|')} "
                f"- Frequency: {value} Hz"
            )
        # 0x50 is the ASCII code for 'P' (P - phase)
        case 0x50:
            phase_angle[signal_id] = int(value)
            update_rms_values()
            packet += phase_angle[signal_id].to_bytes(2)
            logging.info(
                f"Packet: {packet.hex('|')} "
                f"- Phase: {value}°"
            )
        # 0x48 is the ASCII code for 'H' (H - harmonics)
        case 0x48:

            harmonics_order = int(value)

            match harmonics_type_var.get():
                # 0x42 is the ASCII code for 'B' (B - bez)
                case "None": 

                    harmonics_order_var.set(1)
                    harmonics_order = 1
                    harmonic_spinbox.configure(
                        from_ = 1,
                        to = 50,
                        increment = 1,
                        state = "disabled",
                        cursor = "arrow"
                    )
                    
                    packet += bytes([0x42])

                # 0x41 is the ASCII code for 'A' (A - all)
                case "All": 

                    harmonic_spinbox.configure(
                        from_ = 1,
                        to = 50,
                        increment = 1,
                        state = "normal"
                    )

                    packet += bytes([0x41])

                # 0x45 is the ASCII code for 'E'
                case "Even": 

                    harmonic_spinbox.configure(
                        from_=2,
                        to = 50,
                        increment=2,
                        state = "normal"
                    )

                    packet += bytes([0x45])

                # 0x4F is the ASCII code for 'O'
                case "Odd": 

                    harmonic_spinbox.configure(
                        from_ = 1,
                        to = 49,
                        increment = 2,
                        state = "normal"
                    )

                    packet += bytes([0x4F])

                # 0x54 is the ASCII code for 'T'
                case "Triplen": 
                    
                    harmonic_spinbox.configure(
                        from_ = 3,
                        to = 45,
                        increment = 6,
                        state = "normal"
                    )

                    packet += bytes([0x54])

                # 0x52 is the ASCII code for 'R'
                case "Non-Triplen Odd": 
                    
                    harmonic_spinbox.configure(
                        from_ = 1,
                        to = 49,
                        increment = 2,
                        state = "normal"
                    )

                    if harmonics_order % 3 == 0: 
                        harmonics_order += 2
                        harmonics_order_var.set(harmonics_order)
                    
                    
                    packet += bytes([0x52])

                # 0x50 is the ASCII code for 'P'
                case "Positive Sequence": 
                    
                    harmonic_spinbox.configure(
                        from_ = 1,
                        to = 49,
                        increment = 3,
                        state = "normal"
                    )
                    
                    packet += bytes([0x50])

                # 0x4E is the ASCII code for 'N'
                case "Negative Sequence": 
                    
                    harmonic_spinbox.configure(
                        from_ = 2,
                        to = 50,
                        increment = 3,
                        state = "normal"
                    )

                    packet += bytes([0x4E])

                # 0x5A is the ASCII code for 'Z'
                case "Zero Sequence": 
                    
                    harmonic_spinbox.configure(
                        from_ = 3,
                        to = 48,
                        increment = 3,
                        state = "normal"
                    )

                    packet += bytes([0x5A])

            if type_changed: 
                harmonics_order_var.set(int(harmonic_spinbox.configure('from')[4]))   
                harmonics_order = int(harmonics_order_var.get())  

            update_rms_values()
            packet += harmonics_order.to_bytes(1)
            logging.info(
                f"Packet: {packet.hex('|')} "
                f"- Harmonics: {harmonics_order}"
            )
    
    update_signal()
    update_phasor()

    # Send the command to the Arduino
    if "ser" in globals(): ser.write(packet)



def parameter_controls(
    frame: tk.Frame,
    row: int,
    column: int,
    update_function: callable,
    unit: str,
    min_value: int,
    max_value: int,
    resolution: float|int,
    default_value: int|float,
    parameter_id: int,
    type = "B",
    phase_id = 1
):
    
    def update_spinbox(*args):
        try:
            new_value = parameter_var.get()
            if new_value > max_value: new_value = max_value
            elif new_value < min_value: new_value = min_value
            parameter_var.set(new_value)
            update_function(new_value, parameter_id, type, phase_id)
        except ValueError as e:
            logging.error(e)
    
    control_variables = {}

    if isinstance(default_value, int):
        parameter_var = tk.IntVar(value=default_value)
    elif isinstance(default_value, float):
        parameter_var = tk.DoubleVar(value=default_value) 

    control_variables["var"] = parameter_var

    parameter_spinbox = tk.Spinbox(
        frame,
        from_=min_value,
        to=max_value,
        increment=resolution,
        width=7,
        textvariable=parameter_var,
        command=lambda *args: update_spinbox(
            parameter_var.get(),
            parameter_id,
            type,
            phase_id
        )
    )
    parameter_spinbox.grid(
        row=row, 
        column=column, 
    )

    control_variables["spinbox"] = parameter_spinbox

    units_label = tk.Label(frame, text=unit)
    units_label.grid(
        row = row, 
        column = column + 1, 
        padx= (0, 20),
        sticky = "W",
        pady=5
    )
    units_label.config(font=("Arial", 9), bg="white")

    parameter_spinbox.bind("<Return>", update_spinbox)
    parameter_spinbox.bind("<FocusOut>", update_spinbox)

    return control_variables

def harmonic_type_selector(
    frame: tk.Frame,
    row: int,
    column: int
):
    
    global harmonics_type_var
    harmonics_options = [
        "None",
        "All",
        "Even", 
        "Odd", 
        "Triplen",
        "Non-Triplen Odd",
        "Positive Sequence",
        "Negative Sequence",
        "Zero Sequence"
    ]

    type_label = tk.Label(frame, text="Harmonics Type:")
    type_label.grid(row=row, column=column, sticky="W", padx=10)
    type_label.config(font=("Arial", 10, "bold"), bg="white")

    harmonics_type_var = tk.StringVar(frame)
    harmonics_type_var.set("None")
    harmonics_type_var.trace_add(
        'write', 
        lambda *args: update(
            int(harmonic_spinbox.configure('from')[4]),
            parameter_id=0x48,
            type="B",
            phase_id=0,
            type_changed=True
        )
    )

    option_menu = tk.OptionMenu(frame, harmonics_type_var, *harmonics_options)
    option_menu.config(width=17, bg="white", highlightthickness=0)
    option_menu.grid(row=row, column=column + 2, sticky="W", padx=10)

def iomod_settings(frame: tk.Frame, row: int, column: int):

    global sensor_setting_entries

    params = {
        "Primary Current (A):": 100,
        "Primary Voltage (V):": 10000,
        "Current sensor (mV):": 225,
        "Voltage sensor (V):": 1.876
    }

    sensor_setting_entries = []

    for r, (label, value) in enumerate(params.items()):

        if r > 1:
            column = 2
            r -= 2

        parameter_label = tk.Label(frame, text=label)
        parameter_label.grid(
            row=row + r, 
            column=column, 
            sticky="W", 
            padx=(5, 15), 
            pady=5
        )
        parameter_label.config(font=("Arial", 10, "bold"), bg="white")

        parameter_entry = tk.Entry(frame, width=7)
        parameter_entry.grid(
            row=row + r, 
            column=column + 1, 
            padx=(0, 20), 
            pady=5
        )
        parameter_entry.insert(0, str(value))

        sensor_setting_entries.append(parameter_entry)
     


def main_parameters_controls(
    frame: tk.Frame,
    start_row: int,
    start_column: int
):

    labels = [
        "U (Frequency):",
        "I (Frequency):",
        "U (Amplitude):",
        "I (Amplitude):",
        "U (Angle):",
        "I (Angle):"
    ]

    for i, label in enumerate(labels, start=1):

        parameter_label = tk.Label(frame, text=label)
        parameter_label.grid(
            row=start_row + i, 
            column=start_column, 
            sticky="W", 
            padx=(5, 15), 
            pady=5
        )
        parameter_label.config(font=("Arial", 10, "bold"), bg="white")

    
    units = [ "Hz", "Hz", "V", "A", "°", "°" ]
    min_values = [ 0, 0, 0, 0, 0, 0 ]
    max_values = [ 
        100, 
        100, 
        int(10 * voltage_sensor_coefficient * sqrt(2)), 
        int(10 * current_sensor_coefficient * sqrt(2)),
        360,  
        360
     ]
    resolutions = [ 1, 1, 1, 1, 1, 1 ]
    default_amplitudes = {
        "u1": int(round_half_up(amplitude["u1"])),
        "u2": int(round_half_up(amplitude["u2"])),
        "u3": int(round_half_up(amplitude["u3"])),
        "i1": int(round_half_up(amplitude["i1"])),
        "i2": int(round_half_up(amplitude["i2"])),
        "i3": int(round_half_up(amplitude["i3"]))
    }
    default_values = [
        [ 50, 50, default_amplitudes["u1"], default_amplitudes["i1"], 0,  0 ],
        [ 50, 50, default_amplitudes["u2"], default_amplitudes["i2"], 240, 240 ],
        [ 50, 50, default_amplitudes["u3"], default_amplitudes["i3"], 120, 120 ]
    ]
    update_functions = [
        update, 
        update, 
        update, 
        update, 
        update, 
        update
     ]
    parameter_ids = [ 0x46, 0x46, 0x41, 0x41, 0x50,  0x50 ]
    types = [ "U", "I", "U", "I", "U",  "I" ]
    
    for c, line in enumerate(lines):

        column_label = tk.Label(frame, text=line)
        column_label.grid(
            row=start_row, 
            column=start_column + 1 + 2 * c, 
            columnspan=2,
            pady=(5, 15)
        )
        column_label.config(font=("Arial", 10, "bold"), bg="white")

        if line == "N": break

        loop_params = list(zip(
            labels,
            units,
            min_values,
            max_values,
            resolutions,
            default_values[c],
            update_functions
        ))


        for r, (label, unit, min_value, max_value, resolution, default_value, update_function) in enumerate(loop_params, start=1):

            parameter_control_variables = parameter_controls(
                frame=frame,
                row=start_row + r,
                column=start_column + 1 + 2 * c,
                update_function=update_function,
                unit=unit,
                min_value=min_value,
                max_value=max_value,
                resolution=resolution,
                default_value=default_value,
                parameter_id=parameter_ids[r - 1],
                type=types[r - 1],
                phase_id=c + 1
            )

    

def get_rms(signal) -> float:

    return np.sqrt(np.mean(np.square(signal)))

def update_rms_values():

    calculate_signals()

    for i, (signal_name, signal) in enumerate(signals.items()):

        rms_values[signal_name] = get_rms(signal)
        rms_value_to_show = int(round_half_up(rms_values[signal_name]))
        rms_entries[i].delete(0, tk.END)
        rms_entries[i].insert(0, str(rms_value_to_show))
    
    update_power_values()

def rms_measurements(frame: tk.Frame, row: int, column: int):

    i = 0

    rms_coefficients = []

    rms_names = [ "U (RMS):", "I (RMS):"]

    for r, label in enumerate(rms_names, start=1):

        parameter_label = tk.Label(frame, text=label)
        parameter_label.grid(
            row=row + r, 
            column=column, 
            sticky="W", 
            padx=(5, 15), 
            pady=5
        )
        parameter_label.config(font=("Arial", 10, "bold"), bg="white")

    for r, unit in enumerate([ "V", "A" ], start=1):
        for c in range(len(lines)):
            
            rms_entry = tk.Entry(frame, width=9)
            rms_entry.grid(
                row=row + r, 
                column=column + 1 + 2 * c,
                # padx=(0, 20),
                pady=5
            )

            units_label = tk.Label(frame, text=unit)
            units_label.grid(
                row=row + r, 
                column=column + 2 + 2 * c, 
                padx=(0, 20),
                sticky="W"
            )
            units_label.config(font=("Arial", 9), bg="white")
            
            rms_values[list(signals.keys())[i]] = get_rms(list(signals.values())[i])
            rms_value_to_show = int(round_half_up(rms_values[list(signals.keys())[i]]))
            rms_entry.insert(0, str(rms_value_to_show))

            rms_entries.append(rms_entry)

            i+=1

def power_measurements(frame: tk.Frame, row: int, column: int):

    labels = [
        "Active Power (W):",
        "Reactive Power (VAR):",
        "Apparent Power (VA):",
        "Power Factor:"
    ]

    for i, label in enumerate(labels, start=1):

        parameter_label = tk.Label(frame, text=label)
        parameter_label.grid(
            row=row + i, 
            column=column, 
            sticky="W", 
            padx=(5, 15), 
            pady=5
        )
        parameter_label.config(font=("Arial", 10, "bold"), bg="white")

    for c, line in enumerate(lines):

        for r, label in enumerate(labels):

            parameter_entry = tk.Entry(frame, width=9)
            parameter_entry.grid(
                row=row + r + 1, 
                column=column + 1 + 2 * c,
                # padx=(0, 20),
                pady=5
            )
            power_entries.append(parameter_entry)
    
    update_power_values()
    
def update_power_values():

    indexes = ["1", "2", "3", "N"]

    for i in indexes:

        phase_difference = phase_angle["u" + i] - phase_angle["i" + i]
        powers["p" + i] = rms_values["u" + i] * rms_values["i" + i] * np.cos(phase_difference)
        powers["q" + i] = rms_values["u" + i] * rms_values["i" + i] * np.sin(phase_difference)
        powers["s" + i] = rms_values["u" + i] * rms_values["i" + i]
        powers["pf" + i] = powers["p" + i] / powers["s" + i]
        powers["p"] += powers["p" + i]
        powers["q"] += powers["q" + i]
        powers["s"] += powers["s" + i]

    powers["pf"] = powers["p"] / powers["s"]

    for entry, power_value in zip(power_entries, powers.values()):
            
        power_value = int(round_half_up(power_value))
        entry.delete(0, tk.END)
        entry.insert(0, str(power_value))




def main():

    global harmonic_spinbox
    global frame_signal_plot, frame_phasor_plot

    global harmonics_order_var

    global sensor_settings
    global voltage_sensor_coefficient
    global current_sensor_coefficient
    
    global amplitude
    global frequency
    global phase_angle
    global colors, lines

    global rms_values, rms_entries
    global powers, power_entries


    def on_closing():
        plt.close('all')
        root.destroy()

    logging.basicConfig(
        level = 'INFO', 
        style = '{', 
        format = 'line {lineno} - {levelname}: {message}'
    )

    root = tk.Tk()
    root.title('4Cs4Vs Test Bench GUI')
    root.configure(bg='white')
    
    menu(root)

    frame_iomod_settings = tk.Frame(root)
    frame_iomod_settings.grid(row=0, column=0, padx=10, pady=10)
    frame_iomod_settings.bind("<Button-1>", lambda event: frame_iomod_settings.focus_set())
    frame_iomod_settings.configure(bg='white')

    frame_main_params = tk.Frame(root)
    frame_main_params.grid(row=1, column=0, padx=10, pady=10)
    frame_main_params.bind("<Button-1>", lambda event: frame_main_params.focus_set())
    frame_main_params.configure(bg='white')

    frame_harmonics = tk.Frame(root)
    frame_harmonics.grid(row=0, column=1, padx=10, pady=10)
    frame_harmonics.bind("<Button-1>", lambda event: frame_harmonics.focus_set())
    frame_harmonics.configure(bg='white')

    frame_signal_plot = tk.Frame(root)
    frame_signal_plot.grid(row=0, column=1, padx=10, pady=10)
    frame_signal_plot.configure(bg='white')

    frame_phasor_plot = tk.Frame(root)
    frame_phasor_plot.grid(row=1, column=1, padx=10, pady=10)
    frame_phasor_plot.configure(bg='white')

    sensor_settings = {
        "primary_current": 100,
        "primary_voltage": 10000,
        "current_sensor_v": 0.225,
        "voltage_sensor_v": 1.876
    }

    voltage_sensor_coefficient = sensor_settings["primary_voltage"] / sensor_settings["voltage_sensor_v"]
    current_sensor_coefficient = sensor_settings["primary_current"] / sensor_settings["current_sensor_v"]


    amplitude = { 
        "u1": sensor_settings["primary_voltage"] * sqrt(2),
        "u2": sensor_settings["primary_voltage"] * sqrt(2),
        "u3": sensor_settings["primary_voltage"] * sqrt(2),
        "uN": 0,
        "i1": sensor_settings["primary_current"] * sqrt(2),
        "i2": sensor_settings["primary_current"] * sqrt(2),
        "i3": sensor_settings["primary_current"] * sqrt(2),
        "iN": 0
    }
    
    rms_values = {
        "u1": sensor_settings["primary_voltage"],
        "u2": sensor_settings["primary_voltage"],
        "u3": sensor_settings["primary_voltage"],
        "uN": 0,
        "i1": sensor_settings["primary_current"],
        "i2": sensor_settings["primary_current"],
        "i3": sensor_settings["primary_current"],
        "iN": 0
    }

    powers = {
        "p1": 0,
        "q1": 0,
        "s1": 0,
        "pf1": 0,
        "p2": 0,
        "q2": 0,
        "s2": 0,
        "pf2": 0,
        "p3": 0,
        "q3": 0,
        "s3": 0,
        "pf3": 0,
        "pN": 0,
        "qN": 0,
        "sN": 0,
        "pfN": 0,
        "p": 0,
        "q": 0,
        "s": 0,
        "pf": 0
    }

    rms_entries = []
    power_entries = []

    frequency = { 1: 50, 2: 50, 3: 50 }

    phase_angle = { 
        "u1": 0,
        "u2": 240,
        "u3": 120,
        "uN": 0,
        "i1": 0,
        "i2": 240,
        "i3": 120,
        "iN": 0
    }
    colors = ['brown', 'black', 'gray', 'blue']
    lines = [ "L1", "L2", "L3", "N" ]

    harmonic_type_selector(frame_harmonics, row=0, column=0)

    harmonic_control_variables = parameter_controls(
        frame_harmonics,
        row=0,
        column=3,
        update_function=update,
        unit="",
        min_value=1,
        max_value=50,
        resolution=1,
        default_value=1,
        parameter_id=0x48,
        type="B"
    )

    calculate_signals() 

    iomod_settings(frame_iomod_settings, row=0, column=0)
    
    main_parameters_controls(
        frame=frame_main_params,
        start_row=0,
        start_column=0
    )
    
    frame_main_params.rowconfigure(6, minsize=20)
    rms_measurements(frame_main_params, 7, 0)  
    frame_main_params.rowconfigure(10, minsize=20)
    power_measurements(frame_main_params, 10, 0)

    harmonic_spinbox= harmonic_control_variables["spinbox"]
    harmonics_order_var = harmonic_control_variables["var"]

    harmonic_spinbox.config(state="disabled")

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

main()