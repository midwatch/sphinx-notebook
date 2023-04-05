export DEBIAN_FRONTEND=noninteractive

echo "Set Time Zone"
timedatectl set-timezone America/Los_Angeles

echo "Add Ubuntu Dependencies"
apt-get update
apt-get upgrade -y
xargs apt-get install -y < /vagrant/project.d/requirements-dev.txt

echo "Installing python dependencies"
/usr/bin/python3 -m pip install --upgrade -r /vagrant/project.d/requirements-py3.txt
