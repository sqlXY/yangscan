#-*- encoding:utf-8 -*-
import argparse
import socket
import ipaddr
import sys
import time
import threading, Queue

class mainScan(threading.Thread):
    """扫描一个IP"""
    def __init__(self, ips, ports, result):
        super(mainScan, self).__init__()
        self._ips = ips
        self._ports = ports
        self._res = result

    def run(self):
        if type(self._ips) == type(""):
            for port in self._ports:
                self.socketScan(self._ips, port)
            return

        while not self._ips.empty():
            ip = self._ips.get()
            for port in self._ports:
                self.socketScan(ip, port)

    def socketScan(self, ip, port):
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sk.connect((ip, int(port)))
            r = [ip, port, 'open']
            
            try:
                sk.send('Hi')
                r.append(str(sk.recv(200)))
            except Exception as e:
                r.append(None)

            self._res.put(r)
        except Exception as e:
            pass

        sk.close()

def printLog(res, file, cli_end):
    while threading.activeCount() != 1:
        if not res.empty():
            r = res.get()
            if cli_end != True:
                print '[+] %s finded %s port %s | %s' % (r[0], r[1], r[2], r[3])
            if file:
                with open(file, 'a+') as sf:
                    sf.write("%s|%s|%s|%s\n" % (r[0], r[1], r[2], \
                                                r[3].replace('\n', ' ')))

def startProcess(ip, ports, threads, file, cli_end):
    #Config
    targets = Queue.Queue()
    res = Queue.Queue()
    socket.setdefaulttimeout(1)
    

    if '/' in ip:
        hosts = ipaddr.IPv4Network(ip).iterhosts()
        for i in hosts:
            targets.put(str(i))
    else:
        targets = ip
    ports = ports.split(',')

    

    for i in range(threads):
        th = mainScan(targets, ports, res)
        th.start()

    printLog(res, file, cli_end)

def main():
    parser = argparse.ArgumentParser(version='1.0', description = "This program is used to scan ports and check if they are open.")
    
    parser.add_argument('-i', '--ip', help = "Input IP or IP/mask")
    parser.add_argument('-l', '--list', help = "Input a file to load ip")
    parser.add_argument('-p', '--ports', required = True,help = "Input scan one or some ports like 21,22,3389")
    parser.add_argument('-t', '--threads', default = 10, help = "Input your crack threads(default 10)")
    parser.add_argument('-f', '--file', default = None, help = "Input your output file path to save result as a file")
    parser.add_argument('--cli-end', action="store_true", help = "Close CLI print")


    arg = parser.parse_args()
    if arg.ip and arg.list:
        print "[-] you can't use -i/--ip with -l/--list.You must choose one of them."
        return
    elif not (arg.ip or arg.list):
        print "[-] We require a ip. you should use -i/--ip or -l/--list.You must choose one of them."
        return

    if arg.ip:
        startProcess(arg.ip, arg.ports, arg.threads, arg.file, arg.cli_end)

if __name__ == '__main__':
    main()

    
