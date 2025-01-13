echo updating 
cp /etc/letsencrypt/live/jorm.kurowski.xyz/fullchain.pem server/server.crt
cp /etc/letsencrypt/live/jorm.kurowski.xyz/privkey.pem server/server.key
cp client/index.html /var/www/Jorm/index.html
echo done
# sudo certbot renew
