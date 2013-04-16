#!/bin/bash
# Hawkeye installation script
ORIGIN_DIR=`pwd`

if [[ `whoami` == 'root' ]]
    then
    TMP_DIR=/tmp/hawkeye
    INSTALLATION_DIR=/etc/hawkeye
    HAWKEYE_CONFIG=/usr/local/bin/hawkeye-config

    echo "Fetching hawkeye's sources from GitHub..."
    git clone https://github.com/MrMitch/Hawkeye.git $TMP_DIR
    CLONE="$?"

    if [[ $CLONE != 0 ]]
        then
        echo '...fail!'
        echo "The installation script could not fetch Hawkeye's sources."
        echo "Please check your Internet connection and make sure that you have installed git."
        exit 1
    fi

    echo "...done"
    echo ""

    echo "Fetching hawkeye's dependencies..."
    cd $TMP_DIR
    git submodule init
    git submodule update
    echo "...done"
    echo ""

    echo "Creating hawkeye user and group..."
    useradd -r -s /bin/false hawkeye
    echo "...done"
    echo ""

    mv /tmp/hawkeye/ $INSTALLATION_DIR

    echo "Creating hawkeye service launcher and config binary..."
    ln -s $INSTALLATION_DIR/configure.py $HAWKEYE_CONFIG
    ln -s $INSTALLATION_DIR/install/service_launcher.sh /etc/init.d/hawkeye
    echo "...done"
    echo ""

    # chown -R hawkeye:hawkeye /etc/hawkeye

    echo -n "Should hawkeye start on boot ? [yes/no] "
    read BOOT

    if [[ $BOOT == "y" || $BOOT == "yes" ]]
        then
        echo "Configuring hawkeye to start on boot..."
        update-rd.d hawkeye defaults
        echo "...done"
        echo ""
    fi

    echo "To control hawkeye manualy, you can run (as root): "
    echo "service hawkeye {status|start|stop|restart}"

    echo "Cleaning installation files..."
    rm -rf $TMP_DIR
    cd $ORIGIN_DIR
    echo "...done"
    echo ""

    echo "Hawkeye is now installed, BUT NOT CONFIGURED."
    echo "You can configure hawkeye by running: hawkeye-config."
    echo -n "Should this script invoke it for you now ? [yes/no] "
    read CONFIG

    if [[ $CONFIG == "y" || $CONFIG == "yes" ]]
        then
        python $HAWKEYE_CONFIG
    fi
else
    echo "This script must be run as root (or using sudo)"
fi