import tkinter as tk
import serial
import logging
import struct
import matplotlib.pyplot as plt
import numpy as np
from serial.tools import list_ports
from math import sqrt, hypot, atan2
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def round_half_up(float_number: float) -> int:

    if float_number >= 0: return int(float_number + 0.5)
    else: return int(float_number - 0.5)

def update_signal():

    if "harmonics_slider" not in globals(): return

    loop_params = zip(amplitude.values(), frequency.values(), phase.values(), signals)

    yN = 0

    for a, f, ph, signal in loop_params:

        # Add harmonics if specified
        
        step = int(harmonics_slider.configure('resolution')[4])
        first_harmonic = int(harmonics_slider.configure('from')[4])
        harmonics_order = int(harmonics_slider.get())

        y = 0

        for h in range(first_harmonic, harmonics_order + 1, step):
            
            if harmonics_type_var.get() == "Non-Triplen Odd" and h % 3 == 0: continue
            
            y += a / h * np.sin(h * (2 * np.pi *  f / 1000  * t + ph * np.pi / 180))
        
        signal.set_ydata(y)
        yN += y

    signalN.set_ydata(yN)

    canvas_signals.draw()

def plot_signal(row: int, column: int):

    global signals, canvas_signals, t, signalN

    signals = []

    t = np.linspace(0, 20, 10000, endpoint=False)

    # Create a figure and a subplot
    fig, ax = plt.subplots()
    fig.set_size_inches(6, 4)
    ax.set_ylim(-10, 10)
    ax.set_ylabel("Amplitude (V Pk-Pk)")
    ax.set_xlabel("Time (ms)")
    ax.grid(linewidth=0.5, color='lightgray', linestyle='--')
    ax.axhline(0, color='black', linewidth=0.5)  # Add x-axis

    loop_params = zip(amplitude.values(), frequency.values(), phase.values(), colors)

    yN = 0
    
    # For each phase
    for i, (A, f, ph, color) in enumerate(loop_params):

        # Calculate the y values for the sine wave
        y = A * np.sin(2 * np.pi * f / 1000 * t + ph * np.pi / 180)

        yN += y

        # Plot x against y
        signal, = ax.plot(t, y, label = f"L{i}", color=color)
        signals.append(signal)

    signalN, = ax.plot(t, yN, label = "N", color=colors[-1])

    ax.legend(loc = "upper right", bbox_to_anchor=(1, 1), prop={'size': 7})
    
    canvas_signals = FigureCanvasTkAgg(fig, master=frame)
    
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

    angles_rad = [ np.pi * p / 180 for p in phase.values() ]

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

def plot_phasors(row: int, column: int):

    global phasors, canvas_phasors
    global phasorN

    phasors = []

    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.set_ylim(0, 10)
    ax.set_rticks([i for i in range(1, 11)])
    ax.set_xticks(np.linspace(0, 2*np.pi, 12, endpoint=False))
    ax.grid(linewidth=0.5, color='lightgray', linestyle='--')

    angles_rad = [ np.pi * p / 180 for p in phase.values() ]

    loop_params = zip(angles_rad, amplitude.values(), colors)

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
        
    canvas_phasors = FigureCanvasTkAgg(fig, master=frame)

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
    



def check_response(request: bytes) -> bool:

    return
    response = ser.read(len(request))  # Read the response from the Arduino
    if response == request: return True
    else: logging.error(f"Error: received {response.hex('|')} instead of {request.hex('|')}")

def select_comport(comport):

    logging.info(f"Selected Serial port: {comport}")
    global selected_comport
    selected_comport = comport

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

    menubar.add_command(label="Connect", command=connect)
    menubar.add_cascade(label="Serial Port", menu=comport_menu)

    root.config(menu=menubar)



def update_amplitude(value: str, clear_entry = True):
        
        global amplitude

        amplitude[phase_id] = float(value)
        update_signal()
        update_phasor()

        if clear_entry: amplitude_entry_value.set("")

        rms = round(float(value) / sqrt(2), 3)
        rms_label.config(text=f"RMS: {rms} V")

        # Create a packet with the command and the amplitude
        # 0x53 is the ASCII code for 'S' and 0x41 is the ASCII code for 'A'
        packet = bytes([0x53, 0x41, phase_id])
        # Convert the amplitude to a 2-byte array and append it to the packet
        packet += round_half_up(float(value)*6553.5).to_bytes(2)    
        logging.info(
            f"Packet: {packet.hex('|')} "
            f"– Amplitude: {value} V – RMS: {rms} V"
        )
        
        if "ser" in globals():
            ser.write(packet) # Send the command to the Arduino
            check_response(packet)

def update_frequency(value, clear_entry = True):

    global frequency

    frequency[phase_id] = int(value)
    update_signal()

    if clear_entry: frequency_entry_value.set("")

    # Create a packet with the command and the frequency
    # 0x53 is the ASCII code for 'S' and 0x46 is the ASCII code for 'F'
    packet = bytes([0x53, 0x46, phase_id])
    # Convert the frequency to a 2-byte array and append it to the packet
    packet += round_half_up(float(value) * 5.32).to_bytes(2)  
    logging.info(
        f"Packet: {packet.hex('|')} "
        f"– Frequency: {value} Hz"
    )

    if "ser" in globals():
        ser.write(packet) # Send the command to the Arduino
        check_response(packet)

def update_phase(value: str, clear_entry = True):

    global phase

    phase[phase_id] = int(value)
    update_signal()
    update_phasor()

    if clear_entry: phase_entry_value.set("")

    phase_factor = int(value)/360
    #
    # Create a packet with the command and the phase factor
    # 0x53 is the ASCII code for 'S' and 0x50 is the ASCII code for 'P'
    packet = bytes([0x53, 0x50, phase_id])
    packet += struct.pack('>f', phase_factor)  # Convert the phase to a 4-byte array and append it to the packet
    # packet += value.to_bytes(2)  # Convert the phase to a 2-byte array and append it to the packet  
    logging.info(
        f"Packet: {packet.hex('|')} "
        f"– Phase: {value}°"
    )
    
    if "ser" in globals():
        ser.write(packet) # Send the command to the Arduino
        check_response(packet)
    
def update_harmonics(value, clear_entry = True, type_changed = False):

    if clear_entry: harmonic_entry_value.set("")

    harmonics_order = int(value)

    # Create a packet with the command and the harmonics
    # 0x53 is the ASCII code for 'S' and 0x48 is the ASCII code for 'H'
    packet = bytes([0x53, 0x48, phase_id])

    match harmonics_type_var.get():
        # 0x42 is the ASCII code for 'B' (B - bez)
        case "None": 

            harmonics_order_var.set(1)
            harmonics_order = 1
            harmonics_slider.configure(
                from_ = 1,
                to = 50,
                resolution = 1,
                state = "disabled",
                cursor = "arrow"
            )
            
            harmonic_entry_value.set("1")
            harmonic_entry.config(state = "disabled")

            packet += bytes([0x42])

        # 0x41 is the ASCII code for 'A' (A - all)
        case "All": 

            harmonics_slider.configure(
                from_ = 1,
                to = 50,
                resolution = 1,
                tickinterval = 4,
                state = "normal",
                cursor = "hand2"
            )

            harmonic_entry.config(state = "normal")

            packet += bytes([0x41])

        # 0x45 is the ASCII code for 'E'
        case "Even": 

            harmonics_slider.configure(
                from_=2,
                to = 50,
                resolution=2,
                state = "normal",
                tickinterval = 4,
                cursor = "hand2"
            )

            harmonic_entry.config(state = "normal")


            packet += bytes([0x45])

        # 0x4F is the ASCII code for 'O'
        case "Odd": 

            harmonics_slider.configure(
                from_ = 1,
                to = 49,
                resolution = 2,
                tickinterval = 4,
                state = "normal",
                cursor = "hand2"
            )

            harmonic_entry.config(state = "normal")
            packet += bytes([0x4F])

        # 0x54 is the ASCII code for 'T'
        case "Triplen": 
            
            harmonics_slider.configure(
                from_ = 3,
                to = 45,
                resolution = 6,
                tickinterval = 6,
                state = "normal",
                cursor = "hand2"
            )

            harmonic_entry.config(state = "normal")
            
            packet += bytes([0x54])

        # 0x52 is the ASCII code for 'R'
        case "Non-Triplen Odd": 
            
            harmonics_slider.configure(
                from_ = 1,
                to = 49,
                resolution = 2,
                tickinterval = 6,
                state = "normal",
                cursor = "hand2"
            )

            harmonic_entry.config(state = "normal")
            
            if harmonics_order % 3 == 0: 
                harmonics_order += 2
                harmonics_slider.set(harmonics_order)
            
            
            packet += bytes([0x52])

        # 0x50 is the ASCII code for 'P'
        case "Positive Sequence": 
            
            harmonics_slider.configure(
                from_ = 1,
                to = 49,
                resolution = 3,
                tickinterval = 6,
                state = "normal",
                cursor = "hand2"
            )
            
            harmonic_entry.config(state = "normal")

            packet += bytes([0x50])

        # 0x4E is the ASCII code for 'N'
        case "Negative Sequence": 
            
            harmonics_slider.configure(
                from_ = 2,
                to = 50,
                resolution = 3,
                tickinterval = 6,
                state = "normal",
                cursor = "hand2"
            )

            harmonic_entry.config(state = "normal")

            packet += bytes([0x4E])

        # 0x5A is the ASCII code for 'Z'
        case "Zero Sequence": 
            
            harmonics_slider.configure(
                from_ = 3,
                to = 48,
                resolution = 3,
                tickinterval = 6,
                state = "normal",
                cursor = "hand2"
            )

            harmonic_entry.config(state = "normal")

            packet += bytes([0x5A])

    if type_changed: 
        harmonics_order_var.set(harmonics_slider.configure('from')[4])   
        harmonics_order = int(harmonics_order_var.get())  

    update_signal()

    # Convert the harmonics to a 1-byte array and append it to the packet
    packet += harmonics_order.to_bytes(1)  
    logging.info(
        f"Packet: {packet.hex('|')} "
        f"– Harmonics: {harmonics_order} – Type: {harmonics_type_var.get()}"
    )
    
    if "ser" in globals():
        ser.write(packet) # Send the command to the Arduino
        check_response(packet)


def phase_selector(
    row: int,
    column: int        
):
    
    global phase_id
    phase_id = 1
    
    def phase_changed(*args):

        global phase_id
    
        match phase_var.get():

            case "1st": phase_id = 1
            case "2nd": phase_id = 2
            case "3rd": phase_id = 3
        
        logging.info(f"Selected phase: {phase_id}")

        update_amplitude(amplitude[phase_id], clear_entry=False)
        update_frequency(frequency[phase_id], clear_entry=False)
        
        amplitude_slider.set(str(amplitude[phase_id]))
        phase_slider.set(str(phase[phase_id]))
        frequency_slider.set(str(frequency[phase_id]))

    phase_label = tk.Label(frame, text="Selected Phase:")
    phase_label.grid(row=row, column=column, sticky="W")
    phase_label.config(font=("Arial", 10, "bold"), bg="white")

    # Create a Tkinter variable
    phase_var = tk.StringVar(frame)
    # Define the options
    phase_options = [ "1st", "2nd", "3rd" ]

    # Set the default option
    phase_var.set("1st")
    phase_var.trace_add('write', phase_changed)

    # Create the dropdown menu
    option_menu = tk.OptionMenu(
        frame, 
        phase_var, 
        *phase_options
    )
    option_menu.config(width=4, bg="white", highlightthickness=0)
    option_menu.grid(row=row, column=column + 1, sticky="W", padx=10)

def pparameter_controls(
        row: int,
        column: int,
        text: str,
        update_function: callable,
        unit: str,
        slider_min: int,
        slider_max: int,
        resolution: float|int,
        slider_tick: int,
        default_value: int|float
):
    
    control_variables = {}

    def update_slider(*args):
        try:
            if parameter_entry_value.get() == "": return
            if isinstance(parameter_var, tk.IntVar):
                parameter_var.set(int(parameter_entry_value.get()))
            elif isinstance(parameter_var, tk.DoubleVar):
                parameter_var.set(float(parameter_entry_value.get()))
            update_function(parameter_slider.get(), clear_entry=False)
        
        except ValueError as e:
            logging.error(e)

    parameter_label = tk.Label(frame, text=text)
    parameter_label.grid(row=row, column=column, sticky="W", padx=10)
    parameter_label.config(font=("Arial", 10, "bold"), bg="white")

    if isinstance(default_value, int):
        parameter_var = tk.IntVar(value=default_value)
    elif isinstance(default_value, float):
        parameter_var = tk.DoubleVar(value=default_value) 

    control_variables["var"] = parameter_var

    parameter_entry_value = tk.StringVar()
    parameter_entry_value.set(str(default_value))
    control_variables["entry_value"] = parameter_entry_value
    parameter_entry = tk.Entry(
        frame, 
        textvariable=parameter_entry_value, 
        width=5
    )
    parameter_entry.grid(row=row, column=column + 1, sticky="E")
    
    parameter_entry.bind("<Return>", update_slider)
    parameter_entry.bind("<FocusOut>", update_slider)

    control_variables["entry"] = parameter_entry

    units_label = tk.Label(frame, text=unit)
    units_label.grid(
        row = row, 
        column = column + 2, 
        sticky = "W"
    )
    units_label.config(font=("Arial", 9), bg="white")

    parameter_slider = tk.Scale(
        frame,
        from_=slider_min,
        to=slider_max,
        resolution=resolution,
        orient=tk.HORIZONTAL,
        length=300,
        sliderlength=20,
        tickinterval = slider_tick,
        cursor = "hand2",
        command = update_function,
        variable = parameter_var,
        bg="white",
        highlightthickness=0
    )
    parameter_slider.grid(
        row = row, 
        column = column + 3,
        padx = 10,
        sticky = "E"
    )
    parameter_slider.set(default_value)  # Set the initial value of the slider
    parameter_var.set(default_value)  # Set the initial value of the variable
    control_variables["slider"] = parameter_slider

    return control_variables

def parameter_controls(
    frame: tk.Frame,
    row: int,
    column: int,
    label: str,
    update_function: callable,
    unit: str,
    min_value: int,
    max_value: int,
    resolution: float|int,
    default_value: int|float
):
    
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
        width=5,
        textvariable=parameter_var,
        command=update_function
    )
    parameter_spinbox.grid(
        row=row, 
        column=column + 1, 
        sticky="W"
    )

    control_variables["spinbox"] = parameter_spinbox

    units_label = tk.Label(frame, text=unit)
    units_label.grid(
        row = row, 
        column = column + 2, 
        sticky = "W",
        pady=5
    )
    units_label.config(font=("Arial", 9), bg="white")

    # parameter_spinbox.bind("<Return>", update_slider)
    # parameter_spinbox.bind("<FocusOut>", update_slider)

    return control_variables



def harmonic_type_selector(
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
        lambda *args: update_harmonics(
            harmonics_slider.get(),
            type_changed=True
        )
    )

    option_menu = tk.OptionMenu(frame, harmonics_type_var, *harmonics_options)
    option_menu.config(width=17, bg="white", highlightthickness=0)
    option_menu.grid(row=row, column=column + 3, sticky="W", padx=10)

def signal_on_off_controller(
    text: str,
    row: int,
    column: int,
    id: str
):
    
    def signal_status_changed(*args):

        # signal_status[id] = radio_var.get()
        if radio_var.get() == "Off": 
            amplitude[int(id[-1])] = 0
            amplitude_slider.set(0)
            amplitude_slider.configure(state="disabled")
        else:
            amplitude_slider.configure(state="normal")
            amplitude_slider.set(1)
            amplitude[int(id[-1])] = 1
        update_signal()
        update_phasor()
        
        # Create a packet with the command and the signal status
        # 0x53 is the ASCII code for 'S' and 0x4F is the ASCII code for 'O'
        packet = [0x53, 0x4F, phase_id]
        match id.casefold():
            case "u1":
                packet.append(0x00)
            case "u2":
                packet.append(0x01)
            case "u3":
                packet.append(0x02)
            case "un":
                packet.append(0x03) 
            case "i1":
                packet.append(0x04)
            case "i2":
                packet.append(0x05)
            case "i3":
                packet.append(0x06)
            case "in":
                packet.append(0x07)

        if radio_var.get() == "On":
            packet[-1] += 0x10  # Turn the signal on

        packet = bytes(packet)
        logging.info(
            f"Packet: {packet.hex('|')} "
            f"– Signal: {text} – Status: {radio_var.get()}"
        )  
        
        if "ser" in globals():
            ser.write(packet)
            check_response(packet)
     
    signal_label = tk.Label(frame, text=text)
    signal_label.grid(row=row, column=column, sticky="W")
    signal_label.config(font=("Arial", 9), bg="white")
    frame.rowconfigure(row, minsize=50)

    # Create a Tkinter variable
    radio_var = tk.StringVar()
    # Set the default state
    radio_var.set("On")
    # Trace the variable
    radio_var.trace_add('write', signal_status_changed)

    # Create the "On" radio button
    on_button = tk.Radiobutton(
        frame, 
        text="On", 
        variable=radio_var, 
        value="On"
    )
    on_button.grid(row=row, column=column + 1)
    on_button.config(bg="white")

    # Create the "Off" radio button
    off_button = tk.Radiobutton(
        frame, 
        text="Off", 
        variable=radio_var, 
        value="Off"
    )
    off_button.grid(row=row, column=column + 2, sticky="W")
    off_button.config(bg="white")

def signal_on_off_controls(
    control_signals_start_row: int,
    control_signals_start_column: int
):
    
    output_label = tk.Label(frame, text="Output signal statuses:")
    output_label.grid(row=control_signals_start_row, column=control_signals_start_column, sticky="W")
    output_label.config(font=("Arial", 12, "bold"), bg="white")

    signal_on_off_controller(
        "First phase voltage (u1)", 
        control_signals_start_row + 1, 
        control_signals_start_column, 
        "u1"
    )

    signal_on_off_controller(
        "Second phase voltage (u2)", 
        control_signals_start_row + 2, 
        control_signals_start_column, 
        "u2"
    )

    signal_on_off_controller(
        "Third phase voltage (u3)", 
        control_signals_start_row + 3, 
        control_signals_start_column, 
        "u3"
    )

    signal_on_off_controller(
        "Neutral voltage (uN)", 
        control_signals_start_row + 4, 
        control_signals_start_column, 
        "uN"
    )

    signal_on_off_controller(
        "First phase current (i1)", 
        control_signals_start_row + 5, 
        control_signals_start_column, 
        "i1"
    )

    signal_on_off_controller(
        "Second phase current (i2)", 
        control_signals_start_row + 6, 
        control_signals_start_column, 
        "i2"
    )

    signal_on_off_controller(
        "Third phase current (i3)", 
        control_signals_start_row + 7, 
        control_signals_start_column, 
        "i3"
    )

    signal_on_off_controller(
        "Neutral current (iN)", 
        control_signals_start_row + 8, 
        control_signals_start_column, 
        "iN"
    )

def main_parameters_controls(
    frame: tk.Frame,
    start_row: int,
    start_column: int
):

    labels = [
        "Frequency:",
        "U (Amplitude):",
        "U (Angle):",
        "I (Amplitude):",
        "I (Angle):"
    ]

    for i, label in enumerate(labels, start=1):

        parameter_label = tk.Label(frame, text=label)
        parameter_label.grid(
            row=start_row + i, 
            column=start_column, 
            sticky="W", 
            padx=10, 
            pady=5
        )
        parameter_label.config(font=("Arial", 10, "bold"), bg="white")

    lines = [ "L1", "L2", "L3" ]
    units = [ "Hz", "V", "°", "A", "°" ]
    min_values = [ 0, 0, 0, 0, 0 ]
    max_values = [ 100, 10, 360, 10, 360 ]
    resolutions = [ 1, 0.01, 1, 0.01, 1 ]
    default_values = [ 50, 1.0, 0, 1.0, 0 ]
    update_functions = [ 
        update_frequency, 
        update_amplitude, 
        update_phase, 
        update_amplitude, 
        update_phase
     ]
    
    loop_params = list(zip(
        labels,
        units,
        min_values,
        max_values,
        resolutions,
        default_values,
        update_functions
    ))

    for c, line in enumerate(lines, start=1):

        parameter_label = tk.Label(frame, text=line)
        parameter_label.grid(
            row=start_row, 
            column=start_column + c, 
            sticky="W", 
            padx=10, 
            pady=5
        )
        parameter_label.config(font=("Arial", 10, "bold"), bg="white")

        for r, (label, unit, min_value, max_value, resolution, default_value, update_function) in enumerate(loop_params, start=1):

            parameter_control_variables = parameter_controls(
                frame=frame,
                row=start_row + r,
                column=start_column + c,
                label=label,
                update_function=update_function,
                unit=unit,
                min_value=min_value,
                max_value=max_value,
                resolution=resolution,
                default_value=default_value
            )


def main():

    def on_closing():
        plt.close('all')
        root.destroy()

    global frame

    logging.basicConfig(
        level = 'INFO', 
        style = '{', 
        format = 'line {lineno} – {levelname}: {message}'
    )

    root = tk.Tk()
    root.title('4Cs4Vs Test Bench GUI')
    root.configure(bg='white')
    
    menu(root)

    # Create a frame for the GUI
    # frame = tk.Frame(root)
    # frame.pack()
    # frame.bind("<Button-1>", lambda event: frame.focus_set())
    # frame.configure(bg='white')

    frame_main_params = tk.Frame(root)
    frame_main_params.grid(row=0, column=0, padx=10, pady=10)
    frame_main_params.configure(bg='white')

    # for i in range(12): 
    #     frame.columnconfigure(i, weight=1)
    #     frame.rowconfigure(i, weight=1)

    # frame.columnconfigure(3, minsize=300, weight=1)
    # frame.columnconfigure(4, minsize=100, weight=1)
    # frame.columnconfigure(11, minsize=20, weight=1)

    global rms_label

    global  amplitude_entry_value,\
            frequency_entry_value,\
            phase_entry_value,\
            harmonic_entry_value
    
    global  harmonic_entry

    global  harmonics_order_var
    
    global  amplitude_slider,\
            frequency_slider,\
            phase_slider,\
            harmonics_slider
    
    global amplitude
    global frequency
    global phase
    global colors

    amplitude = { 1: 1, 2: 1, 3: 1 }
    frequency = { 1: 50, 2: 50, 3: 50 }
    phase = { 1: 0, 2: 120, 3: 240 }
    colors = ['brown', 'black', 'gray', 'blue']

    # phase_selector(
    #     row=0, 
    #     column=0
    # )

    # rms_label = tk.Label(frame, text="RMS: 1.000 V")
    # rms_label.grid(row=1, column=4, sticky="W")
    # rms_label.config(font=("Arial", 9, "bold"), bg="white")


    main_parameters_controls(
        frame=frame_main_params,
        start_row=0,
        start_column=0
    )
    

    
    # amplitude_control_variables = parameter_controls(
    #     row=1,
    #     column=0,
    #     text="Amplitude (V):",
    #     update_function=update_amplitude,
    #     unit="V",
    #     slider_min=0,
    #     slider_max=10,
    #     resolution=0.01,
    #     slider_tick=1,
    #     default_value=1.0
    # )

    # frequency_control_variables = parameter_controls(
    #     row=2,
    #     column=0,
    #     text="Frequency (Hz):",
    #     update_function=update_frequency,
    #     unit="Hz",
    #     slider_min=0,
    #     slider_max=100,
    #     resolution=1,
    #     slider_tick=10,
    #     default_value=50
    # )

    # phase_control_variables = parameter_controls(
    #     row=3,
    #     column=0,
    #     text="Phase (°):",
    #     update_function=update_phase,
    #     unit="°",
    #     slider_min=0,
    #     slider_max=360,
    #     resolution=1,
    #     slider_tick=30,
    #     default_value=0
    # )

    # harmonic_type_selector(row=5, column=0)

    # harmonic_control_variables = pparameter_controls(
    #     row=6,
    #     column=0,
    #     text="Harmonics Order:",
    #     update_function=update_harmonics,
    #     unit="",
    #     slider_min=1,
    #     slider_max=50,
    #     resolution=1,
    #     slider_tick=4,
    #     default_value=1
    # )

    # signal_on_off_controls(
    #     control_signals_start_row = 0, 
    #     control_signals_start_column = 12
    # )

    # plot_signal(row=10, column=0)

    # plot_phasors(row=10, column=5)

    # # amplitude_entry_value = amplitude_control_variables["entry_value"]
    # # frequency_entry_value = frequency_control_variables["entry_value"]
    # # phase_entry_value = phase_control_variables["entry_value"]
    # harmonic_entry_value = harmonic_control_variables["entry_value"]

    # harmonic_entry = harmonic_control_variables["entry"]

    # harmonics_order_var = harmonic_control_variables["var"]

    # # amplitude_slider = amplitude_control_variables["slider"]
    # # frequency_slider = frequency_control_variables["slider"]
    # # phase_slider = phase_control_variables["slider"]
    # harmonics_slider = harmonic_control_variables["slider"]

    # harmonic_entry.config(state="disabled")
    # harmonics_slider.configure(state="disabled")

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

main()