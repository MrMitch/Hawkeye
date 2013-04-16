#Hawkeye

Communicate with distant computers, via Twitter.

## Installation

**TL;DR**: `wget -qO /tmp/h.sh http://bit.ly/get-hawkeye && sudo bash /tmp/h.sh` 


To install Hawkeye, you can download the [install.sh](install/install.sh) script, make it executable and execute it...    
... or you can simply run:    
`wget -qO /tmp/h.sh http://bit.ly/get-hawkeye && sudo bash /tmp/h.sh`    

In both cases, you should get an output that looks like the following (if everything is OK): 
 
```
Fetching hawkeye's sources from GitHub...
Cloning into /tmp/hawkeye...
remote: Counting objects: 411, done.
remote: Compressing objects: 100% (212/212), done.
remote: Total 411 (delta 188), reused 409 (delta 186)
Receiving objects: 100% (411/411), 383.44 KiB | 275 KiB/s, done.
Resolving deltas: 100% (188/188), done.
...done

Fetching hawkeye's dependencies...
Submodule 'modules/rdcli' (git://github.com/MrMitch/realdebrid-CLI.git) registered for path 'modules/rdcli'
Submodule 'modules/twitter' (git://github.com/sixohsix/twitter.git) registered for path 'modules/twitter'
Cloning into modules/rdcli...
remote: Counting objects: 269, done.
remote: Compressing objects: 100% (137/137), done.
remote: Total 269 (delta 140), reused 255 (delta 126)
Receiving objects: 100% (269/269), 41.01 KiB, done.
Resolving deltas: 100% (140/140), done.
Submodule path 'modules/rdcli': checked out '48ffe5c35ef3f0165e828ea1cddaa1d822279cff'
Cloning into modules/twitter...
remote: Counting objects: 1588, done.
remote: Compressing objects: 100% (581/581), done.
remote: Total 1588 (delta 1090), reused 1483 (delta 994)
Receiving objects: 100% (1588/1588), 230.78 KiB | 293 KiB/s, done.
Resolving deltas: 100% (1090/1090), done.
Submodule path 'modules/twitter': checked out 'c0c3727024108dd12d96b7a3133a44f1fd252d1c'
...done

Creating hawkeye user and group...
...done

Creating hawkeye service launcher and config binary...
...done

Should hawkeye start on boot ? [yes/no] y
Configuring hawkeye to start on boot...
update-rc.d: using dependency based boot sequencing
...done

To control hawkeye manualy, you can run (as root): 
service hawkeye {status|start|stop|restart}
Cleaning installation files...
...done

Hawkeye is now installed, BUT NOT CONFIGURED.
You can configure hawkeye by running: hawkeye-config.
Should this script invoke it for you now ? [yes/no] y
```

Runing the `hawkeye-config` command immediatly after the installation is generally a good idea (the installation script will ask if it has to invoke it for you).
