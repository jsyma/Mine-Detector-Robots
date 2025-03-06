Steps to Run the Program (Windows): 
1. Install Chocolatey
  - Open PowerShell and Run as Administrator
  - run: Set-ExecutionPolicy Bypass -Scope Process -Force;
  - run: Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
2. Install RabbitMQ 
  - choco install rabbitmq
3. Install Docker Desktop 
4. Run RabbitMQ using Docker 
  - docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management
5. Install Packages from Requirements.txt
  - cd to project
  - pip install -r requirements.txt
6. Compile the Proto Buffer File 
  - python generate_proto.py
7. Run the Server in one terminal
  - python server.py 
8. Run the Client in another terminal 
  - python client.py (prompted to enter Rover ID)
9. Run the Deminer in a third terminal
  - python deminer.py (prompted to enter Deminer ID)
10. Open RabbitMQ Management Console at 'localhost:15672'
  - Login Credentials: username/password 'guest'