FROM python:3.9-slim

WORKDIR /app

COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install cron
RUN apt-get update && apt-get install -y cron

# Copy the crontab file to the cron directory
COPY crontab /etc/cron.d/model-cron

# Give cron file the correct permissions
RUN chmod 0644 /etc/cron.d/model-cron

# Apply the cron job
RUN crontab /etc/cron.d/model-cron

# Start cron and keep the container running
CMD cron && tail -f /var/log/cron.log
