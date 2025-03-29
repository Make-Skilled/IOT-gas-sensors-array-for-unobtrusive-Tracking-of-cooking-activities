import requests
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ThingSpeak configuration
CHANNEL_ID = "2854419"
API_URL = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feed.json"

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "kr4785543@gmail.com"
SMTP_PASSWORD = "qhuzwfrdagfyqemk"
ALERT_EMAIL = "sudheerthadikonda0605@gmail.com"

def send_alert_email(gas_value, temperature):
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = ALERT_EMAIL
        msg['Subject'] = "⚠️ High Gas Level Alert!"

        # Email body
        body = f"""
        ⚠️ WARNING: High Gas Level Detected!

        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Gas Level: {gas_value} ppm
        Temperature: {temperature}°C

        Please take immediate action:
        1. Ventilate the area
        2. Check for gas leaks
        3. Avoid any open flames
        4. Contact emergency services if needed

        This is an automated alert from your IoT Gas Monitoring System.
        """

        msg.attach(MIMEText(body, 'plain'))

        # Connect to SMTP server and send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

        print(f"Alert email sent successfully! Gas Level: {gas_value}")
        return True

    except Exception as e:
        print(f"Failed to send alert email: {str(e)}")
        return False

def monitor_gas_levels():
    last_alert_time = 0
    alert_cooldown = 300  # 5 minutes between alerts

    while True:
        try:
            # Fetch data from ThingSpeak
            response = requests.get(API_URL)
            if response.status_code != 200:
                print(f"Failed to fetch data: HTTP {response.status_code}")
                continue

            data = response.json()
            if not data.get('feeds'):
                print("No feeds found in response")
                continue

            # Get latest reading
            latest_feed = data['feeds'][-1]
            gas_value = float(latest_feed['field2'])  # field2 contains gas value
            temperature = float(latest_feed['field1'])  # field1 contains temperature

            print(f"Current readings - Gas: {gas_value} ppm, Temperature: {temperature}°C")

            # Check if gas value exceeds threshold and enough time has passed since last alert
            current_time = time.time()
            if gas_value > 500 and (current_time - last_alert_time) > alert_cooldown:
                if send_alert_email(gas_value, temperature):
                    last_alert_time = current_time

            # Wait before next check
            time.sleep(15)  # Check every 15 seconds

        except Exception as e:
            print(f"Error in monitoring loop: {str(e)}")
            time.sleep(30)  # Wait longer if there's an error

if __name__ == "__main__":
    print("Starting gas level monitoring...")
    try:
        monitor_gas_levels()
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    except Exception as e:
        print(f"Monitoring stopped due to error: {str(e)}")