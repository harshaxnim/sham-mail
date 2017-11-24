#!/usr/bin/python
import sys
import smtplib
from email.mime.text import MIMEText

if (len(sys.argv) != 2):
	print "USAGE: shamMail.py <mail.txt>"
	exit()

mailFile = sys.argv[1]

try:
	print "Reading from:",mailFile
	fp = open(mailFile, 'rb')
	fromAdd = fp.readline().strip()
	toAdd = fp.readline().strip()
	subject = fp.readline().strip()
	body=""
	for line in fp:
		body+=line
except:
	print "Trouble reading from:",mailFile
	exit()
finally:
	if ('fp' in globals()):
		fp.close()

print "Creating mail..."
msg = MIMEText(body)
msg['Subject'] = subject
msg['From'] = fromAdd
msg['To'] = toAdd

print "Printing Mail..."
print msg
print "^ Generated MIME Text ^"



try:
	print "Sending mail to",toAdd, "from", fromAdd
	s = smtplib.SMTP('localhost')
	s.sendmail(fromAdd, [toAdd], msg.as_string())
except:
	print "Unable to send mail. I'm bad at logging, so you have to figure out the issue yourself!!"
finally:
	s.quit()