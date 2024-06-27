import serial
import csv

# Replace 'COM6' with your Arduino's serial port
serial_port = 'COM6'  # Adjust this to your specific port
baud_rate = 9600  # Ensure this matches the baud rate set in your Arduino code
output_file = 'measurements.csv'

def read_serial_data():
    try:
        ser = serial.Serial(serial_port, baud_rate)
    except serial.SerialException as e:
        print(f"Serial error: {e}")
        return
    except PermissionError as e:
        print(f"Permission error: {e}")
        return
    except Exception as e:
        print(f"Unexpected error: {e}")
        return
    
    try:
        with open(output_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            while True:
                try:
                    line = ser.readline().decode('latin-1').strip()
                    if line:
                        measurements = line.split(',')
                        if measurements[-1] == '':
                            measurements.pop()
                        writer.writerow(measurements)
                        print(f"Written to CSV: {measurements}")
                except UnicodeDecodeError as e:
                    print(f"Unicode decode error: {e}")
                    print(f"Raw data: {line}")
                except serial.SerialException as e:
                    print(f"Serial read error: {e}")
                    break
                except Exception as e:
                    print(f"Error reading/writing data: {e}")
                    break
    except IOError as e:
        print(f"File error: {e}")
    except Exception as e:
        print(f"Unexpected file error: {e}")

if __name__ == "__main__":
    read_serial_data()
