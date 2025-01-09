(cd server && source env/bin/activate && python3 .) & (cd ..) & (cd client && source env/bin/activate && python3 .) & (cd client && python3 -m http.server 8110)
