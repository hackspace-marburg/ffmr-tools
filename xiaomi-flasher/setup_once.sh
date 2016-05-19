#/bin/bash

echo '######################################################################'
echo 'this will create a virtual Python environment and install selenium.'
echo 'this has to be done only once.'
echo 'Can we continue? (y)'
read answer

# apt-get install python-virtualenv
virtualenv env

#env/bin/pip install -U pip
#env/bin/pip install -U setuptools
env/bin/pip install selenium


echo 'done.'
echo '######################################################################'
echo 'use "env/bin/python xiaomi-flash-selenium.py" to start flashing.'
echo '######################################################################'
