from sourcestatus import Server, db, update_all

update_all()

# I literally put this in here just so I can use it for a cronjob.

# */5 * * * * /usr/bin/python /path/to/update.py

# I'm not joking.