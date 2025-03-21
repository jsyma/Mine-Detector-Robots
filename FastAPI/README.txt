Steps to Run Program (Without Azure/Docker):
1. Run: 'uvicorn server:app --reload'

Steps to Run Program(With Azure and Docker):
1. Run: 'docker build -t <your-repository-name>.azurecr.io/myapp:latest .'
2. Run: 'docker push <your-repository-name>.azurecr.io/myapp:latest'
3. Access the Web App with the default/given domain 