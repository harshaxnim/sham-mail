import sqlite3
from sqlite3 import Error
import os

# TODO
# update this to the actual variable when it's in production
# mail_log = '/var/log/mail.log'
mail_log = 'test/mail.log'


# methods for db interaction

def create_connection(db_file_name):
	""" create a database connection to a SQLite database """
	global db
	try:
		db = sqlite3.connect(db_file_name)
	except Error as e:
		print("Unable to create/connect to the DB.")
		print(e)


def initialize_db():
	""" intialise the db with two tables, one of ip addresses and one of email data. create one to store the status of being initialised """
	try:
		try:
			init = db.execute("select * from meta where key='init'").fetchone()
			if (init[1]==1):
				print "Looks like the DB was already initialised. Aborting the initialisation sequence."
				return
		except Error as e:
			print (e)
		else:
			pass
		# create the meta table for meta info such as init status and last_logs_sync_time etc.
		db.execute('''create table meta(key text primary key, value integer)''')
		
		# creaete a table for ip tracking
		db.execute('''create table ip(
			id integer primary key autoincrement not null,
			ip integer,
			last_access_time int(11)
			)''')

		# create a table to track cookie and the message-id
		db.execute('''create table mail(
			id integer primary key autoincrement not null,
			mid text,
			from_add text,
			to_add text,
			body text,
			qid text,
			log text
			)''')

		# create a table to store the mail data
		db.execute('''create table track_user(
			id integer primary key autoincrement not null,
			mid text,
			cookie text
			)''')
	except Error as e:
		print "error initialising the db:"
		print e
	else:
		print "DB initialised successfully"
		db.execute('''insert into meta values ("init",1)''')
		db.execute('''insert into meta values ("last_logs_sync_time",0)''')
		db.commit();

def close_connection():
	""" closes the db connection """
	db.close()


# methods for ip table

def ip_to_int(ip):
	parts = ip.split('.')
	int_ip = (int(parts[0]) << 24) + (int(parts[1]) << 16) + \
			(int(parts[2]) << 8) + int(parts[3])
	return int_ip

def store_ip(ip_addr, time):
	""" stores the ip address in the DB. expects the input sanitised. """
	ip = ip_to_int(ip_addr)
	db.execute("insert into ip (ip, last_access_time) values (?, ?)", (ip, time))
	db.commit()

def retrieve_ip(ip_addr):
	""" retrieves the last access time for an ip if any. else returns 0. """
	ip = ip_to_int(ip_addr)
	cmd = "select * from ip where ip = " + str(ip)
	try:

		return db.execute(cmd).fetchone()[2]
	except:
		# first visit
		return 0


# methods for email table

def store_email(mid, fromAdd, toAdd, body, cookie):
	""" store the mail into the db. expects the input sanitized. """
	try:
		# store in mail
		db.execute("insert into mail (mid, from_add, to_add, body) values (?,?,?,?)", (mid, fromAdd, toAdd, body))
		# store in tracker
		db.execute("insert into track_user (mid, cookie) values (?,?)", (mid, cookie))
		db.commit();
	except Error as e:
		print "Unable to store mail"
		print e

def get_mids_list(cookie):
	""" gives the list of emails given the user cookie """
	# get all the mail ids from that cookie
	cmd = "select * from track_user where cookie = '" + str(cookie)+"'"
	cur = db.execute(cmd)
	mids = []
	for entry in cur:
		mids.append(entry[1])
	print mids

def get_last_logs_sync_time():
	return db.execute("select * from meta where key='last_logs_sync_time'").fetchone()[1]

def check_mail_status(mids):
	""" call when you need logs for the given mids. takes a list of mids! """

	last_file_update_time = os.path.getmtime(mail_log)
	# check the last update everytime a user asks and update the whole doc further! (sounds better and easier)
	
		# on user asking to check logs, check the last_logs_sync_time and compare with last_file_update_time.
	log_updated = last_file_update_time > get_last_logs_sync_time()
	print last_file_update_time
		# if llst<lfut, meaning there is an update in the logs
	if (log_updated):
		print "log was updated, initialising syncing procedures."
		
			# do comm -13 last_access.log /var/log/mail.log
		os.system("comm -13 data/last_access.log "+mail_log+" > data/change.log")
		
			# use the output to extract the logs
				# all the lines after postfix/cleanup string containing the same queue id belong to one message. these need to go into the log column
					# i.e, look for lines with postfix/cleanup, get the message id, see if it is in our list of mids. note the queue id.
		change_log = open('data/change.log')
		for line in change_log:
			if 'postfix/cleanup' in line:
				# print line
				queue_id = line.split(" ")[5].strip(":")
					# store the all the lines after the just read line until the new line does not contain the queue id anymore.
				print ">",queue_id
				log_for_this_mid = ""
				for relevant_line in change_log:
					if queue_id in relevant_line:
						log_for_this_mid += relevant_line
				# print log_for_this_mid
		# update logs in db, also update the last_logs_sync_time, and copy mail.log file to last_access.log
		# finally, show the logs from db
	print get_last_logs_sync_time()
	# for mid in mids:
	# 	cmd = "select * from mail where mid='"+mid+"'"
	# 	print db.execute(cmd).fetchone()



if __name__ == '__main__':
	print "Creating DB connection..."
	create_connection("data/sham-mail.db")
	print "Initialising the DB..."
	initialize_db()
	
	# print retrieve_ip('1.2.3.4')
	# store_email("asdf","a","b","lola","qwer")
	get_mids_list("qwer")
	check_mail_status(["asdf","a"])


	print "Closing DB connection..."
	close_connection()