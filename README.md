EdhithaUI

1. Introduction
EdhithaUI is a project that combines a React-based frontend with a Python backend. It is designed for creating a seamless user interface and backend services, providing an integrated approach to building web applications. The purpose of this documentation is to guide developers through the structure, setup, and usage of this repository.
2. Project Structure
The repository is organized as follows:

- backend: Contains Python files for backend API and logic.
- src: Houses the React frontend source code, including components and assets.
- static: Static files used in the application.
- package.json: Defines frontend dependencies.
3. Setup and Installation

Prerequisites
- Node.js and npm for frontend.
- Python 3.x and pip for backend.
- Git to clone the repository.
Installation Steps
1. Clone the repository:
   git clone https://github.com/Edhitha-Juniors/edhithaUI.git


  
4. Install frontend dependencies:


  npm install


4. Usage

Step 1: Start the Servers
To run both the frontend and backend servers simultaneously, use the following command in the project root directory:
npm run dev



This will:
Start the Python backend server on http://127.0.0.1:5000/.
Start the React frontend server on http://localhost:3000/.
Step 2: Connect the Drone
In the UI, click the Connect button to establish a connection with the drone.
By default, the connection is made using:



the_connection = mavutil.mavlink_connection('tcp:192.168.1.21:5760')




Step 3: Start Geotagging
Wait for the drone to reach the desired altitude.
Begin geotagging by enabling the feature in the UI.
As images start displaying:
Click on the required image.
Select a target in the enlarged image view.
The selected area will be cropped and displayed.
Step 4: Save the Target
Assign a name to the target and save it for further processing.
Step 5: Stop Geotagging
Important: When the drone reaches its last waypoint, stop geotagging by disabling the feature in the UI.
Step 6: Reposition and Drop Payload
Click on the Target button to reposition the drone.
Once repositioned, the drone will automatically drop the payload at the designated location.


TROUBLESHOOTING COMMON ISSUE

1. Dependency Errors
Ensure all dependencies listed in requirements.txt (for the backend) and package.json (for the frontend) are installed.
For the backend, use:
pip install -r requirements.txt

For the frontend, use:
npm install




2. Port Conflicts
Verify that the default ports (5000 for the backend and 3000 for the frontend) are not in use by other processes.
Use the following command to check and free up the ports if necessary:


lsof -i :<port_number>
kill <process_id>




3. MAVLink Command Issues
If MAVLink commands fail to execute and geotagging is active:
Check whether the UI and geotagging are using the same port.
Solution: Stop geotagging to free up the port for MAVLink commands.
4. Python Server Not Starting
Ensure all required Python dependencies are installed
5. Frontend Server Not Starting
Ensure npm install has been run successfully in the project root.
If there are errors, try deleting the node_modules folder and reinstalling:


rm -rf node_modules
npm install



6. Connectivity Issues
Verify that the drone is on the same network as the host machine.
Double-check the IP address and port used in the connection string

mavutil.mavlink_connection('tcp:192.168.1.21:5760')


7. Logs for Debugging
Check backend server logs for errors or exceptions.
For the frontend, check the browser console and terminal output for debugging information.

