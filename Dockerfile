# Use Python 3.9 as the base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements file
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY ./reports /app/reports
COPY ./main.py /app/main.py
COPY ./sms.py /app/sms.py
COPY ./requirements.txt /app/requirements.txt

# Expose the port Flask runs on
EXPOSE 8080

# Command to run the app
CMD ["python", "sms.py"]
