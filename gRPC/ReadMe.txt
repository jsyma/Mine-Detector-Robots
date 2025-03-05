Steps to Run Program:
1. Install Packages from Requirements.txt
    - cd to project 
    - pip install -r requirements.txt
2. Compile the Proto Buffer File
    - python generate_proto.py
3. Run the Server 
    - python server.py
4. Run the Client 
    - Specify which rover ID you want to run it for 
    - python client.py <rover_id>
    - Ex: python client.py 2