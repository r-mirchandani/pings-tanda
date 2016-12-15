# pings-tanda
My implementation of Tanda's developer challenge.

This implementation was written in Python, based on Flask. The server runs on the Flask development server - most likely is not a good idea to deploy in this way. sqlite3 is used for storage of data in order to provide sold data persistence, while being relatively lightweight on the server.

Implementation requires Flask and sqlite3 installed.

To run:

1. Navigate to folder within terminal.
2. 'export FLASK_APP=tanda_pings.py' - Move application onto the flask development server.
3. 'flask initdb' - If .db file is corrupt/missing, this command will create the database.
4. 'flask run' - Launch the server, running on http://localhost:5000
5. Run pings.rb to test!
