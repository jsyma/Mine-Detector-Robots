# Rover Mine Exploration Simulator

This project focuses on developing rovers (clients) capable of detecting and mapping mines and correctly handling either the disarming or explosions upon encountering a mine. The system is designed to explore different communication methods between the client and the server, specifically: gRPC, RabbitMQ and FastAPI. 

## Table of Contents 
- [gRPC](#gRPC)

## gRPC
- Enables communications between rovers and server using a Protocol Buffer Definition File (.proto) to define the service and messages used for communication. 

#### To run the program:
1. **Navigate to gRPC Directory and Install Packages from `requirements.txt`**
   - ```
     cd /path/to/project
     ```
   - ```
     pip install -r requirements.txt
     ```

2. **Compile the Proto Buffer File**
   - ```
     python generate_proto.py
     ```

3. **Run the Server**
   - ```
     python server.py
     ```

4. **Run the Client**
   -```
     python client.py <rover_id>
     ```