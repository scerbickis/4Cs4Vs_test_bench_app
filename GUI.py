import tkinter as tk
import serial
import logging
from math import sqrt

# Create a serial connection to the Arduino Portenta H7
# ser = serial.Serial('COM7', 115200)  # Replace 'COM1' with the appropriate serial port

logging.basicConfig(level=logging.DEBUG, style='{', format='{levelname}: {message}')

def round_half_up(float_number: float) -> int:

    if float_number >= 0: return int(float_number + 0.5)
    else: return int(float_number - 0.5)

# def check_response(request: bytes) -> bool:

#     response = ser.read(len(request))  # Read the response from the Arduino
#     if response == request: return True
#     else: logging.error(f"Error: received {response.hex('|')} instead of {request.hex('|')}")
     
                 
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
        # ser.write(packet)  # Send the command to the Arduino
        # check_response(packet)
    
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
        # ser.write(packet)  # Send the command to the Arduino
        # check_response(packet)
    
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

    frequency_slider = tk.Scale(frame,
                                from_=0,
                                to=100,
                                orient=tk.HORIZONTAL,
                                length=300,
                                sliderlength=20,
                                tickinterval=10,
                                cursor="hand2",
                                command=update_frequency,
                                variable=frequency)
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
            # 0x42 is the ASCII code for 'B'
            case "Both": packet += bytes([0x42]) 

        # Convert the harmonics to a 1-byte array and append it to the packet
        packet += harmonics.to_bytes(1)  
        logging.debug(packet.hex('|'))
        # ser.write(packet)  # Send the command to the Arduino
        # check_response(packet)
    
    def harmonic_changed(*args):
        
        update_harmonics(harmonics_slider.get())

    def update_slider(*args):
        try:
            harmonic.set(float(harmonic_entry_value.get()))
            update_harmonics(harmonic.get())
        except ValueError:
            pass

    harmonics_label = tk.Label(frame, text="Number of Harmonics:")
    harmonics_label.grid(row=row, column=column + 2)
    harmonics_label.config(font=("Arial", 12, "bold"))

    # Create a Tkinter variable
    harmonics_var = tk.StringVar(frame)
    # Define the options
    harmonics_options = {"Even", "Odd", "Both"}
    # Set the default option
    harmonics_var.set("Even")

    harmonic = tk.DoubleVar(value=1) 

    harmonic_entry_value = tk.StringVar()
    harmonic_entry_value.set("0")
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
    harmonics_slider.set(0)  # Set the initial value of the slider

    parity_label = tk.Label(frame, text="Harmonics\nParity:")
    parity_label.grid(row=row, column=column + 3, sticky="SW", padx=10)
    parity_label.config(font=("Arial", 11, "bold"))
    
    harmonics_var.trace_add('write', harmonic_changed)
    # Create the dropdown menu
    option_menu = tk.OptionMenu(frame, harmonics_var, *harmonics_options)
    option_menu.grid(row=row + 1, column=column + 3, sticky="NW", padx=10)

def signal_on_off(
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
                packet += bytes([0x55, 0x01])  # 0x55 is the ASCII code for 'U'
            case "u2":
                packet += bytes([0x55, 0x02])  # 0x55 is the ASCII code for 'U'
            case "u3":
                packet += bytes([0x55, 0x03])  # 0x55 is the ASCII code for 'U'
            case "un":
                packet += bytes([0x55, 0x04])  # 0x55 is the ASCII code for 'U'
            case "i1":
                packet += bytes([0x49, 0x01])  # 0x49 is the ASCII code for 'I'
            case "i2":
                packet += bytes([0x49, 0x02])  # 0x49 is the ASCII code for 'I'
            case "i3":
                packet += bytes([0x49, 0x03])  # 0x49 is the ASCII code for 'I'
            case "in":
                packet += bytes([0x49, 0x04])  # 0x49 is the ASCII code for 'I'

        if radio_var.get() == "On":
            packet += bytes([0x01])
        elif radio_var.get() == "Off":
            packet += bytes([0x00])

        logging.debug(packet.hex('|'))  
        # ser.write(packet)  # Send the command to the Arduino
        # check_response(packet) 
     
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

    # Create a frame for the GUI
    frame = tk.Frame(root)
    frame.pack()

    frame.columnconfigure(0, minsize=50)
    frame.columnconfigure(1, minsize=40)
    frame.columnconfigure(2, minsize=180)
    frame.columnconfigure(5, minsize=70)

    amplitude_controls(frame, 0, 0)
    frequency_controls(frame, 2, 0)
    harmonics_controls(frame, 4, 0)

    control_signals_start_row = 1
    control_signals_start_column = 6

    output_label = tk.Label(frame, text="Control output signals:")
    output_label.grid(row=0, column=6)
    output_label.config(font=("Arial", 12, "bold"))

    signal_on_off(
        frame, 
        "First phase voltage (u1)", 
        control_signals_start_row, 
        control_signals_start_column, 
        "u1"
    )

    signal_on_off(
        frame, 
        "Second phase voltage (u2)", 
        control_signals_start_row + 1, 
        control_signals_start_column, 
        "u2"
    )

    signal_on_off(
        frame, 
        "Third phase voltage (u3)", 
        control_signals_start_row + 2, 
        control_signals_start_column, 
        "u3"
    )

    signal_on_off(
        frame, 
        "Neutral voltage (uN)", 
        control_signals_start_row + 3, 
        control_signals_start_column, 
        "uN"
    )

    signal_on_off(
        frame, 
        "First phase current (i1)", 
        control_signals_start_row + 4, 
        control_signals_start_column, 
        "i1"
    )

    signal_on_off(
        frame, 
        "Second phase current (i2)", 
        control_signals_start_row + 5, 
        control_signals_start_column, 
        "i2"
    )

    signal_on_off(
        frame, 
        "Third phase current (i3)", 
        control_signals_start_row + 6, 
        control_signals_start_column, 
        "i3"
    )

    signal_on_off(
        frame, 
        "Neutral current (iN)", 
        control_signals_start_row + 7, 
        control_signals_start_column, 
        "iN"
    )


    root.mainloop()

main()