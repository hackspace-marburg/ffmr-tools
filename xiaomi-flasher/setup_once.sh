#/bin/bash

echo '######################################################################'
echo 'this will create a virtual Python environment and install selenium.'
echo 'this has to be done only once.'
echo 'Can we continue? (y)'
read answer

# apt-get install python-virtualenv
virtualenv2 env

#env/bin/pip install -U pip
#env/bin/pip install -U setuptools
env/bin/pip2 install selenium
env/bin/pip2 install requests  # TODO use pip freeze.


echo 'done.'
echo '######################################################################'
echo 'use "env/bin/python2 xiaomi-flash-selenium.py" to start flashing.'
echo '######################################################################'
