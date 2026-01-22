echo Starting whole setup!

(cd server && python3 -m venv env && source env/bin/activate && pip install -e .) &&
(cd ..) &&

(cd client && python3 -m venv env && source env/bin/activate && pip install -r requirements.txt) &&
(cd ..) &&
(openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout server.key -out server.crt -subj "/C=US/ST=State/L=City/O=Organization/OU=IT/CN=example.com") &&
mv server.crt ./server/server.crt &&
mv server.key ./server/server.key &&

echo done!