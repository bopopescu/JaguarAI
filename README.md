# Windows Setup

 - Clone the repository
 - Install Python 3.6 by downloading from here
 - In the shell the commmand `python -m pip install -r requirements.txt`
 - Put your database file into the folder with the rest of the files
 - Create a new account with `python manage.py createsuperuser`
 - Run `python manage.py runserver` to start the development server
 - Visit `http;//localhost:8000` in your browser to use the site


# Setting up TOR on Linux

```
# Install
sudo apt-get install tor

# Generate the password
tor --hash-password foobie-bletch

# Add lines to the torrc
sudo vim /etc/tor/torrc

# ControlPort 9051
# HashedControlPassword <the password from above>
# SOCKSPort 9050
# SOCKSPolicy accept *
# MaxCircuitDirtiness 10

# Restart tor
sudo service tor restart
```

# Gathering Amazon Data

```
./manage.py fetch_browse_nodes
./manage.py fetch_search_data
./manage.py populate_searches
./manage.py fetch_product_data
./manage.py cache_judgement_data
```

# Server Setup
```
sudo cp jaguar/guncorn.service /etc/systemd/system/gunicorn.service

# Install Caddy
curl -s https://getcaddy.com | bash
sudo mkdir /etc/caddy
sudo chown -R root:www-data /etc/caddy
sudo cp Caddyfile /etc/caddy/Caddyfile
sudo mkdir /etc/ssl/caddy
sudo chown -R www-data:root /etc/ssl/caddy
sudo chmod 0770 /etc/ssl/caddy
sudo curl -s https://raw.githubusercontent.com/mholt/caddy/master/dist/init/linux-systemd/caddy.service -o /etc/systemd/system/caddy.service
sudo systemctl daemon-reload
sudo systemctl enable caddy.service
sudo systemctl status caddy.service
sudo ufw allow http
sudo ufw allow https
sudo systemctl start caddy

# Setup a database
```
