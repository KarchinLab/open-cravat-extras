#!/usr/bin/python3

import argparse
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import platform

parser = argparse.ArgumentParser()
parser.add_argument('log_dir',
                    help='Log directory'
                    )
parser.add_argument('recipients',
                    nargs='+',
                    help='Recipients for email'
                    )
cmd_args = parser.parse_args()

sender = 'support@cravat.us'
server_address = 'smtp.johnshopkins.edu'
server = smtplib.SMTP(server_address)
server.ehlo()

msg = EmailMessage()
msg['From'] = sender
msg['To'] = ', '.join(cmd_args.recipients)
msg['Subject'] = 'Clinvar ACMG Data Update'
log_dir = os.path.abspath(cmd_args.log_dir)

hostname=platform.node()
payload = 'The new Clinvar ACMG database was created at {hostname}:{log_dir}'.format(
    hostname = hostname,
    log_dir = log_dir
)
msg.set_content(payload)
server.send_message(msg)
server.close()