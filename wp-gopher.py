#!/usr/bin/env python

import ConfigParser
import MySQLdb
import sys

config = ConfigParser.ConfigParser()
config.read(("/etc/wp-gopher.ini", "wp-gopher.ini"))

dbh = MySQLdb.connect(host = config.get("database", "host"),
		      user = config.get("database", "user"),
		      passwd = config.get("database", "password"),
		      db = config.get("database", "database")
		     )

def printblankline():
	printitem("i", "")

def printcopyright():
	"""Prints a copyright message."""

	global config

	printitem("i", config.get("blog", "copyright"))

def printitem(type, description, selector = "", domain = None, port = None):
	"""Prints a directory item in the proper Gopher format."""
	
	global config
	
	if not domain:
		domain = config.get("blog", "domain")

	if not port:
		port = config.getint("blog", "port")

	print "%s%s\t/%s\t%s\t%d\r\n" % (type, description, selector, domain, port),

def printtitle(pagetitle = None):
	"""Prints a title as an information message."""

	global config

	title = config.get("blog", "title")
	if pagetitle:
		title += " :: %s" % pagetitle

	printitem("i", title)

def index(limit = None):
	"""Prints a suitable index of blog posts, using limit if necessary."""
	
	global dbh
	
	c = dbh.cursor()
	c.execute("SELECT post_name, post_date, post_title FROM posts WHERE post_type = %s AND post_status = %s ORDER BY post_date DESC", ("post", "publish"))
	if limit:
		rows = c.fetchmany(limit)
	else:
		rows = c.fetchall()

	printtitle()

	for row in rows:
		printitem("h", "%s (%s)" % (row[2], row[1]), row[0])

	printblankline()
	if limit:
		printitem("i", "Only the last %d entries are listed here." % limit)
		printitem("1", "View all entries", "all")
	else:
		printitem("i", "All blog entries are shown.")

	printblankline()
	printcopyright()

def post(name):
	"""Prints a post."""

	global config
	global dbh

	if name == "all":
		return index()
	elif name == "":
		return index(config.getint("blog", "default"))

	c = dbh.cursor()
	c.execute("SELECT post_title, post_content FROM posts WHERE post_type = %s AND post_status = %s AND post_name = %s", ("post", "publish", name))
	row = c.fetchone()

	title = config.get("blog", "title")

	if row:
		pagetitle, body = row
	else:
		pagetitle = "Error"
		body = "Post not found"

	print """
<html>
	<head>
		<title>%s :: %s</title>
	</head>
	<body>
		<h1>%s :: %s</h1>
		%s
		<p>
			<a href="gopher://%s">Back to index</a>
		</p>
		<p style="font-style: italic; font-size: 80%%">
			%s
		</p>
	</body>
</html>
""" % (title, pagetitle, title, pagetitle, body, config.get("blog", "domain"), config.get("blog", "copyright"))

try:
	post(sys.stdin.readline().strip("\r\n/"))
except Exception, e:
	printtitle("Error")
	printitem("3", str(e))

# vim:set nocin ai ts=8 noet:
