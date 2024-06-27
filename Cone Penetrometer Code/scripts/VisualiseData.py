import pandas as pd
import matplotlib.pyplot as plt

# Provide the full path to the CSV file
csv_file_path = r'C:\Users\TRD\Desktop\stepper\scripts\measurements.csv'

# Read the CSV file line by line
with open(csv_file_path, 'r', encoding='latin-1') as file:
    lines = file.readlines()

# Extract only the numeric data
measurements = []
for line in lines:
    line = line.strip()
    if line.isdigit():
        measurements.append(int(line))

# Generate y-coordinates from 0 to 188
y_coordinates = list(range(189))  # 0 to 188 inclusive

# Ensure the number of measurements matches the number of y-coordinates
# If there are more measurements than 189, truncate the list
# If there are fewer, pad the list with the last measurement
if len(measurements) > 189:
    measurements = measurements[:189]
else:
    measurements += [measurements[-1]] * (189 - len(measurements))

# Plot the data
plt.figure(figsize=(10, 5))
plt.plot(y_coordinates, measurements, marker='o', linestyle='-', color='b')
plt.xlabel('Y Coordinate')
plt.ylabel('Measurement Value')
plt.title('Measurements Plot')
plt.grid(True)
plt.show()
