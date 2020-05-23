#!/usr/bin/python3
import smtplib
from string import Template
from email.mime.text import MIMEText

MY_ADDRESS = 'jose.cantero@bancard.com.py'

def get_contacts(filename):
    """
    Return two lists names, emails containing names and email addresses
    read from a file specified by filename.
    """

    names = []
    emails = []
    with open(filename, mode='r') as contacts_file:
        for a_contact in contacts_file:
            names.append(a_contact.split()[0])
            emails.append(a_contact.split()[1])
    return names, emails

def read_template(filename):
    """
    Returns a Template object comprising the contents of the
    file specified by filename.
    """

    with open(filename, 'r') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

def main():
    names, emails = get_contacts('mycontacts.txt') # read contacts
    message_template = read_template('message.txt')

    # set up the SMTP server
    server = smtplib.SMTP(host='192.100.1.12', port=25)

    # For each contact, send the email:
    for name, email in zip(names, emails):
        # Add in the actual person name to the message template
        message = message_template.substitute(PERSON_NAME=name.title())

        # Prints out the message body for our sake
        print(message)

        # Create the message
        msg = MIMEText(message)
        # setup the parameters of the message
        msg['From'] = MY_ADDRESS
        msg['To'] = email
        msg['Subject'] = 'This is TEST'

        # send the message via the server set up earlier.
        server.sendmail(msg['From'], [msg['To']], msg.as_string())
        del msg

    # Terminate the SMTP session and close the connection
    server.quit()

if __name__ == '__main__':
    main()