import socket, datetime, threading, os, urllib
from math import *

class BobServer(threading.Thread):
    counter = 0
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = port

    def now(self):
        d = datetime.datetime.now()
        return d.strftime("%d/%m/%y %H:%M:%S")
    """
    Handle Boblight messages and send response
    """
    def parseMessage(self, conn , msg):
        if (msg == "hello\n"):
            print 'Got hello'
            conn.send("hello\n")
        if (msg == "get version\n"):
            print 'recieved Get version'
            conn.send("version 5\n")
        if (msg == "ping\n"):
            conn.send("ping 0\n")

        """
        Get lights asks the server to reply with the configured led lights and wich section of the screen each light represents.

        In this case there is only one light defined, with a scan of 0-100, 0-100; meaning, the entire screen is handled by one led.
        """
        if (msg == "get lights\n"):
            print 'recieved Get lights'
            conn.send("lights 1\nlight alles scan 0 100 0 100\n")

        if (msg.find("set light") != -1):
            self.counter += 1
            print 'set light'

            # Handle every other set-light command.
            if ((self.counter % 1) == 0):
                print '                    Counter: ', self.counter
                lines = msg.splitlines()

                # Parse colors
                colors = lines[0].split(' ')
                if (colors[3] != 'rgb'):
                    print 'no valid rgb colors'
                    print colors
                    return

                # Write rgb colors to pi-blaster
                os.system('echo "6='+colors[5]+'" > /dev/pi-blaster')
                os.system('echo "7='+colors[6]+'" > /dev/pi-blaster')
                os.system('echo "5='+colors[4]+'" > /dev/pi-blaster')
                print colors

    """
    Run a server forever and listen on a port.
    Recieved messages are handled by parseMessage()
    """
    def run(self):
        host = ''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, self.port))
        print 'server started successfully, waiting...'
        s.listen(1)
        conn, addr = s.accept()
        print 'contact', addr, 'on', self.now()

        while 1:
            try:
                data = conn.recv(1024)
            except socket.error:
                print 'lost', addr, 'waiting..'
                s.listen(1)
                conn, addr = s.accept()
                print 'contact', addr, 'on', self.now()
                continue

            if not data:
                print 'lost', addr, 'waiting..'
                s.listen(1)
                conn, addr = s.accept()
                print 'contact', addr, 'on', self.now()
            else:
                self.parseMessage(conn, data)



t = BobServer(31944)
t.start()
