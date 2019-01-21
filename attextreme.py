#!/usr/bin/env python3
import os
import sys
import time
import getpass
import telnetlib
from multiprocessing import Pool

## Import private configs or use the above, change '<PARAMS>'
import private
# tftpcmd = "download image <IP_LOCAL> %s VR-Default" # %img
# radiuscmd = "configure radius mgmt-access primary server <IP_SERVER> 1812 client-ip %s vr VR-Default\nconf radius mgmt-access primary shared-secret <PASSWD>\nenable radius mgmt-access\n"

## Fix models selection, now just commenting/ uncommenting
# model = "X440-48"
# lastv = "16.2.5.4"
# img = "X440-summitX-16.2.5.4-patch1-7.xos"
#
# model = "X440-G2"
# lastv = "22.6.1.4"
# img = "X440G2-summitX-22.6.1.4-patch1-1.xos"
#
model = "X430"
lastv = "16.2.5.4"
img = "X430-summitlite-16.2.5.4-patch1-7.xos"


def enablessh(host):
    print('Ativando SSH do %s' % host)
    try:
        tn = telnetlib.Telnet(host)
        tn.read_until(b"login:")
        tn.write(user.encode('ascii') + b"\n")
        tn.read_until(b"password:")
        tn.write(passwd.encode('ascii') + b"\n")
        tn.read_until(b" # ",30)
        tn.write(b"enable ssh2\n")
        tn.write(b"y\n")
        tn.write(b"save config\n")
        tn.write(b"y\n")
        tn.write(b"exit\n")
        s = tn.read_all().decode('ascii')
    except:
        print('Erro ao ativar ssh no host: %s' % host)
        f = open(model+'.falha','a+')
        f.write(host)
        f.write('\n')
        f.close()

def atualiza(host):
    print('Atualizando %s' % host)
    tn = telnetlib.Telnet(host)
    tn.read_until(b"login:")
    tn.write(user.encode('ascii') + b"\n")
    tn.read_until(b"password:")
    tn.write(passwd.encode('ascii') + b"\n")
    tn.read_until(b" # ",30)
    msg = private.tftpcmd %img
    # msg = msg.replace("\n","") # need?
    tn.write(msg.encode('ascii') + b"\n")
    tn.write(b"y\n")
    tn.read_until(b"Image installed successfully",1500)
    tn.write(b"save config\n")
    tn.write(b"y\n")
    tn.write(b"exit\n")
    s = tn.read_all().decode('ascii')

def set_radius(host):
    try:
        tn = telnetlib.Telnet(host,23,7)
        # tn.set_debuglevel(1)
        tn.read_until(b"login:")
        tn.write(useradm.encode('ascii') + b"\n")
        tn.read_until(b"password:")
        tn.write(passwdadm.encode('ascii') + b"\n")
        tn.read_until(b" # ",30)
        msg = private.radiuscmd %host
        tn.write(msg.encode('ascii')+b"\n")
        tn.write(b"save config\n")
        tn.write(b"y\n")
        tn.write(b"exit\n")
        s = tn.read_all().decode('ascii')
        time.sleep(5)
        verifica(host)
    except:
        print('Não foi possivel logar com \'%s\' no %s' %(useradm,host))
        f = open(model+'.falha','a+')
        f.write(host)
        f.write('\n')
        f.close()

def reboot(host):
    # TODO: make the rebootcmd auto getting time from switch + 2min
    # rebootcmd = "reboot time 1 15 2019 21 20 0"
    try:
        tn = telnetlib.Telnet(host,23,7)
        tn.read_until(b"login:")
        tn.write(user.encode('ascii') + b"\n")
        tn.read_until(b"password:")
        tn.write(passwd.encode('ascii') + b"\n")
        tn.read_until(b" # ",30)
        # tn.write(rebootcmd.encode('ascii') + b"\n")
        # tn.write(b"y\n")
        tn.write(b"reboot\n")
        tn.write(b"y\n")
        # tn.write(b"exit\n")
        s = tn.read_all().decode('ascii')
        # print(s)
    except:
        print("must have rebooted")

def verifica(host):
    try:
        tn = telnetlib.Telnet(host,23,7)
        # tn.set_debuglevel(1)
        tn.read_until(b"login:")
        tn.write(user.encode('ascii') + b"\n")
        tn.read_until(b"password:")
        tn.write(passwd.encode('ascii') + b"\n")
        tn.read_until(b" # ",30)
        tn.write(b"show config exsshd\n\n")
        tn.write(b"show switch\n\n")
        tn.write(b"exit\n")
        tn.write(b"y\n")
        s = tn.read_all().decode('ascii')
        # print(s)
        if lastv in s:
            match = 'xxxxxxxxx!!'
            for line in s.splitlines():
                if 'Image Booted:' in line:
                    match = line.split(':')[1].strip().title()
                if match in line:
                    if lastv in line:
                        if not 'enable ssh2' in s:
                            enablessh(host)
                        else:
                            print("OK")
                    else:
                        reboot(host)
                        # print('Falta rebootar o %s' % host)
        else:
            atualiza(host)
    except:
        print("Tentando logar com \'%s\' e ativar o radius..." % useradm)
        set_radius(host)

if __name__ == "__main__":
    user = input("Enter your radius user name: ")
    passwd = getpass.getpass('Enter your radius password: ')
    useradm = "admredes"
    passwdadm =  getpass.getpass('Enter the local \'%s\' password: ' %useradm)
    if not passwd:
        print("Senha em branco")
        exit(9)
    open(model+'.falha','w').close()
    pool = Pool(processes=50)
    hosts = open(sys.argv[1])
    count = 0
    for host in hosts:
        if model in host:
            count += 1
            pool.apply_async(verifica, args=(host.split(',')[0],))
    # print pool.map(f, range(10))          # prints "[0, 1, 4,..., 81]"
    pool.close()
    pool.join()
    print(count," Switches Encontrados")

exit(0)
