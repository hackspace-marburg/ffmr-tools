# this script can be used to prepare a xiaomi mini device
# for flashing of the freifunk firmware onto it.
#
#
import os
# import pdb  # just for debugging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import sys
import telnetlib
import time  # we sleep sometimes...


class FlashXiaomiRouter:

    def __init__(self):
        self.driver = None
        self.admin_password_set_already = False

    def opening(self):
        print('#'*50)
        print('# this script will attempt to flash your xiaomi router.')
        print('# * just watch the browser do things...')
        print('# * make sure your router has power '
              'and you have an ethernet connection to it '
              '(connect to one of the *yellow* ports)')
        print('#'*50)

    def check_ping(self):
        # check ip connectivity...
        response = os.system("ping -c 1 192.168.31.1")
        # and then check the response...
        print('the response: {}'.format(response))
        if response != 0:
            print('#'*50)
            print("# no ping to 192.168.31.1. are you cable connected?!?\n"
                  "# please connect and try again.\n"
                  "# exiting.")
            print('#'*50)
            sys.exit(1)
        if response == 0:
            print('ping to 192.168.31.1 worked.')

    def start_browser(self):
        self.driver = webdriver.Firefox()
        self.driver.set_window_size(800, 600)
        print('opening the routers web frontend...')
        self.driver.get("http://192.168.31.1")
        assert "Mi Router" in self.driver.title
        print("we found a Mi router. good.")

        if "Enter administrator password" in self.driver.page_source:
            print('#' * 50)
            print("this router has an admin password set.")
            print("let's see if we can guess it... else:")
            print("please reset the router to factory defaults and try again.")
            print("type 'freudich' into that form, go to Settings, status, "
                  "then click Restore and confirm with OK.")
            print('#' * 50)
            self.admin_password_set_already = True
        print('#' * 50)

    def start_wizard(self):
        # step #1 ###################################################
        assert "Terms of Service" in self.driver.page_source
        assert "Agree to terms" in self.driver.page_source
        print("let's click some buttons... step #1.")
        button = self.driver.find_element_by_id('btnStart')
        button.click()
        print("clicked the button. let's wait a bit... (10 seconds)")
        time.sleep(15)
        
        print('#' * 50)

    def choose_wifi_mode(self):
        # step #2 ###################################################
        try:
            assert 'Mode (Set up Wi-Fi network)' in self.driver.page_source
            print("let's click some buttons... step #2.")
            button2 = self.driver.find_element_by_link_text(
                'Mode (Set up Wi-Fi network)')
            button2.click()
            print("clicked the button. let's wait a bit... (5 seconds)")
            time.sleep(5)
            print('#' * 50)
        except NoSuchElementException as nsee:
            print nsee
            pass

    def set_wifi_password(self):
        # step #3 ##################################################
        print("let's set a wifi password... step #3.")
        assert "Set Wi-Fi network name and password" in self.driver.page_source
        _wifipwd = self.driver.find_element_by_name('wifipwd')
        _wifipwd.click()
        _wifipwd.send_keys('freufunk')
        _wifipwd.send_keys(Keys.RETURN)
        time.sleep(1)
        print("we set a wifi password ('freufunk'). "
              "let's wait a bit... (2 seconds)")
        time.sleep(2)
        print('#' * 50)

    def set_admin_password(self):
        # step #4 ##################################################
        print("and now: set the admin passwd... step #4")
        _routerpwd = self.driver.find_elements_by_name('routerpwd')[1]
        _routerpwd.click()
        _routerpwd.send_keys('freudich')
        time.sleep(1)
        _routerpwd.send_keys(Keys.RETURN)
        print("we set an admin password ('freudich'). "
              "let's wait a bit... (10 sec.)")
        time.sleep(10)
        print('#' * 50)
        assert 'Setting up' in self.driver.page_source
        _still_setting_up = 'Setting up' in self.driver.page_source
        secs = 0
        while _still_setting_up:
            print("after {} secs...".format(secs))
            print('still setting up...')
            _still_setting_up = 'Setting up' in self.driver.page_source
            time.sleep(5)
            secs += 5

    def log_in_as_admin(self):
        print("and now: log in as admin to get the stok...")
        if "Enter administrator password" in self.driver.page_source:
            _input = self.driver.find_element_by_id('password')
            _input.click()
            _input.send_keys('freudich')
            _input.send_keys(Keys.RETURN)
            print("logging in; wait a bit... (10 sec.)")
            time.sleep(10)
        else:
            btn = self.driver.find_element_by_partial_link_text(
                'Connect to router admin page')
            assert btn.is_enabled()
            btn.click()
            print("logging in; wait a bit... (10 sec.)")
            time.sleep(10)
        self.stok = self.driver.current_url.split('=')[1].split('/')[0]
        print("the stok token: {}".format(self.stok))

    def enable_telnet(self):
        _first = ("http://192.168.31.1/cgi-bin/luci/;stok={}/api/xqnetwork/"
                  "set_wifi_ap?ssid=whatever&encryption=NONE&enctype=NONE&"
                  "channel=1%3B%2Fusr%2Fsbin%2Ftelnetd".format(self.stok))
        print("the crafted get: {}".format(_first))
        print("wait a bit...")
        time.sleep(5)
        print("go on... issue that get")
        _telnet_on = self.driver.get(_first)
        time.sleep(10)

        _no_result = True
        while _no_result:  # loop to wait
            try:
                print("result: {}".format(_telnet_on))
                print("response: {}".format(self.driver.page_source))
                if '1616' in self.driver.page_source:
                    _no_result = False
            except:
                print("wait 5 more seconds...")
                time.sleep(5)

        # print("status code: {}".format(.status_code))
        # res3 = driver.get(first_put)
        print('#' * 50)
        print("wait a bit, then issue next command... (5 sec.)")
        time.sleep(5)
        ############################################################

        self.stok = self.driver.current_url.split('=')[1].split('/')[0]
        print("the stok token: {}".format(self.stok))

        _second = ("http://192.168.31.1/cgi-bin/luci/;stok={}/api/xqsystem/"
                   "set_name_password?oldPwd=freudich&newPwd=freumich".format(
                       self.stok))

        print("issuing the second request...")
        print(_second)
        _second_get = self.driver.get(_second)
        time.sleep(10)

        _no_result = True
        while _no_result:  # loop to wait
            try:
                # print("result: {}".format(_second_get))
                # print("response: {}".format(self.driver.page_source))
                if """{"code":0}""" in self.driver.page_source:
                    _no_result = False
                    print("found the expected code: 0")
            except:
                print("wait 5 more seconds...")
                time.sleep(5)
                # pass

        print("result: {}".format(_second_get))
        # print("response: {}".format(_second_get.page_source))
        self.driver.close()
        print('#' * 50)
        print("almost done. telnet should work now...")
        print('#' * 50)
        time.sleep(5)

    def telnet_and_flash(self):
        print('#' * 50)
        print("# now we use telnet to log into the router, wget the "
              "# new firmware,\n and trigger flashing of the router.")
        print("# just a check...")
        positive_response = None
        while not positive_response:
            # check ip connectivity...
            response = os.system("ping -c 1 208.67.222.222")
            # and then check the response...
            print('# the response: {}'.format(response))
            if response != 0:
                print('#'*50)
                print("# no ping to 208.67.222.222. LAN port connected?!?\n"
                      "# please connect and try again.\n"
                      "# ")
                print("# * make sure the router is now connected to the "
                      "$internets!")
                print("# * plug the $internet (DHCP) into the blue WAN port!")
                print("# ==>OK to go on?<==")
                raw_input()

                print('#'*50)
            if response == 0:
                print('# ping to 208.67.222.222 worked.')
                positive_response = True

        print('#' * 50)
        SERVER = "http://update.marburg.link/experimental/sysupgrade/"
        FIRMWARE = ("gluon-ffmr-5-experimental-"
                    "xiaomi-miwifi-mini-sysupgrade.bin")
        MD5HASH = '9238621ad4f42f5fc7db085927c20fcd'
        HOST = "192.168.31.1"
        user = "root"
        password = "freumich"

        try:
            tn = telnetlib.Telnet(HOST)
            time.sleep(0.5)
        except Exception as e:
            print e.errno
            print e.strerror
            print("this means your router is not ready for telnet. sorry.")
            print("your best bet is to log in as admin, reset the router,")
            print("and start all over again.")
            print("Settings -> Status -> Restore to factory.")
            sys.exit(1)

        tn.read_until("login: ")
        tn.write(user + "\n")

        if password:
            tn.read_until("Password: ")
        tn.write(password + "\n")

        print("tn.sock_alive(): {}".format(tn.sock_avail()))

        tn.read_until('BusyBox')
        print("we are in!")

        tn.read_until('root@XiaoQiang:~#')
        print("login worked.")
        print("will cd to /tmp...")
        tn.write('cd /tmp/\n')
        #tn.interact()
        print("expecting output")
        print tn.read_until('root@XiaoQiang:/tmp#')
        #import pdb
        #pdb.set_trace()
        print('setting nameserver to 208.67.222.222')
        tn.write('echo "nameserver 208.67.222.222" > /etc/resolv.conf\n')
        tn.read_until('root@XiaoQiang:/tmp#')
        print('now start wget...')
        print('wget ' + SERVER + FIRMWARE + ' \n')
        tn.write('wget ' + SERVER + FIRMWARE + ' \n')
        print tn.read_until('root@XiaoQiang:/tmp#')
        print("check the md5 hash of the file")
        tn.write('md5sum ' + FIRMWARE + ' \n')
        time.sleep(10)
        print(tn.read_until('.bin'))
        tn.write("mtd -r write " + FIRMWARE + " OS1 \n")

        tn.write("exit\n")
        print tn.read_all()


if __name__ == '__main__':

    f = FlashXiaomiRouter()
    f.opening()
    f.check_ping()
    # the wizard...
    f.start_browser()
    if not f.admin_password_set_already:
        f.start_wizard()
        f.choose_wifi_mode()
        f.set_wifi_password()
        f.set_admin_password()
    f.log_in_as_admin()
    f.enable_telnet()
    f.telnet_and_flash()
    print('#' * 50)
    print("# all done. router will take sone time and reboot now.")
    print("# be patient...")
    print("# watch the blinking blue light...")
    print("# once it stops blinking...")
    print("# see if you can still ping 192.168.31.1. if not, reconnect...")
    print("# and try pinging 192.168.1.1... if that works")
    print("# point your browser at http://192.168.1.1 ...")

    print('#' * 50)
