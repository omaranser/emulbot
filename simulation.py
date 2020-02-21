import docker
import threading
import schedule
import time
import re
from numpy import ones
from numpy import random
from numpy.random import choice
from argparse import ArgumentParser
import coloredlogs, logging

client = docker.from_env()

logger = logging.getLogger(__name__)
logging.basicConfig()
coloredlogs.install(level='INFO', logger=logger)


def init():
    #set up queue
    queue={}
    i=0
    for container in client.containers.list():
        if re.match("^bot_[0-9]+", container.name):
            queue.update({i:container.id})
            i=i+1
    return i,queue


def scheduler(queue,idMax):

    rand = random.randint(0,idMax)
    return queue[rand]


def execSingleRequest(queue,idMax):

    lines = open("dns.txt").read().splitlines()
    dn = choice(lines,1,p=sorted(random.dirichlet(ones(100),size=1)[0],reverse=True))
    id = scheduler(queue, idMax - 1)
    cont = client.containers.get(id)
    cont.exec_run("dig " + str(dn) + " @193.168.0.9")


def execMResquest(queue,idMax):

    mresquest = random.randint(0,20)
    for i in range(mresquest):
        t=threading.Thread(target=execSingleRequest(queue,idMax))
        t.start()
    try:
        t.join()
    except :
        pass


def execRequests(queue,idMax):

    nbot = random.randint(0,idMax-1)
    for i in range(nbot):
        t=threading.Thread(target=execMResquest(queue,idMax))
        t.start()
    try:
        t.join()
    except :
        pass



def execBadRequest(queue,idMAx):

    for i in range(idMAx):
        cont = client.containers.get(queue[i])
        cont.exec_run("dig cnc.internet @193.168.0.9")



def main():

    parser = ArgumentParser()

    parser.add_argument("--pktfreq", default=None)
    parser.add_argument("--duration", default=None)

    args=parser.parse_args()
    fq=args.pktfreq
    dur=args.duration

    logging.info("Preparing simulation")
    idMax,queue=init()

    logging.info("Setup scheduler")
    schedule.every(5).seconds.do(execRequests,queue,idMax)
    schedule.every().hour.do(execBadRequest,queue,idMax)

    logging.info("Running simulation")

    while True:
        schedule.run_pending()
        time.sleep(1)



if __name__ == '__main__':
    main()


