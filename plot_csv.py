import pandas as pd
import matplotlib.pyplot as plt
import os

csv_file_path = os.path.join(os.getcwd(), 'csv', '3phase.csv')
# Read the CSV file
data = pd.read_csv(csv_file_path)

# # Plot the data
plt.plot(
    data['time_s'], data['1_V'], 
    data['time_s'], data['2_V'], 
    data['time_s'], data['3_V']
)
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Data Plot')
plt.show()