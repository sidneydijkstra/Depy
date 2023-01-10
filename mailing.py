import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.request

class Mailer:
    def __init__(self, enable, server, port, email, password):
        self.enable = enable
        self.server = server
        self.port = port
        self.email = email
        self.password = password

    def send_email(self, from_addr, to_addr, subject, body, html=None):
        # Check if mail is active
        if not self.enable:
            return False

        # Create an SMTP connection object
        conn = smtplib.SMTP(self.server, self.port)

        # Start TLS for security
        conn.starttls()

        # Login to the account
        conn.login(self.email, self.password)

        # Create the email message
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = from_addr
        msg['To'] = to_addr

        # Create a MIMEText object with the message body
        text = MIMEText(body)

        # Add the MIMEText object to the MIMEMultipart message
        msg.attach(text)

        if html is not None:
            # Add the HTML content as an attachment
            attachment = MIMEText(html, 'html', _charset='utf-8')
            msg.attach(attachment)

        # Send the email
        conn.sendmail(
            from_addr, 
            to_addr,
            msg.as_string()
        )

        # Close the SMTP connection
        conn.quit()

        return True