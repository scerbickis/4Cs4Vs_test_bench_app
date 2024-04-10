import tkinter as tk
import serial
import logging
import struct
from serial.tools import list_ports
from math import sqrt


def round_half_up(float_number: float) -> int:

    if float_number >= 0: return int(float_number + 0.5)
    else: return int(float_number - 0.5)



def check_response(request: bytes) -> bool:

    return
    response = ser.read(len(request))  # Read the response from the Arduino
    if response == request: return True
    else: logging.error(f"Error: received {response.hex('|')} instead of {request.hex('|')}")

def select_comport(comport):

    logging.debug(f"Selected Serial port: {comport}")
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

        if clear_entry: amplitude_entry_value.set("")
        global amplitude1, amplitude2, amplitude3

        amplitude = round_half_up(float(value)*6553.5)
        rms = round(float(value) / sqrt(2), 3)
        rms_label.config(text=f"RMS: {rms} V")

        # Create a packet with the command and the amplitude
        # 0x53 is the ASCII code for 'S' and 0x41 is the ASCII code for 'A'
        packet = bytes([0x53, 0x41, phase_id])
        packet += amplitude.to_bytes(2)  # Convert the amplitude to a 2-byte array and append it to the packet  
        logging.debug(
            f"Packet: {packet.hex('|')} "
            f"– Amplitude: {value} V – RMS: {rms} V"
        )
        
        if "ser" in globals():
            ser.write(packet) # Send the command to the Arduino
            check_response(packet)

        match phase_id:
            case 1: amplitude1 = float(value)
            case 2: amplitude2 = float(value)
            case 3: amplitude3 = float(value)

def update_frequency(value, clear_entry = True):

    global frequency1, frequency2, frequency3

    if clear_entry: frequency_entry_value.set("")

    frequency = round_half_up(float(value)*3.8)

    # Create a packet with the command and the frequency
    # 0x53 is the ASCII code for 'S' and 0x46 is the ASCII code for 'F'
    packet = bytes([0x53, 0x46, phase_id])
    packet += frequency.to_bytes(2)  # Convert the frequency to a 2-byte array and append it to the packet
    logging.debug(
        f"Packet: {packet.hex('|')} "
        f"– Frequency: {value} Hz"
    )

    if "ser" in globals():
        ser.write(packet) # Send the command to the Arduino
        check_response(packet)

    match phase_id:
        case 1: frequency1 = int(value)
        case 2: frequency2 = int(value)
        case 3: frequency3 = int(value)

def update_phase(value: str, clear_entry = True):

    global phase1, phase2, phase3

    if clear_entry: phase_entry_value.set("")

    phase_factor = int(value)/360
    #
    # Create a packet with the command and the phase factor
    # 0x53 is the ASCII code for 'S' and 0x50 is the ASCII code for 'P'
    packet = bytes([0x53, 0x50, phase_id])
    packet += struct.pack('>f', phase_factor)  # Convert the phase to a 4-byte array and append it to the packet
    # packet += value.to_bytes(2)  # Convert the phase to a 2-byte array and append it to the packet  
    logging.debug(
        f"Packet: {packet.hex('|')} "
        f"– Phase: {value}°"
    )
    
    if "ser" in globals():
        ser.write(packet) # Send the command to the Arduino
        check_response(packet)
    
    match phase_id:
        case 1: phase1 = int(value)
        case 2: phase2 = int(value)
        case 3: phase3 = int(value)

def update_harmonics(value, clear_entry = True):

    global harmonics1, harmonics2, harmonics3

    if clear_entry: harmonic_entry_value.set("")

    harmonics_number = int(value)

    # Create a packet with the command and the harmonics
    # 0x53 is the ASCII code for 'S' and 0x48 is the ASCII code for 'H'
    packet = bytes([0x53, 0x48, phase_id])

    match harmonics_var.get():
        # 0x45 is the ASCII code for 'E'
        case "Even": packet += bytes([0x45])
        # 0x4F is the ASCII code for 'O'
        case "Odd": packet += bytes([0x4F])
        # 0x54 is the ASCII code for 'T'
        case "Triplen": packet += bytes([0x54])
        # 0x52 is the ASCII code for 'R'
        case "Non-Triplen Odd": packet += bytes([0x52])
        # 0x50 is the ASCII code for 'P'
        case "Positive Sequence": packet += bytes([0x50])
        # 0x4E is the ASCII code for 'N'
        case "Negative Sequence": packet += bytes([0x4E])
        # 0x5A is the ASCII code for 'Z'
        case "Zero Sequence": packet += bytes([0x5A])

    # Convert the harmonics to a 1-byte array and append it to the packet
    packet += harmonics_number.to_bytes(1)  
    logging.debug(
        f"Packet: {packet.hex('|')} "
        f"– Harmonics: {harmonics_number} – Type: {harmonics_var.get()}"
    )
    
    if "ser" in globals():
        ser.write(packet) # Send the command to the Arduino
        check_response(packet)

    match phase_id:
        case 1: harmonics1 = {
            "count": harmonics_number, 
            "type": harmonics_var.get()
        }
        case 2: harmonics2 = {
            "count": harmonics_number, 
            "type": harmonics_var.get()
        }
        case 3: harmonics3 = {
            "count": harmonics_number, 
            "type": harmonics_var.get()
        }



def phase_selector(
    row: int,
    column: int        
):
    
    global phase_id
    phase_id = 1
    
    def phase_changed(*args):

        global phase_id
    
        match phase_var.get():

            case "1st": 
                
                phase_id = 1

                logging.debug(f"Selected phase: {phase_id}")

                update_amplitude(amplitude1, clear_entry=False)
                update_frequency(frequency1, clear_entry=False)
                harmonics_var.set(harmonics1["type"])
                
                amplitude_slider.set(str(amplitude1))
                phase_slider.set(str(phase1))
                frequency_slider.set(str(frequency1))
                harmonics_slider.set(str(harmonics1["count"]))
                

            case "2nd": 
                
                phase_id = 2

                logging.debug(f"Selected phase: {phase_id}")
                
                update_amplitude(amplitude2, clear_entry=False)
                update_frequency(frequency2, clear_entry=False)
                harmonics_var.set(harmonics2["type"])

                amplitude_slider.set(str(amplitude2))
                phase_slider.set(str(phase2))
                frequency_slider.set(str(frequency2))
                harmonics_slider.set(str(harmonics2["count"]))

            case "3rd": 
                
                phase_id = 3

                logging.debug(f"Selected phase: {phase_id}")

                update_amplitude(amplitude3, clear_entry=False)
                update_frequency(frequency3, clear_entry=False)
                harmonics_var.set(harmonics3["type"])
                
                amplitude_slider.set(str(amplitude3))
                phase_slider.set(str(240))
                frequency_slider.set(str(frequency3))
                harmonics_slider.set(str(harmonics3["count"]))
        
    phase_label = tk.Label(frame, text="Selected Phase:")
    phase_label.grid(row=row, column=column, sticky="W")
    phase_label.config(font=("Arial", 10, "bold"))

    # Create a Tkinter variable
    phase_var = tk.StringVar(frame)
    # Define the options
    phase_options = [
        "1st",
        "2nd",
        "3rd"
    ]

    # Set the default option
    phase_var.set("1st")
    phase_var.trace_add('write', phase_changed)

    # Create the dropdown menu
    option_menu = tk.OptionMenu(frame, phase_var, *phase_options)
    option_menu.grid(row=row, column=column + 1, sticky="W", padx=10)

def parameter_controls(
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
            update_function(parameter_var.get(), clear_entry=False)
        
        except ValueError as e:
            logging.error(e)

    parameter_label = tk.Label(frame, text=text)
    parameter_label.grid(row=row, column=column, sticky="W", padx=10)
    parameter_label.config(font=("Arial", 10, "bold"))

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

    units_label = tk.Label(frame, text=unit)
    units_label.grid(row=row, column=column + 2, sticky="W")
    units_label.config(font=("Arial", 9))

    parameter_slider = tk.Scale(
        frame,
        from_=slider_min,
        to=slider_max,
        resolution=resolution,
        orient=tk.HORIZONTAL,
        length=300,
        sliderlength=20,
        tickinterval=slider_tick,
        cursor="hand2",
        command=update_function,
        variable=parameter_var
    )
    parameter_slider.grid(row=row, column=column + 3)
    parameter_slider.set(default_value)  # Set the initial value of the slider
    parameter_var.set(default_value)  # Set the initial value of the variable
    update_function(parameter_var.get(), clear_entry=False)
    control_variables["slider"] = parameter_slider

    return control_variables

def harmonic_type_selector(
    row: int,
    column: int
):
    
    global harmonics_var

    harmonics_options = [
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
    type_label.config(font=("Arial", 10, "bold"))

    harmonics_var = tk.StringVar(frame)
    harmonics_var.set("Odd")
    harmonics_var.trace_add('write', lambda *args: update_harmonics(harmonics_slider.get()))

    option_menu = tk.OptionMenu(frame, harmonics_var, *harmonics_options)
    option_menu.grid(row=row, column=column + 3, sticky="W", padx=10)

def signal_on_off_controller(
    text: str,
    row: int,
    column: int,
    id: str

):
    
    def signal_status_changed(*args):

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
        logging.debug(
            f"Packet: {packet.hex('|')} "
            f"– Signal: {text} – Status: {radio_var.get()}"
        )  
        
        if "ser" in globals():
            ser.write(packet)
            check_response(packet)
     
    signal_label = tk.Label(frame, text=text)
    signal_label.grid(row=row, column=column, sticky="W")
    signal_label.config(font=("Arial", 9))
    frame.rowconfigure(row, minsize=50)

    # Create a Tkinter variable
    radio_var = tk.StringVar()
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

    # Create the "Off" radio button
    off_button = tk.Radiobutton(
        frame, 
        text="Off", 
        variable=radio_var, 
        value="Off"
    )
    off_button.grid(row=row, column=column + 2, sticky="W")


    # Set the default state
    radio_var.set("On")

def signal_on_off_controls(
    control_signals_start_row: int,
    control_signals_start_column: int
):
    
    output_label = tk.Label(frame, text="Control output signals:")
    output_label.grid(row=control_signals_start_row, column=control_signals_start_column, sticky="W")
    output_label.config(font=("Arial", 12, "bold"))

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


def main():

    global frame

    logging.basicConfig(
        level=logging.DEBUG, 
        style='{', 
        format='line {lineno} – {levelname}: {message}'
    )

    root = tk.Tk()
    root.title('4Cs4Vs Test Bench GUI')

    menu(root)

    # Create a frame for the GUI
    frame = tk.Frame(root)
    frame.pack()
    frame.bind("<Button-1>", lambda event: frame.focus_set())

    frame.columnconfigure(4, minsize=100)

    global rms_label

    global  amplitude_entry_value,\
            frequency_entry_value,\
            phase_entry_value,\
            harmonic_entry_value
    
    global  amplitude_slider,\
            frequency_slider,\
            phase_slider,\
            harmonics_slider
    
    global amplitude1, amplitude2, amplitude3
    global frequency1, frequency2, frequency3
    global phase1, phase2, phase3
    global harmonics1, harmonics2, harmonics3

    amplitude1 = 1; amplitude2 = 1; amplitude3 = 1  
    phase1 = 0; phase2 = 120; phase3 = 240
    frequency1 = 50; frequency2 = 50; frequency3 = 50
    harmonics1 = {"count": 1, "type": "Odd"}
    harmonics2 = {"count": 1, "type": "Odd"}
    harmonics3 = {"count": 1, "type": "Odd"}

    phase_selector(
        row=0, 
        column=0
    )

    rms_label = tk.Label(frame, text="RMS: 1.000 V")
    rms_label.grid(row=1, column=4, sticky="W", padx=10, pady=10)
    rms_label.config(font=("Arial", 9, "bold"))
    
    amplitude_control_variables = parameter_controls(
        row=1,
        column=0,
        text="Amplitude (V):",
        update_function=update_amplitude,
        unit="V",
        slider_min=0,
        slider_max=10,
        resolution=0.01,
        slider_tick=1,
        default_value=1.0
    )

    frequency_control_variables = parameter_controls(
        row=2,
        column=0,
        text="Frequency (Hz):",
        update_function=update_frequency,
        unit="Hz",
        slider_min=0,
        slider_max=100,
        resolution=1,
        slider_tick=10,
        default_value=50
    )

    phase_control_variables = parameter_controls(
        row=3,
        column=0,
        text="Phase (°):",
        update_function=update_phase,
        unit="°",
        slider_min=0,
        slider_max=360,
        resolution=1,
        slider_tick=30,
        default_value=0
    )

    harmonic_type_selector(row=5, column=0)

    harmonic_control_variables = parameter_controls(
        row=4,
        column=0,
        text="Harmonics Order:",
        update_function=update_harmonics,
        unit="",
        slider_min=0,
        slider_max=50,
        resolution=1,
        slider_tick=10,
        default_value=1
    )

    signal_on_off_controls(
        control_signals_start_row = 0, 
        control_signals_start_column = 11
    )

    amplitude_entry_value = amplitude_control_variables["entry_value"]
    frequency_entry_value = frequency_control_variables["entry_value"]
    phase_entry_value = phase_control_variables["entry_value"]
    harmonic_entry_value = harmonic_control_variables["entry_value"]

    amplitude_slider = amplitude_control_variables["slider"]
    frequency_slider = frequency_control_variables["slider"]
    phase_slider = phase_control_variables["slider"]
    harmonics_slider = harmonic_control_variables["slider"]

    root.mainloop()

main()