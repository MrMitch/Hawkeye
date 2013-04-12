#!/bin/bash
# Hawkeye installation script

sudo su -
$INSTALLATION_DIR=/etc/hawkeye
$HAWKEYE_CONFIG=/usr/local/bin/hawkeye-config

echo "Creating hawkeye user and group..."
useradd -r -s /bin/false hawkeye
echo "...done"

echo "Fetching hawkeye's sources from GitHub..."
git clone https://github.com/MrMitch/Hawkeye.git /tmp/hawkeye

if [[ $? = 0 ]]
	then
	echo '...done'

	echo "Fetching hawkeye's dependencies..."
	cd $INSTALLATION_DIR
	git submodule init
	git submodule update
	echo "...done"

	mv /tmp/hawkeye/ $INSTALLATION_DIR

	echo "Creating hawkeye service launcher and config binary..."
	ln -s $HAWKEYE_CONFIG $INSTALLATION_DIR/configure.py
	ln -s /etc/init.d/hawkeye $INSTALLATION_DIR/install/service_launcher.sh
	echo "...done"

	# chown -R hawkeye:hawkeye /etc/hawkeye

	echo -n "Should hawkeye start on boot ? [yes/no] "
	read BOOT

	if [[ $BOOT == "y" || $BOOT == "yes" ]]
		then
		echo "Configuring hawkeye to start on boot..."
		update-rd.d hawkeye defaults
		echo "...done"
	fi

	echo "To control hawkeye manualy, you can run (as root): "
	echo "service hawkeye {status|start|stop|restart}"

	echo "Hawkeye is now installed, BUT NOT CONFIGURED, You can configure hawkeye by running: hawkeye-config."
	echo -n "Should this script invoke it for you now ? [yes/no]"
	read CONFIG

	if [[ $CONFIG == "y" || $CONFIG == "yes" ]]
		then
		python $HAWKEYE_CONFIG
	fi
else
	echo "...fail!"
fi

logout