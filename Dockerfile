FROM python:3.9

RUN apt-get update
RUN apt-get -y install gcc

EXPOSE 5000/tcp

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY req.txt .

# Install any dependencies
RUN pip install -r req.txt

# Copy the content of the local src directory to the working directory
COPY . .

# Specify the command to run on container start
ENTRYPOINT [ "streamlit", "run" ]
CMD [ "app.py", "--server.headless", "true", "--server.fileWatcherType", "none", "--browser.gatherUsageStats", "false","--server.enableCORS","false","--server.enableWebsocketCompression","false"]