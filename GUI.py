import tkinter as tk
import serial
import logging
from serial.tools import list_ports
from math import sqrt

logging.basicConfig(level=logging.DEBUG, style='{', format='{levelname}: {message}')

def round_half_up(float_number: float) -> int:

    if float_number >= 0: return int(float_number + 0.5)
    else: return int(float_number - 0.5)

def check_response(request: bytes) -> bool:

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
            ser = serial.Serial(selected_comport)
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

def amplitude_controls(
    frame: tk.Frame,
    row: int,
    column: int
):
    
    # Function to send control parameters to the Arduino
    def update_amplitude(value):

        amplitude = round_half_up(float(value)*6553.5)
        rms = round(float(value) / sqrt(2), 3)
        rms_label.config(text=f"RMS: {rms} V")

        # Create a packet with the command and the amplitude
        # 0x53 is the ASCII code for 'S' and 0x41 is the ASCII code for 'A'
        packet = bytes([0x53, 0x41])
        packet += amplitude.to_bytes(2)  # Convert the amplitude to a 2-byte array and append it to the packet  
        logging.debug(packet.hex('|'))
        
        if "ser" in globals():
            ser.write(packet) # Send the command to the Arduino
            check_response(packet)
    
    def update_slider(*args):

        try:
            amplitude.set(float(amplitude_entry_value.get()))
            update_amplitude(amplitude.get())

        except ValueError:
            pass

    amplitude_label = tk.Label(frame, text="Amplitude (V):")
    amplitude_label.grid(row=row, column=column + 2)
    amplitude_label.config(font=("Arial", 12, "bold"))

    amplitude = tk.DoubleVar(value=1) 

    amplitude_entry_value = tk.StringVar()
    amplitude_entry_value.set("1")
    amplitude_entry_value.trace_add("write", update_slider)
    amplitude_entry = tk.Entry(
        frame, 
        textvariable=amplitude_entry_value, 
        width=5
    )
    amplitude_entry.grid(row=row + 1, column=column, sticky="E")

    units_label = tk.Label(frame, text="V")
    units_label.grid(row=row + 1, column=column + 1, sticky="W")
    units_label.config(font=("Arial", 9))
    
    amplitude_slider = tk.Scale(
        frame,
        from_=0,
        to=10,
        resolution=0.01,
        orient=tk.HORIZONTAL,
        length=300, 
        sliderlength=20,
        tickinterval=1,
        cursor="hand2",
        command=update_amplitude,
        variable=amplitude
    )
    
    amplitude_slider.grid(row=row + 1, column=column + 2, sticky="E")
    amplitude_slider.set(1)  # Set the initial value of the slider

    rms_label = tk.Label(frame, text="RMS: 0.000 V")
    rms_label.grid(row=row + 1, column=column + 3, sticky="W", padx=10, pady=10)
    rms_label.config(font=("Arial", 9, "bold"))

def frequency_controls(
        frame: tk.Frame,
        row: int,
        column: int
):

    def update_frequency(value):

        frequency = round_half_up(float(value)*3.8)

        # Create a packet with the command and the frequency
        # 0x53 is the ASCII code for 'S' and 0x46 is the ASCII code for 'F'
        packet = bytes([0x53, 0x46])
        packet += frequency.to_bytes(2)  # Convert the frequency to a 2-byte array and append it to the packet
        logging.debug(packet.hex('|'))

        if "ser" in globals():
            ser.write(packet) # Send the command to the Arduino
            check_response(packet)
    
    def update_slider(*args):
        try:
            frequency.set(float(frequency_entry_value.get()))
            update_frequency(frequency.get())
        except ValueError:
            pass

    frequency_label = tk.Label(frame, text="Frequency (Hz):")
    frequency_label.grid(row=row, column=column + 2)
    frequency_label.config(font=("Arial", 12, "bold"))

    frequency = tk.DoubleVar(value=1) 

    frequency_entry_value = tk.StringVar()
    frequency_entry_value.set("50")
    frequency_entry_value.trace_add("write", update_slider)
    frequency_entry = tk.Entry(
        frame, 
        textvariable=frequency_entry_value, 
        width=5
    )
    frequency_entry.grid(row=row + 1, column=column, sticky="E")

    units_label = tk.Label(frame, text="Hz")
    units_label.grid(row=row + 1, column=column + 1, sticky="W")
    units_label.config(font=("Arial", 9))

    frequency_slider = tk.Scale(
        frame,
        from_=0,
        to=100,
        orient=tk.HORIZONTAL,
        length=300,
        sliderlength=20,
        tickinterval=10,
        cursor="hand2",
        command=update_frequency,
        variable=frequency
    )
    frequency_slider.grid(row=row + 1, column=column + 2)
    frequency_slider.set(50)  # Set the initial value of the slider

def harmonics_controls(
        frame: tk.Frame,
        row: int,
        column: int
):

    def update_harmonics(value):
    
        harmonics = int(value)
    
        # Create a packet with the command and the harmonics
        # 0x53 is the ASCII code for 'S' and 0x48 is the ASCII code for 'H'
        packet = bytes([0x53, 0x48])

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
        packet += harmonics.to_bytes(1)  
        logging.debug(packet.hex('|'))
        
        if "ser" in globals():
            ser.write(packet) # Send the command to the Arduino
            check_response(packet)
    
    def harmonic_changed(*args):
        
        update_harmonics(harmonics_slider.get())

    def update_slider(*args):
        try:
            harmonic.set(float(harmonic_entry_value.get()))
            update_harmonics(harmonic.get())
        except ValueError:
            pass

    harmonics_label = tk.Label(frame, text="Harmonics Order:")
    harmonics_label.grid(row=row, column=column + 2)
    harmonics_label.config(font=("Arial", 12, "bold"))

    # Create a Tkinter variable
    harmonics_var = tk.StringVar(frame)
    # Define the options
    harmonics_options = {
        "Even", 
        "Odd", 
        "Triplen",
        "Non-Triplen Odd",
        "Positive Sequence",
        "Negative Sequence",
        "Zero Sequence"
    }
    # Set the default option
    harmonics_var.set("Odd")

    harmonic = tk.DoubleVar(value=1) 

    harmonic_entry_value = tk.StringVar()
    harmonic_entry_value.set("1")
    harmonic_entry_value.trace_add("write", update_slider)
    amplitude_entry = tk.Entry(
        frame, 
        textvariable=harmonic_entry_value, 
        width=5
    )
    amplitude_entry.grid(row=row + 1, column=column, sticky="E")

    harmonics_slider = tk.Scale(
        frame,
        from_=0,
        to=50,
        orient=tk.HORIZONTAL,
        length=300,
        sliderlength=20,
        tickinterval=10,
        cursor="hand2",
        command=update_harmonics,
        variable=harmonic
    )
    harmonics_slider.grid(row=row + 1, column=column + 2)
    harmonics_slider.set(1)  # Set the initial value of the slider

    type_label = tk.Label(frame, text="Harmonics\nType:")
    type_label.grid(row=row, column=column + 3, sticky="SW", padx=10)
    type_label.config(font=("Arial", 11, "bold"))
    
    harmonics_var.trace_add('write', harmonic_changed)
    # Create the dropdown menu
    option_menu = tk.OptionMenu(frame, harmonics_var, *harmonics_options)
    option_menu.grid(row=row + 1, column=column + 3, sticky="NW", padx=10)

def phase_controls(
        frame: tk.Frame,
        row: int,
        column: int,
        text: str,
        initial_value: int
):
    
    def update_phase(value: str):

        value = int(value)
        # Create a packet with the command and the phase
        # 0x53 is the ASCII code for 'S' and 0x50 is the ASCII code for 'P'
        packet = bytes([0x53, 0x50])
        packet += value.to_bytes(2)  # Convert the phase to a 2-byte array and append it to the packet  
        logging.debug(packet.hex('|'))
        
        if "ser" in globals():
            ser.write(packet) # Send the command to the Arduino
            check_response(packet)
    
    def update_slider(*args):
        try:
            phase.set(int(phase_entry_value.get()))
            update_phase(phase.get())
        except ValueError:
            pass

    phase_label = tk.Label(frame, text=text)
    phase_label.grid(row=row, column=column + 2)
    phase_label.config(font=("Arial", 12, "bold"))

    phase = tk.DoubleVar(value=initial_value) 

    phase_entry_value = tk.StringVar()
    phase_entry_value.set(f"{initial_value}")
    phase_entry_value.trace_add("write", update_slider)

    phase_entry = tk.Entry(
        frame, 
        textvariable=phase_entry_value, 
        width=5
    )
    phase_entry.grid(row=row + 1, column=column, sticky="E")

    units_label = tk.Label(frame, text="°")
    units_label.grid(row=row + 1, column=column + 1, sticky="W")
    units_label.config(font=("Arial", 11))

    phase_slider = tk.Scale(
        frame,
        from_=0,
        to=360,
        orient=tk.HORIZONTAL,
        length=300,
        sliderlength=20,
        tickinterval=45,
        cursor="hand2",
        command=update_phase,
        variable=phase
    )

    phase_slider.grid(row=row + 1, column=column + 2)
    phase_slider.set(initial_value)  # Set the initial value of the slider

def signal_on_off_controls(
    frame: tk.Frame,
    text: str,
    row: int,
    column: int,
    id: str

):
    
    def signal_status_changed(*args):

        # Create a packet with the command and the signal status
        # 0x53 is the ASCII code for 'S' and 0x4F is the ASCII code for 'O'
        packet = bytes([0x53, 0x4F]) 
        match id.casefold():
            case "u1":
                packet += bytes([0x00])  
            case "u2":
                packet += bytes([0x01])  
            case "u3":
                packet += bytes([0x02])  
            case "un":
                packet += bytes([0x03])  
            case "i1":
                packet += bytes([0x04])  
            case "i2":
                packet += bytes([0x05])  
            case "i3":
                packet += bytes([0x06])  
            case "in":
                packet += bytes([0x07])  

        if radio_var.get() == "On":
            packet += bytes([0x01])
        elif radio_var.get() == "Off":
            packet += bytes([0x00])

        logging.debug(packet.hex('|'))  
        
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

def main():

    root = tk.Tk()
    
    root.title('4Cs4Vs Test Bench GUI')

    menu(root)

    # Create a frame for the GUI
    frame = tk.Frame(root)
    frame.pack()

    frame.columnconfigure(0, minsize=50)
    frame.columnconfigure(1, minsize=40)
    frame.columnconfigure(2, minsize=180)
    frame.columnconfigure(5, minsize=70)

    amplitude_controls(frame, row=0, column=0)
    frequency_controls(frame, row=2, column=0)
    harmonics_controls(frame, row=4, column=0)
    
    phase_controls(
        frame=frame,
        row=6,
        column=0,
        text="First Phase Angle (°):",
        initial_value=0
    )

    phase_controls(
        frame=frame,
        row=8,
        column=0,
        text="Second Phase Angle (°):",
        initial_value=120
    )

    phase_controls(
        frame=frame,
        row=10,
        column=0,
        text="Third Phase Angle (°):",
        initial_value=240
    )

    control_signals_start_row = 1
    control_signals_start_column = 6

    output_label = tk.Label(frame, text="Control output signals:")
    output_label.grid(row=0, column=6)
    output_label.config(font=("Arial", 12, "bold"))

    signal_on_off_controls(
        frame, 
        "First phase voltage (u1)", 
        control_signals_start_row, 
        control_signals_start_column, 
        "u1"
    )

    signal_on_off_controls(
        frame, 
        "Second phase voltage (u2)", 
        control_signals_start_row + 1, 
        control_signals_start_column, 
        "u2"
    )

    signal_on_off_controls(
        frame, 
        "Third phase voltage (u3)", 
        control_signals_start_row + 2, 
        control_signals_start_column, 
        "u3"
    )

    signal_on_off_controls(
        frame, 
        "Neutral voltage (uN)", 
        control_signals_start_row + 3, 
        control_signals_start_column, 
        "uN"
    )

    signal_on_off_controls(
        frame, 
        "First phase current (i1)", 
        control_signals_start_row + 4, 
        control_signals_start_column, 
        "i1"
    )

    signal_on_off_controls(
        frame, 
        "Second phase current (i2)", 
        control_signals_start_row + 5, 
        control_signals_start_column, 
        "i2"
    )

    signal_on_off_controls(
        frame, 
        "Third phase current (i3)", 
        control_signals_start_row + 6, 
        control_signals_start_column, 
        "i3"
    )

    signal_on_off_controls(
        frame, 
        "Neutral current (iN)", 
        control_signals_start_row + 7, 
        control_signals_start_column, 
        "iN"
    )


    root.mainloop()

main()