import tkinter as tk
# import serial
from math import sqrt

# Create a serial connection to the Arduino Portenta H7
# ser = serial.Serial('COM7', 115200)  # Replace 'COM1' with the appropriate serial port

def round_half_up(float_number: float) -> int:

    if float_number >= 0: return int(float_number + 0.5)
    else: return int(float_number - 0.5)

# Function to send control parameters to the Arduino
def update_amplitude(value, rms_label):

    amplitude = round_half_up(float(value)*6553.5)
    rms = round(float(value) / sqrt(2), 3)
    rms_label.config(text=f"RMS: {rms} V")

    # Create a packet with the command and the amplitude
    # 0x53 is the ASCII code for 'S' and 0x41 is the ASCII code for 'A'
    packet = bytes([0x53, 0x41])
    packet += amplitude.to_bytes(2)  # Convert the amplitude to a 2-byte array and append it to the packet  
    print(packet.hex(' '))
    # ser.write(packet)  # Send the command to the Arduino

def update_frequency(value):

    frequency = round_half_up(float(value)*3.8)

    # Create a packet with the command and the frequency
    # 0x53 is the ASCII code for 'S' and 0x46 is the ASCII code for 'F'
    packet = bytes([0x53, 0x46])
    packet += frequency.to_bytes(2)  # Convert the frequency to a 2-byte array and append it to the packet
    print(packet.hex(' '))
    # ser.write(packet)  # Send the command to the Arduino

def update_harmonics(value, harmonics_var: tk.StringVar):
    
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
        print(packet.hex(' '))
        # ser.write(packet)  # Send the command to the Arduino

def harmonic_changed(
        *args,
        harmonics_var: tk.StringVar,
        harmonics_slider: tk.Scale
):
    update_harmonics(
        harmonics_slider.get(),
        harmonics_var
    )

def signal_status_changed(
        *args,
        radio_var: tk.StringVar,
        id: str
):
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

    print(packet.hex(' '))        
                 
def amplitude_slider(frame: tk.Frame):
    
    amplitude_label = tk.Label(frame, text="Amplitude (V):")
    amplitude_label.grid(row=0, column=0)
    amplitude_label.config(font=("Arial", 12, "bold"))

    rms_label = tk.Label(frame, text="RMS: 0.000 V")
    rms_label.grid(row=1, column=1, sticky="W", padx=10, pady=10)
    rms_label.config(font=("Arial", 9, "bold"))

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
                                command=lambda value: update_amplitude(
                                    value, 
                                    rms_label
                                )
    )
    amplitude_slider.grid(row=1, column=0)
    amplitude_slider.set(1)  # Set the initial value of the slider

def frequency_slider(frame: tk.Frame):

    frequency_label = tk.Label(frame, text="Frequency (Hz):")
    frequency_label.grid(row=2, column=0)
    frequency_label.config(font=("Arial", 12, "bold"))

    frequency_slider = tk.Scale(frame,
                                from_=0,
                                to=100,
                                orient=tk.HORIZONTAL,
                                length=300,
                                sliderlength=20,
                                tickinterval=10,
                                cursor="hand2",
                                command=update_frequency)
    frequency_slider.grid(row=3, column=0)
    frequency_slider.set(50)  # Set the initial value of the slider

def harmonics_controls(frame: tk.Frame):

    harmonics_label = tk.Label(frame, text="Number of Harmonics:")
    harmonics_label.grid(row=4, column=0)
    harmonics_label.config(font=("Arial", 12, "bold"))

    # Create a Tkinter variable
    harmonics_var = tk.StringVar(frame)
    # Define the options
    harmonics_options = {"Even", "Odd", "Both"}
    # Set the default option
    harmonics_var.set("Even")

    harmonics_slider = tk.Scale(
                                frame,
                                from_=0,
                                to=50,
                                orient=tk.HORIZONTAL,
                                length=300,
                                sliderlength=20,
                                tickinterval=10,
                                cursor="hand2",
                                command=lambda value: update_harmonics(
                                    value,
                                    harmonics_var
                                )
    )
    harmonics_slider.grid(row=5, column=0)
    harmonics_slider.set(0)  # Set the initial value of the slider

    parity_label = tk.Label(frame, text="Harmonics\nParity:")
    parity_label.grid(row=4, column=1, sticky="SW", padx=10)
    parity_label.config(font=("Arial", 11, "bold"))
    
    harmonics_var.trace_add('write', lambda *args: harmonic_changed(
        *args,
        harmonics_var=harmonics_var,
        harmonics_slider=harmonics_slider
    ))
    # Create the dropdown menu
    option_menu = tk.OptionMenu(frame, harmonics_var, *harmonics_options)
    option_menu.grid(row=5, column=1, sticky="NW", padx=10)

def signal_on_off(
          frame: tk.Frame,
          text: str,
          row: int,
          column: int,
          id: str

):
     
    signal_label = tk.Label(frame, text=text)
    signal_label.grid(row=row, column=3, sticky="W")
    signal_label.config(font=("Arial", 9))
    frame.rowconfigure(row, minsize=50)

    # Create a Tkinter variable
    radio_var = tk.StringVar()
    # Trace the variable
    radio_var.trace_add('write', lambda *args: signal_status_changed(
        *args,
        radio_var=radio_var,
        id = id
    ))

    # Create the "On" radio button
    on_button = tk.Radiobutton(
        frame, 
        text="On", 
        variable=radio_var, 
        value="On"
    )
    on_button.grid(row=row, column=4)

    # Create the "Off" radio button
    off_button = tk.Radiobutton(
        frame, 
        text="Off", 
        variable=radio_var, 
        value="Off"
    )
    off_button.grid(row=row, column=5, sticky="W")

    frame.columnconfigure(5, minsize=70)

    # Set the default state
    radio_var.set("On")

def main():

    root = tk.Tk()
    
    root.title('4Cs4Vs Test Bench GUI')

    # Create a frame for the GUI
    frame = tk.Frame(root)
    frame.pack()

    amplitude_slider(frame)
    frequency_slider(frame)
    harmonics_controls(frame)

    frame.columnconfigure(1, minsize=180)

    output_label = tk.Label(frame, text="Control output signals:")
    output_label.grid(row=0, column=3)
    output_label.config(font=("Arial", 12, "bold"))

    signal_on_off(frame, "First phase voltage (u1)", 1, 3, "u1")
    signal_on_off(frame, "Second phase voltage (u2)", 2, 3, "u2")
    signal_on_off(frame, "Third phase voltage (u3)", 3, 3, "u3")
    signal_on_off(frame, "Neutral voltage (uN)", 4, 3, "uN")
    signal_on_off(frame, "First phase current (i1)", 5, 3, "i1")
    signal_on_off(frame, "Second phase current (i2)", 6, 3, "i2")
    signal_on_off(frame, "Third phase current (i3)", 7, 3, "i3")
    signal_on_off(frame, "Neutral current (iN)", 8, 3, "iN")

    root.mainloop()

main()