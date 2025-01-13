# Use Python 3.9 as the base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements file
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

ENV OPENAI_API_ENDPOINT = "https://progress-tracking-dev-east-us.openai.azure.com/openai/deployments/gpt-4o-prig-dev/chat/completions?api-version=2024-08-01-preview"
ENV OPENAI_API_KEY = "3aac79231b2d402ea89f0d94d5cefec4"
ENV TWIL_ACCOUNT_SID = "AC5607ca505b69a91cfafe52310fe3bd05"
ENV TWIL_AUTH_TOKEN = "9f77c17db760e00676cfcd15a02451ed"
ENV TWIL_PHONE_NUMBER = "+12183665130"

# Copy the app code
COPY ./reports /app/reports
COPY ./main.py /app/main.py
COPY ./sms.py /app/sms.py
COPY ./requirements.txt /app/requirements.txt

# Expose the port Flask runs on
EXPOSE 5000

# Command to run the app
CMD ["python", "sms.py"]
