# Measurement API Project

## Setup Instructions

Follow these steps to set up and run the Measurement API project:

### 1. Create a Virtual Environment

First, create a virtual environment for the project:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt


Update ESP Server IP

In measurementAPI.py, replace the placeholder with the IP address of the ESP server:

    Row 25

    arduino_server_url = 'http://<YOUR_ESP_SERVER_IP>'

Replace <YOUR_ESP_SERVER_IP> with the actual IP address of your ESP server.
Update Graphs Directory Path

In measurementAPI.py, replace the placeholder with the absolute path to the graphs folder:

    Row 186:

    GRAPH_DIRECTORY = r'<YOUR_ABSOLUTE_PATH_TO_GRAPHS_FOLDER>'

Replace <YOUR_ABSOLUTE_PATH_TO_GRAPHS_FOLDER> with the absolute path to your graphs folder.


Make sure that you are connected to the same WiFi as the ESP32.
To run the aplication select the measurementAPI.py file in Visual Studio code and run code 