# Set base image
FROM python:3.10

# Set project creator as maintainer
LABEL Michael Watson "mdwatson988@gmail.com"

# Listen on port 5000
EXPOSE 5000/tcp

# Set working directory in container
WORKDIR /task_tracker

# Copy dependencies file to working directory (so it can be installed before copying the remaining files to allow use of cached files when app is updated)
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy remaining files to working directory
COPY . .

# Set entrypoint and command to run app on container start
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]