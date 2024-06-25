from django.test import TestCase

import smtplib

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('rentalsroca@gmail.com', 'doze kmwf ctjd rsba')
    server.quit()
    print("Successfully connected to the SMTP server.")
except Exception as e:
    print(f"Failed to connect to the SMTP server: {e}")
