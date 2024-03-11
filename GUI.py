import tkinter as tk
import serial
from math import sqrt

# Create a serial connection to the Arduino Portenta H7
# ser = serial.Serial('COM7', 115200)  # Replace 'COM1' with the appropriate serial port

def round_half_up(float_number: float) -> int:

    if float_number >= 0: return int(float_number + 0.5)
    else: return int(float_number - 0.5)

# Function to send control parameters to the Arduino
def update_amplitude(value):

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
        print(packet.hex(' '))
        # ser.write(packet)  # Send the command to the Arduino

def harmonic_changed(*args):
    update_harmonics(harmonics_slider.get())

# Create the GUI
root = tk.Tk()
# root.geometry("800x600") # Set the size of the window
root.title('4Cs4Vs Test Bench GUI')
# Create a frame for the GUI
frame = tk.Frame(root)
frame.pack()

amplitude_label = tk.Label(frame, text="Amplitude (V):")
amplitude_label.grid(row=0, column=0)

amplitude_slider = tk.Scale(frame,
                            from_=0,
                            to=10,
                            resolution=0.01,
                            orient=tk.HORIZONTAL,
                            length=300, 
                            sliderlength=20,
                            tickinterval=1,
                            cursor="hand2",
                            command=update_amplitude)
amplitude_slider.grid(row=1, column=0)
amplitude_slider.set(1)  # Set the initial value of the slider

rms_label = tk.Label(frame, text="RMS: 0.000 V")
rms_label.grid(row=1, column=1)

frequency_label = tk.Label(frame, text="Frequency (Hz):")
frequency_label.grid(row=2, column=0)

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

harmonics_label = tk.Label(frame, text="Number of Harmonics:")
harmonics_label.grid(row=4, column=0)

harmonics_slider = tk.Scale(frame,
                            from_=0,
                            to=50,
                            orient=tk.HORIZONTAL,
                            length=300,
                            sliderlength=20,
                            tickinterval=10,
                            cursor="hand2",
                            command=update_harmonics)
harmonics_slider.grid(row=5, column=0)
harmonics_slider.set(0)  # Set the initial value of the slider

harmonics_parity_label = tk.Label(frame, text="Harmonics Parity:")
harmonics_parity_label.grid(row=4, column=1)

# Create a Tkinter variable
harmonics_var = tk.StringVar(frame)
harmonics_var.trace_add('write', harmonic_changed)
# Define the options
harmonics_options = {"Even", "Odd", "Both"}
# Set the default option
harmonics_var.set("Even")
# Create the dropdown menu
harmonics_menu = tk.OptionMenu(frame, harmonics_var, *harmonics_options)
harmonics_menu.grid(row=5, column=1)


# Create a Tkinter variable
radio_var_u1 = tk.StringVar()

# Create the "On" radio button
on_button_u1 = tk.Radiobutton(frame, text="On", variable=radio_var_u1, value="On")
on_button_u1.grid(row=0, column=3, padx=5, pady=5)

# Create the "Off" radio button
off_button_u1 = tk.Radiobutton(frame, text="Off", variable=radio_var_u1, value="Off")
off_button_u1.grid(row=0, column=4, padx=5, pady=5)

# Set the default state
radio_var_u1.set("On")



# Create a Tkinter variable
radio_var_u2 = tk.StringVar()

# Create the "On" radio button
on_button_u2 = tk.Radiobutton(frame, text="On", variable=radio_var_u2, value="On")
on_button_u2.grid(row=1, column=3, padx=5, pady=5)

# Create the "Off" radio button
off_button_u2 = tk.Radiobutton(frame, text="Off", variable=radio_var_u2, value="Off")
off_button_u2.grid(row=1, column=4, padx=5, pady=5)

# Set the default state
radio_var_u2.set("On")



# Create a Tkinter variable
radio_var_u3 = tk.StringVar()

# Create the "On" radio button
on_button_u3 = tk.Radiobutton(frame, text="On", variable=radio_var_u3, value="On")
on_button_u3.grid(row=2, column=3, padx=5, pady=5)

# Create the "Off" radio button
off_button_u3 = tk.Radiobutton(frame, text="Off", variable=radio_var_u3, value="Off")
off_button_u3.grid(row=2, column=4, padx=5, pady=5)

# Set the default state
radio_var_u3.set("On")



# Create a Tkinter variable
radio_var_uN = tk.StringVar()

# Create the "On" radio button
on_button_uN = tk.Radiobutton(frame, text="On", variable=radio_var_uN, value="On")
on_button_uN.grid(row=3, column=3, padx=5, pady=5)

# Create the "Off" radio button
off_button_uN = tk.Radiobutton(frame, text="Off", variable=radio_var_uN, value="Off")
off_button_uN.grid(row=3, column=4, padx=5, pady=5)

# Set the default state
radio_var_uN.set("On")



# Create a Tkinter variable
radio_var_i1 = tk.StringVar()

# Create the "On" radio button
on_button_i1 = tk.Radiobutton(frame, text="On", variable=radio_var_i1, value="On")
on_button_i1.grid(row=4, column=3, padx=5, pady=5)

# Create the "Off" radio button
off_button_i1 = tk.Radiobutton(frame, text="Off", variable=radio_var_i1, value="Off")
off_button_i1.grid(row=4, column=4, padx=5, pady=5)

# Set the default state
radio_var_i1.set("On")



# Create a Tkinter variable
radio_var_i2 = tk.StringVar()

# Create the "On" radio button
on_button_i2 = tk.Radiobutton(frame, text="On", variable=radio_var_i2, value="On")
on_button_i2.grid(row=5, column=3, padx=5, pady=5)

# Create the "Off" radio button
off_button_i2 = tk.Radiobutton(frame, text="Off", variable=radio_var_i2, value="Off")
off_button_i2.grid(row=5, column=4, padx=5, pady=5)

# Set the default state
radio_var_i2.set("On")



# Create a Tkinter variable
radio_var_i3 = tk.StringVar()

# Create the "On" radio button
on_button_i3 = tk.Radiobutton(frame, text="On", variable=radio_var_i3, value="On")
on_button_i3.grid(row=6, column=3, padx=5, pady=5)

# Create the "Off" radio button
off_button_i3 = tk.Radiobutton(frame, text="Off", variable=radio_var_i3, value="Off")
off_button_i3.grid(row=6, column=4, padx=5, pady=5)

# Set the default state
radio_var_i3.set("On")



# Create a Tkinter variable
radio_var_iN = tk.StringVar()

# Create the "On" radio button
on_button_iN = tk.Radiobutton(frame, text="On", variable=radio_var_iN, value="On")
on_button_iN.grid(row=7, column=3, padx=5, pady=5)

# Create the "Off" radio button
off_button_iN = tk.Radiobutton(frame, text="Off", variable=radio_var_iN, value="Off")
off_button_iN.grid(row=7, column=4, padx=5, pady=5)

# Set the default state
radio_var_iN.set("On")

# Start the GUI event loop
root.mainloop()
