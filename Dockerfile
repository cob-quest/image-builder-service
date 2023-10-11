FROM docker:stable-dind

# Set up Python
RUN apk update && apk add --no-cache python3 python3-dev py3-pip

# Set symbolic link from python3 to python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Update pip and clean up cache to reduce image size
RUN pip3 install --upgrade pip
RUN rm -rf /var/cache/apk/*

# Set the working directory in the container
WORKDIR /usr/image_builder

# Copy your application code into the container
COPY ./ /usr/image_builder/

# Optionally, install Python packages using pip
RUN pip3 install --no-cache-dir -r requirements.txt

# Run the app
CMD ["python3", "src/app.py"]