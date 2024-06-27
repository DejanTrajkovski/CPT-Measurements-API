# ESP-WROOM-32 Penetrometer Code

This code is designed to run on the ESP-WROOM-32 microcontroller to enable communication with the API server and execute the functions of the penetrometer.

## Prerequisites

Ensure all necessary libraries are installed on the ESP-WROOM-32 device. Refer to the ESP documentation for instructions on installing required libraries.

## Setup Instructions

1. **Modify `main.cpp`:**

   - **Row 8**: Set the SSID of your Wi-Fi network.
     ```cpp
     const char* ssid = "<YOUR_WIFI_SSID>";
     ```

   - **Row 9**: Set the password of your Wi-Fi network.
     ```cpp
     const char* password = "<YOUR_WIFI_PASSWORD>";
     ```

   - **Row 12**: Set the IP address of the measurements API server.
     ```cpp
     const char* server_ip = "<MEASUREMENTS_API_IP>";
     ```

   Replace `<YOUR_WIFI_SSID>`, `<YOUR_WIFI_PASSWORD>`, and `<MEASUREMENTS_API_IP>` with your actual Wi-Fi SSID, password, and the IP address of the measurements API server, respectively.

2. **Upload `main.cpp` to the Microcontroller:**

   Use the appropriate tools (such as the Arduino IDE or PlatformIO) to upload `main.cpp` to the ESP-WROOM-32 microcontroller.

3. **Monitor Serial Output:**

   After uploading the code, use the serial monitor to:

   - Track the successful connection to the Wi-Fi network.
   - Log the executions and ensure the code is functioning as expected.

## Additional Information

- Ensure that your Wi-Fi network is accessible and the credentials are correctly set.
- The IP address of the measurements API server should be reachable from the ESP-WROOM-32 device.

If you encounter any issues, check the serial monitor for error messages and verify the configurations in `main.cpp`.
