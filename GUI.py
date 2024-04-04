import tkinter as tk
import serial
import logging
from serial.tools import list_ports
from math import sqrt


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
                
                amplitude_slider.set(str(amplitude1))
                phase_slider.set(str(phase1))
                frequency_slider.set(str(frequency1))
                harmonics_slider.set(str(harmonics1["count"]))
                harmonics_var.set(harmonics1["type"])

            case "2nd": 
                
                phase_id = 2
                
                amplitude_slider.set(str(amplitude2))
                phase_slider.set(str(phase2))
                frequency_slider.set(str(frequency2))
                harmonics_slider.set(str(harmonics2["count"]))
                harmonics_var.set(harmonics2["type"])

            case "3rd": 
                
                phase_id = 3
                
                amplitude_slider.set(str(amplitude3))
                phase_slider.set(str(240))
                frequency_slider.set(str(frequency3))
                harmonics_slider.set(str(harmonics3["count"]))
                harmonics_var.set(harmonics3["type"])
        
        logging.debug(f"Phase: {phase_id}")

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

def amplitude_controls(
    row: int,
    column: int,
    text: str = "Amplitude (V):"
):
    
    global amplitude_slider
    global amplitude_entry
    global amplitude1, amplitude2, amplitude3

    amplitude1 = 1; amplitude2 = 1; amplitude3 = 1    
    # Function to send control parameters to the Arduino
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
        logging.debug(packet.hex('|'))
        
        if "ser" in globals():
            ser.write(packet) # Send the command to the Arduino
            check_response(packet)

        match phase_id:
            case 1: amplitude1 = float(value)
            case 2: amplitude2 = float(value)
            case 3: amplitude3 = float(value)
    
    def update_slider(*args):

        try:
            if amplitude_entry_value.get() == "": return
            amplitude_var.set(float(amplitude_entry_value.get()))
            update_amplitude(amplitude_var.get(), clear_entry=False)

        except ValueError as e:
            logging.error(e)

    amplitude_label = tk.Label(frame, text=text)
    amplitude_label.grid(row=row, column=column, sticky="W")
    amplitude_label.config(font=("Arial", 10, "bold"))

    amplitude_var = tk.DoubleVar(value=1) 

    amplitude_entry_value = tk.StringVar()
    amplitude_entry_value.set("1")
    # amplitude_entry_value.trace_add("write", update_slider)
    amplitude_entry = tk.Entry(
        frame, 
        textvariable=amplitude_entry_value, 
        width=5
    )
    amplitude_entry.grid(row=row, column=column + 1, sticky="E")

    amplitude_entry.bind("<Return>", update_slider)
    amplitude_entry.bind("<FocusOut>", update_slider)

    units_label = tk.Label(frame, text="V")
    units_label.grid(row=row, column=column + 2, sticky="W")
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
        variable=amplitude_var
    )
    
    amplitude_slider.grid(row=row, column=column + 3, sticky="E")
    amplitude_slider.set(1)  # Set the initial value of the slider

    rms_label = tk.Label(frame, text="RMS: 1.000 V")
    rms_label.grid(row=row, column=column + 4, sticky="W", padx=10, pady=10)
    rms_label.config(font=("Arial", 9, "bold"))

def frequency_controls(
        row: int,
        column: int
):

    global frequency_slider
    global frequency1, frequency2, frequency3

    frequency1 = 50; frequency2 = 50; frequency3 = 50

    def update_frequency(value):

        global frequency1, frequency2, frequency3

        frequency = round_half_up(float(value)*3.8)

        # Create a packet with the command and the frequency
        # 0x53 is the ASCII code for 'S' and 0x46 is the ASCII code for 'F'
        packet = bytes([0x53, 0x46, phase_id])
        packet += frequency.to_bytes(2)  # Convert the frequency to a 2-byte array and append it to the packet
        logging.debug(packet.hex('|'))

        if "ser" in globals():
            ser.write(packet) # Send the command to the Arduino
            check_response(packet)

        match phase_id:
            case 1: frequency1 = int(value)
            case 2: frequency2 = int(value)
            case 3: frequency3 = int(value)
    
    def update_slider(*args):
        try:
            frequency.set(float(frequency_entry_value.get()))
            update_frequency(frequency.get())
        except ValueError:
            pass

    frequency_label = tk.Label(frame, text="Frequency (Hz):")
    frequency_label.grid(row=row, column=column, sticky="W")
    frequency_label.config(font=("Arial", 10, "bold"))

    frequency = tk.DoubleVar(value=1) 

    frequency_entry_value = tk.StringVar()
    frequency_entry_value.set("50")
    frequency_entry_value.trace_add("write", update_slider)
    frequency_entry = tk.Entry(
        frame, 
        textvariable=frequency_entry_value, 
        width=5
    )
    frequency_entry.grid(row=row, column=column + 1, sticky="E")

    units_label = tk.Label(frame, text="Hz")
    units_label.grid(row=row, column=column + 2, sticky="W")
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
    frequency_slider.grid(row=row, column=column + 3)
    frequency_slider.set(50)  # Set the initial value of the slider

def harmonics_controls(
        row: int,
        column: int
):
    
    global harmonics_slider
    global harmonics_var
    global harmonics1, harmonics2, harmonics3

    harmonics1 = {"count": 1, "type": "Odd"}
    harmonics2 = {"count": 1, "type": "Odd"}
    harmonics3 = {"count": 1, "type": "Odd"}
    
    def update_harmonics(value):

        global harmonics1, harmonics2, harmonics3
    
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
        logging.debug(packet.hex('|'))
        
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

    def harmonic_changed(*args):
        
        update_harmonics(harmonics_slider.get())

    def update_slider(*args):
        try:
            harmonic.set(float(harmonic_entry_value.get()))
            update_harmonics(harmonic.get())
        except ValueError:
            pass

    harmonics_label = tk.Label(frame, text="Harmonics Order:")
    harmonics_label.grid(row=row, column=column, sticky="W")
    harmonics_label.config(font=("Arial", 10, "bold"))

    # Create a Tkinter variable
    harmonics_var = tk.StringVar(frame)
    # Define the options
    harmonics_options = [
        "Even", 
        "Odd", 
        "Triplen",
        "Non-Triplen Odd",
        "Positive Sequence",
        "Negative Sequence",
        "Zero Sequence"
    ]

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
    amplitude_entry.grid(row=row, column=column + 1, sticky="E")

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
    harmonics_slider.grid(row=row, column=column + 3)
    harmonics_slider.set(1)  # Set the initial value of the slider

    type_label = tk.Label(frame, text="Harmonics Type:")
    type_label.grid(row=row + 1, column=column, sticky="W", padx=10)
    type_label.config(font=("Arial", 10, "bold"))
    
    harmonics_var.trace_add('write', harmonic_changed)
    # Create the dropdown menu
    option_menu = tk.OptionMenu(frame, harmonics_var, *harmonics_options)
    option_menu.grid(row=row + 1, column=column + 1, sticky="W", padx=10)

def phase_controls(
        row: int,
        column: int
):
    
    global phase_slider
    global phase1, phase2, phase3
    
    phase1 = 0; phase2 = 120; phase3 = 240
    
    def update_phase(value: str):

        global phase1, phase2, phase3

        phase_factor = int(value)/360
        #
        # Create a packet with the command and the phase factor
        # 0x53 is the ASCII code for 'S' and 0x50 is the ASCII code for 'P'
        packet = bytes([0x53, 0x50, phase_id])
        # packet += value.to_bytes(2)  # Convert the phase to a 2-byte array and append it to the packet  
        logging.debug(packet.hex('|'))
        
        if "ser" in globals():
            ser.write(packet) # Send the command to the Arduino
            check_response(packet)
        
        match phase_id:
            case 1: phase1 = int(value)
            case 2: phase2 = int(value)
            case 3: phase3 = int(value)

    def update_slider(*args):
      
        try:
            phase.set(int(phase_entry_value.get()))
            update_phase(phase.get())
        except ValueError:
            pass

    phase_label = tk.Label(frame, text="Phase Angle (°):")
    phase_label.grid(row=row, column=column, sticky="W")
    phase_label.config(font=("Arial", 10, "bold"))

    phase = tk.DoubleVar(value=phase1) 

    phase_entry_value = tk.StringVar()
    phase_entry_value.set(f"{phase1}")
    phase_entry_value.trace_add("write", update_slider)

    phase_entry = tk.Entry(
        frame, 
        textvariable=phase_entry_value, 
        width=5
    )
    phase_entry.grid(row=row, column=column + 1, sticky="E")

    units_label = tk.Label(frame, text="°")
    units_label.grid(row=row, column=column + 2, sticky="W")
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

    phase_slider.grid(row=row, column=column + 3)
    phase_slider.set(phase1)  # Set the initial value of the slider

def signal_on_off_controller(
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

def on_frame_click(event):
    
    frame.focus_force()

def main():

    global frame

    logging.basicConfig(level=logging.DEBUG, style='{', format='{levelname}: {message}')

    root = tk.Tk()
    root.title('4Cs4Vs Test Bench GUI')

    menu(root)

    # Create a frame for the GUI
    frame = tk.Frame(root)
    frame.pack()
    frame.bind("<Button-1>", on_frame_click)

    # frame.columnconfigure(0, minsize=50)
    # frame.columnconfigure(1, minsize=40)
    # frame.columnconfigure(2, minsize=180)
    # frame.columnconfigure(5, minsize=70)

    amplitude_controls_column = 0

    phase_selector(
        row=0, 
        column=0
    )

    amplitude_controls(
        row=1, 
        column=amplitude_controls_column, 
        text="Amplitude (V):"
    )
    
    frequency_controls(row=2, column=0)

    phase_controls(
        row=3,
        column=0
    )

    harmonics_controls(row=4, column=0)
    
    signal_on_off_controls(
        control_signals_start_row = 0, 
        control_signals_start_column = 11
    )

    root.mainloop()

main()