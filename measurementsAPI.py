from flask import Flask, request, jsonify, render_template, send_from_directory
import csv
import os
import datetime
import hashlib
import numpy as np
import requests
import matplotlib
import pandas as pd

matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)

CSV_DIRECTORY = 'csv_files'
GRAPH_DIRECTORY = 'graphs'
if not os.path.exists(CSV_DIRECTORY):
    os.makedirs(CSV_DIRECTORY)
if not os.path.exists(GRAPH_DIRECTORY):
    os.makedirs(GRAPH_DIRECTORY)

CSV_FILE_PATH = None
file_open = False
arduino_server_url = '<Insert the ip of the arduino here>' # 'http://192.168.87.144'

def get_timestamped_file_path(measurement_name):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(CSV_DIRECTORY, f'{measurement_name}_{timestamp}.csv')

def create_graph(filename):
    file_path = os.path.join(CSV_DIRECTORY, filename)
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist")
        return None

    loads = []
    positions = []

    with open(file_path, mode='r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            loads.append(float(row[0]))
            positions.append(float(row[1]))

    plt.figure(figsize=(8, 6))
    plt.plot(loads, positions, marker='o', linestyle='-', color='b')
    plt.xlabel('Load')
    plt.ylabel('Position')
    plt.title(f'Measurements from {filename}')
    plt.grid(True)
    
    graph_filename = hashlib.md5(filename.encode()).hexdigest() + '.png'
    graph_path = os.path.join(GRAPH_DIRECTORY, graph_filename)
    plt.savefig(graph_path)
    plt.close()
    
    print(f"Graph saved as {graph_path}")
    return graph_filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/listcsv', methods=['GET'])
def list_csv_files():
    csv_files = [f for f in os.listdir(CSV_DIRECTORY) if f.endswith('.csv')]
    return jsonify(csv_files)

@app.route('/view/<filename>')
def view_file(filename):
    graph_filename = create_graph(filename)
    return render_template('view.html', filename=filename, graph_filename=graph_filename)

@app.route('/data/<filename>', methods=['GET'])
def get_file_data(filename):
    file_path = os.path.join(CSV_DIRECTORY, filename)
    measurements = []
    if os.path.exists(file_path):
        with open(file_path, mode='r') as file:
            reader = csv.reader(file)
            next(reader)
            measurements = [row for row in reader]
    return jsonify(measurements)

@app.route('/startrecording', methods=['POST'])
def start_recording():
    global CSV_FILE_PATH, file_open
    data = request.get_json()
    measurement_name = data.get('measurement_name', 'measurement_data')
    CSV_FILE_PATH = get_timestamped_file_path(measurement_name)
    with open(CSV_FILE_PATH, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Load", "Position"])
    file_open = True
    return jsonify({"status": "success", "message": f"Recording started, saving to {CSV_FILE_PATH}"}), 200

@app.route('/add', methods=['POST'])
def add_data():
    global file_open

    if not file_open:
        return jsonify({"status": "error", "message": "No recording session is active"}), 400

    data = request.get_json()

    if 'loads' in data and 'positions' in data:
        loads = data['loads']
        positions = data['positions']

        if len(loads) == len(positions):
            with open(CSV_FILE_PATH, mode='a', newline='') as file:
                writer = csv.writer(file)
                for load, position in zip(loads, positions):
                    writer.writerow([load, position])

            return jsonify({"status": "success", "message": "Data received"}), 200
        else:
            return jsonify({"status": "error", "message": "Mismatched array lengths"}), 400
    else:
        return jsonify({"status": "error", "message": "Invalid data format"}), 400

@app.route('/stoprecording', methods=['POST'])
def stop_recording():
    global file_open
    if file_open:
        file_open = False
        return jsonify({"status": "success", "message": "Recording stopped"}), 200
    else:
        return jsonify({"status": "error", "message": "No recording session is active"}), 400

@app.route('/triggerMeasurement', methods=['GET'])
def trigger_measurement():
    try:
        response = requests.post(f'{arduino_server_url}:80/triggerMeasurement')
        if response.status_code == 200:
            return jsonify({"status": "success", "message": "Measurement started on Arduino server"}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to trigger measurement on Arduino server"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message": f"Failed to connect to Arduino server: {str(e)}"}), 500

@app.route('/processcsv/<filename>', methods=['POST'])
def process_csv(filename):
    # Path to the CSV file
    file_path = os.path.join(CSV_DIRECTORY, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    
    # Read CSV file
    df = pd.read_csv(file_path)

    # Filter data where load is greater than 330
    filtered_df = df[df['Load'] > 330]

    if filtered_df.empty:
        return jsonify({"error": "No data points above threshold"}), 400

    # Perform linear fit
    x = filtered_df['Load']
    y = filtered_df['Position']
    coeffs = np.polyfit(x, y, 1)
    k_value = coeffs[0]

    # Plot the data and linear fit
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, label='Data Points')
    plt.plot(x, coeffs[0] * x + coeffs[1], color='red', label=f'Linear Fit (k = {k_value:.2f})')
    plt.ylabel('Position')
    plt.xlabel('Load')
    plt.title('Load vs Position with Linear Fit')
    plt.legend()

    # Save the plot as a PNG file
    graph_filename = f"{filename.split('.')[0]}_graph.png"
    graph_filepath = os.path.join(GRAPH_DIRECTORY, graph_filename)
    plt.savefig(graph_filepath)
    plt.close()

    return jsonify({"k_value": k_value, "graph_filename": graph_filename})


@app.route('/graphs/<filename>')
def get_graph(filename):
    GRAPH_DIRECTORY = r'C:\Users\TRD\Desktop\Projekti\TerraScout\Penetrometer Code\Analysis of mesurements\graphs'
    try:
        
        return send_from_directory(GRAPH_DIRECTORY, filename)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/moveUp', methods=['POST'])
def move_up():
    try:
        response = requests.post(f'{arduino_server_url}:80/moveUp')
        if response.status_code == 200:
            return jsonify({"status": "success", "message": "Moved up by 5mm"}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to move up on Arduino server"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message": f"Failed to connect to Arduino server: {str(e)}"}), 500

@app.route('/moveDown', methods=['POST'])
def move_down():
    try:
        response = requests.post(f'{arduino_server_url}:80/moveDown')
        if response.status_code == 200:
            return jsonify({"status": "success", "message": "Moved down by 5mm"}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to move down on Arduino server"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message": f"Failed to connect to Arduino server: {str(e)}"}), 500

@app.route('/returnToZero', methods=['POST'])
def return_to_zero():
    try:
        response = requests.post(f'{arduino_server_url}:80/returnToZero')
        if response.status_code == 200:
            return jsonify({"status": "success", "message": "Returned to zero position"}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to return to zero position on Arduino server"}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message": f"Failed to connect to Arduino server: {str(e)}"}), 500

@app.route('/deletecsv/<filename>', methods=['DELETE'])
def delete_csv_file(filename):
    try:
        file_path = os.path.join(CSV_DIRECTORY, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({"status": "success", "message": f"Deleted file '{filename}'"}), 200
        else:
            return jsonify({"status": "error", "message": f"File '{filename}' not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
