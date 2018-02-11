#!/usr/bin/python

import serial, time, datetime, cgi, cgitb, getpass, sqlite3 as lite, sys, os, random, hashlib
#cgitb.enable()

# Initialize
class Initialize:
	def setKey(self):
		h = hashlib.sha512()
		h.update(str(random.randrange(256,10000)))
		file = open('A6GSMKEY','w')
		file.seek(0)
		file.write(h.hexdigest())
		file.close()

	def getKey(self):
		if not(os.path.isfile('A6GSMKEY')):
			self.setKey()
		file = open('A6GSMKEY','r')
		file.seek(0)
		key = file.read()
		file.close()
		return key

# DB MANAGER
class SqliteManager:

	def __init__(self):
		self.dbConn = lite.connect('tasks.db')
		self.dbCur = self.dbConn.cursor()

	def insert(self,number,text, date):
		result = self.dbCur.execute("INSERT INTO messages (number, text, send_after) VALUES(?, ?, ?)", (number,text, date.replace('T',' ')))
		self.commit()
		return result

	def destroy(self,id):
		result = self.dbCur.execute("DELETE FROM messages WHERE id=?;",(id,))
		self.commit()
		return result

	def getLast(self):
		result = self.dbCur.execute("SELECT * FROM messages WHERE send_after < DATETIME('now') ORDER BY id ASC LIMIT 1")
		result = result.fetchone()
		return result

	def getAll(self):
		result = self.dbCur.execute("SELECT * FROM messages ORDER BY id")
		result = result.fetchAll()
		return result	

	def dbConnClose(self):
		self.dbConn.close()

	def commit(self):
		self.dbConn.commit()


# SMS MANAGER 
class A6gsmManager:

	def __init__(self):
		self.port = serial.Serial("/dev/ttyS1",  115200, timeout=4)
		if(self.port.isOpen() == False):
			self.port.open()

	def command(self, command):
		command += "\r\n"
		self.port.write(command.encode())
		return self.port.readlines()
		
	def closePort(self):
		self.port.close()

	def smsCreate(self, number, body):
		if not(self.checkNumber(number)):
			return 0
		self.printLines(self.command('AT+CMGF=1'))
		self.printLines(self.command('AT+CMGS="+48'+ number +'"'))
		self.printLines(self.command(body.replace(chr(26),"")))
		self.printLines(self.command(chr(26)))
		return 1

	def smsGetAll(self):
		self.printLines(self.command('AT+CMGL="ALL"'))

	def smsGetUnread(self):
		self.printLines(self.command('AT+CMGL="REC UNREAD"'))

	def smsRemoveAll(self):
		self.printLines(self.command('AT+CMGD=1,4'))

	def smsRemoveById(self,id):
		self.printLines(self.command('AT+CMGD=' + id))

	def callMake(self,number):
		self.printLines(self.command('AT+SNFS=0'))
		self.printLines(self.command('ATD+'+number+';'))

	def callEnd(self):
		self.printLines(self.command('ATH'))	

	def printLines(self,lines):
		for msg in lines:
			continue
			print (msg)

	def checkNumber(self, number):
		if len(str(number)) == 9 and number.isdigit():
			return 1
		else:
			return 0


# CORE
try:
	user = getpass.getuser()
	if (user == "www-data"):	
		form = cgi.FieldStorage()
		initialize = Initialize()
		savedKey = str(initialize.getKey())
		print ("Content-type: text/html\n\n")
		if not(form.has_key("number") or form.has_key("text") or form.has_key("key")):
			print ('<form method="post">')
			print ('+48<input type="number" name="number" value="729694910"><br>')
			print ('Text<input type="text" name="text"><br>')
			print ('Data wysylki<input type="datetime-local" name="date" value="'+str(datetime.datetime.now().time())+'">')
			print ('<input type="submit" name="Send SMS">')
			print ('<input type="hidden" value="'+savedKey+'" name="key">')
			print ('</form>')
		else:
			
			number = form.getvalue('number')
			if not(form.has_key("number") and len(number) == 9 and number.isdigit()):
				print("BAD NUMBER")
				sys.exit()

			text = form.getvalue('text')
			if not(form.has_key("text") and len(text) > 1 and (len(text)<160)):
				print("BAD TEXT")
				sys.exit()

			if not (form.has_key("key") and (savedKey == form['key'].value)):
				print('BAD KEY')
				sys.exit()

			date = form.getvalue('date')
			if not (form.has_key("date")):
				print('BAD DATE')
				sys.exit()

			sqliteManager = SqliteManager()
			sqliteManager.insert(number,text, date)
			sqliteManager.dbConnClose()
			print ('saved in db')
	else:
		sqliteManager = SqliteManager()
		gsm = A6gsmManager()
		while (True):
			now = datetime.datetime.now()
			hour = datetime.time(now.hour)
			last = sqliteManager.getLast()
			if(str(hour) > "21" and str(hour) < "7"):
				print("SLEEP TIME "+str(hour))
				last = None

			if(last is None):
				print('DB is None')
				time.sleep(300)
			else:
				print('CREATE SMS')
				gsm.smsCreate(last[1],last[2])
				#print("DESTROY: "+str(last[0]))
				sqliteManager.destroy(last[0])
				#print ("Sent sms to:  "+str(last[1])+" ;")
				print('COMPLETED SMS')
				time.sleep(20)
except ValueError:
	print "ERR STOPPED EXECUTION CODE"
