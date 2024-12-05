# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application into the container
COPY . /app/

# Expose the port your application runs on
EXPOSE 8443

# Define environment variable for token and password files
ENV TOKEN_PATH=/app/token.txt
ENV PASSWORD_PATH=/app/password.txt

# Run the bot
CMD ["python3", "bot.py"]