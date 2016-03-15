#!/usr/bin/env python
#
#    CrankTools.py
#        The OnNetworkLoad method is called from crankd on a network state change, all other
#            methods assist it. Modified from Gary Larizza's script (https://gist.github.com/glarizza/626169).
#
#    Last Revised - 10/07/2013
 
__author__ = 'Graham Gilbert (graham@grahamgilbert.com)'
__change__ = 'Yves Zieger (yves.zieger@googlemail.com)'
__version__ = '0.7'
 
import syslog
import subprocess
from time import sleep
 
syslog.openlog("CrankD")
 
class CrankTools():
    """The main CrankTools class needed for our crankd config plist"""
 
    def puppetRun(self):
        """Checks for an active network connection and calls puppet if it finds one.
            If the network is NOT active, it logs an error and exits
        ---
        Arguments: None
        Returns:  Nothing
        """
        command = ['/opt/puppetlabs/bin/puppet','agent','-t']
        if self.LinkState():
            self.callCmd(command)
        else:
            syslog.syslog(syslog.LOG_ALERT, "Internet Connection Not Found, Puppet Run Exiting...")
 
    def munkiRun(self):
        """Checks for an active network connection and calls Munki if it finds one.
            If the network is NOT active, it logs an error and exits
        ---
        Arguments: None
        Returns:  Nothing
        """
        command = ['/usr/local/munki/managedsoftwareupdate','--auto']
        if self.LinkState():
            self.callCmd(command)
        else:
            syslog.syslog(syslog.LOG_ALERT, "Internet Connection Not Found, Munki Run Exiting...")
 
    def callCmd(self, command):
        """Simple utility function that calls a command via subprocess
        ---
        Arguments: command - A list of arguments for the command
        Returns: Nothing
        """
        task = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        task.communicate()
 
    def LinkState(self):
        """This utility returns the status of the passed interface.
        ---
        Arguments:
            None
        Returns:
            status - The return code of the subprocess call
        """
 
        theState = False
 
        for interface in range(0, 20):
            interface = str(interface)
            adapter = 'en' + interface
            print 'checking adapter '+adapter
            if not subprocess.call(["ipconfig", "getifaddr", adapter]):
                theState = True
                break
 
        return theState
 
    def OnNetworkLoad(self, *args, **kwargs):
        """Called from crankd directly on a Network State Change. We sleep for 10 seconds to ensure that
            an IP address has been cleared or attained, and then perform a Puppet run and a Munki run.
        ---
        Arguments:
            *args and **kwargs - Catchall arguments coming from crankd
        Returns:  Nothing
        """
        sleep(10)
        self.puppetRun()
        self.munkiRun()
 
def main():
    crank = CrankTools()
    crank.OnNetworkLoad()
 
if __name__ == '__main__':  
    main()
