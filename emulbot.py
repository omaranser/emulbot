import threading
import docker
from argparse import ArgumentParser
import sys
import time
import coloredlogs, logging
from console_progressbar import ProgressBar

client = docker.DockerClient(base_url='unix://var/run/docker.sock')

logger = logging.getLogger(__name__)
logging.basicConfig()
coloredlogs.install(level='INFO', logger=logger)


def buildDockerNetworks():
    ipam_pool_local = docker.types.IPAMPool(
        subnet='10.0.0.0/8',
        gateway='10.255.255.254'
    )
    ipam_config = docker.types.IPAMConfig(
        pool_configs=[ipam_pool_local]
    )
    try:
        client.networks.create("nw_local", driver="bridge", ipam=ipam_config)
    except docker.errors.APIError:
        logging.error("[client.networks.create()] The server returns an error while creating nw_local network")

    ipam_pool_internet = docker.types.IPAMPool(
        subnet='193.168.0.0/24',
        gateway='193.168.0.254'
    )
    ipam_config = docker.types.IPAMConfig(
        pool_configs=[ipam_pool_internet]
    )
    try:
        client.networks.create("nw_internet", driver="bridge", ipam=ipam_config)
    except docker.errors.APIError:
        logging.error("[client.networks.create()] The server returns an error while creating nw_internet network")


def buildServersImages():
    try:
        client.images.build(path="servers/dns", tag="dns")
    except docker.errors.BuildError:
        logging.error("Error during the build of the DNS server")
    except docker.errors.APIError:
        logging.error("The server returns an error while building the DNS server")
    except TypeError:
        pass

    try:
        client.images.build(path="servers/http", tag="http")
    except docker.errors.BuildError:
        logging.error("Error during the build of the HTTP server")
    except docker.errors.APIError:
        logging.error("The server returns an error while building the HTTP server")
    except TypeError:
        pass

    try:
        client.images.build(path="servers/ftp", tag="ftp")
    except docker.errors.BuildError:
        logging.error("Error during the build of the FTP server")
    except docker.errors.APIError:
        logging.error("The server returns an error while building the FTP server")
    except TypeError:
        pass


def buildBotnetImages():
    try:
        client.images.build(path="botnet/botmaster", tag="tbotm")
    except docker.errors.BuildError:
        logging.error("Error during the build of the bot_master")
    except docker.errors.APIError:
        logging.error("The server returns an error while building the bot_master")
    except TypeError:
        pass
    try:
        client.images.build(path="botnet/bots", tag="tbot")
    except docker.errors.BuildError:
        logging.error("Error during the build of the bot")
    except docker.errors.APIError:
        logging.error("The server returns an error while building the bot")
    except TypeError:
        pass


def buildEmulbot():
    logging.info("Building networks")
    buildDockerNetworks()
    logging.info("Networks built")
    logging.info("Building servers images")
    buildServersImages()
    logging.info("Servers images built")
    logging.info("Building botnet images")
    buildBotnetImages()
    logging.info("Botnet images built")


def createServersContainer():
    try:
        client.containers.create(image="dns", network="nw_internet")
    except docker.errors.ImageNotFound:
        logging.error("The specified DNS image does not exist")
    except docker.errors.APIError:
        logging.error("The server returns an error while creating the DNS server")

    try:
        client.containers.create(image="ftp", network="nw_internet")
    except docker.errors.ImageNotFound:
        logging.error("The specified FTP image does not exist")
    except docker.errors.APIError:
        logging.error("The server returns ans error while creating the FTP server")

    try:
        client.containers.create(image="http", network="nw_internet")
    except docker.errors.ImageNotFound:
        logging.error("The specified HTTP image does not exist")
    except docker.errors.APIError:
        logging.error("The specified HTTP image does not exist")


def startServersContainer():
    try:
        client.containers.run(image="dns", detach=True, network="nw_internet", name="dns_server")
    except docker.errors.ContainerError:
        logging.error("The DNS container exits with a non-zero exit code and detach is False")
    except docker.errors.ImageNotFound:
        logging.error("The specified DNS image does not exist")
    except docker.errors.APIError:
        logging.error("The server returns an error while running the DNS server")

    for i in range(3):
        try:
            client.containers.run("ftp", detach=True, network="nw_internet", name="ftp_server"+str(i))
        except docker.errors.ContainerError:
            logging.error("The FTP container exists with a non-zero exit code and detach is False")
        except docker.errors.ImageNotFound:
            logging.error("The specified FTP image does not exist")
        except docker.errors.APIError:
            logging.error("The server returns an error while running the FTP server")

    for i in range(5):
        try:
            client.containers.run("http", detach=True, network="nw_internet", name="http_server"+str(i))
        except docker.errors.ContainerError:
            logging.error("The HTTP container exists with a non-zero exit code and detach is False")
        except docker.errors.ImageNotFound:
            logging.error("The specified HTTP image does not exist")
        except docker.errors.APIError:
            logging.error("The server returns an error while running the HTTP server")


def createBotnetContainer():
    try:
        client.containers.create(image="tbotm", network="nw_internet")
    except docker.errors.ImageNotFound:
        logging.error("The specified tbotm image does not exist")
    except docker.errors.APIError:
        logging.error("The server returns an error while creating the tbotm container")
    for i in range(0, NB):
        try:
            client.containers.create(image="tbot", network="nw_local")
        except docker.errors.ImageNotFound:
            logging.error("The specified tbot image does not exist")
        except docker.errors.APIError:
            logging.error("The server returns an error while creating the tbot container")


def startBotnetContainers():
    try:
        client.containers.run("tbotm", detach=True, network="nw_internet", name="bot_master")
    except docker.errors.ContainerError:
        logging.error("The tbotm container exits with a non-zero exit code and detach is False")
    except docker.errors.ImageNotFound:
        logging.error("The specified tbotm image does not exist")
    except docker.errors.APIError:
        logging.error("The server returns an error while running the tbot container")

    for i in range(0, NB):
        t = threading.Thread(target=startSingleBotContainer(i))
        t.start()
    t.join()


def startSingleBotContainer(id_bot):
    try:
        client.containers.run("tbot", detach=True, network="nw_local", name="bot_" + str(id_bot))
    except docker.errors.ContainerError:
        logging.error("The tbot container exits with a non-zero exit code and detach is False")
    except docker.errors.ImageNotFound:
        logging.error("The specified tbot image does not exist")
    except docker.errors.APIError:
        logging.error("The server returns an error while running the tbot container")



def startEmulbot():
    logging.info("Creating servers container")
    createServersContainer()
    logging.info("Servers container created")
    logging.info("Starting servers container")
    startServersContainer()
    logging.info("Servers container started")
    logging.info("Creating botnet container")
    createBotnetContainer()
    logging.info("Botnet container created")
    logging.info("Starting botnet container")
    startBotnetContainers()
    logging.info("Botnet container started")


def cleanNetwork():
    try:
        networks = client.networks.list(names=["nw_local", "nw_internet"])
    except docker.errors.APIError:
        logging.error("[client.networks.list()] The server returns an error while cleaning the network")
    for network in networks:
        try:
            network.remove()
        except docker.errors.APIError:
            logging.error("[network.remove()] The server returns an error while cleaning the network")


def stopServersContainer():
    try:
        dns_server = client.containers.get("dns_server")
    except docker.errors.NotFound:
        logging.error("The container dns_server does not exist")
    except docker.errors.APIError:
        logging.error("The server returns an error while getting the dns_server container")

    try:
        dns_server.stop()
    except docker.errors.APIError:
        logging.error("The server returns an error while stopping the dns_server container")

    for i in range(3):
        try:
            ftp_server = client.containers.get("ftp_server"+str(i))
        except docker.errors.NotFound:
            logging.error("The container ftp_server does not exist")
        except docker.errors.APIError:
            logging.error("The server returns an error while getting the ftp_server container")
        try:
            ftp_server.stop()
        except docker.errors.APIError:
            logging.error("The server returns an error while stopping the ftp_server container")

    for i in range(5):
        try:
            http_server = client.containers.get("http_server"+str(i))
        except docker.errors.NotFound:
            logging.error("The container http_server does not exist")
        except docker.errors.APIError:
            logging.error("The server returns an error while getting the http_server container")

        try:
            http_server.stop()
        except docker.errors.APIError:
            logging.error("The server returns an error while stopping the http_server container")


def removeServersContainer():
    try:
        client.containers.prune()
    except docker.errors.APIError:
        logging.error("The server returns an error at the prune function")


def stopBotnetContainers():
    for i in range(0, NB):
        t = threading.Thread(target=stopSingleBotContainer(i))
        t.start()
    t.join()
    try:
        bot_master = client.containers.get("bot_master")
    except docker.errors.NotFound:
        logging.error("The container bot does not exist")
    except docker.errors.APIError:
        logging.error("The server returns an error while getting the bot container")
    try:
        bot_master.stop()
    except docker.errors.APIError:
        logging.error("The server returns an error while stopping the bot_master container")


def stopSingleBotContainer(id_bot):
    try:
        bot = client.containers.get("bot_"+str(id_bot))
    except docker.errors.NotFound:
        logging.error("The container bot does not exist")
    except docker.errors.APIError:
        logging.error("The server returns an error while getting the bot container")
    try:
        bot.stop()
    except docker.errors.APIError:
        logging.error("The server returns an error while stopping the bot container")


def removeBotnetContainer():
    try:
        client.containers.prune()
    except docker.errors.APIError:
        logging.error("The server returns an error at the prune function")


def cleanEmulbot():
    logging.info("Cleaning servers container")
    stopServersContainer()
    removeServersContainer()
    logging.info("Servers container cleaned")
    logging.info("Cleaning botnet container")
    stopBotnetContainers()
    removeBotnetContainer()
    logging.info("Botnet container cleaned")
    logging.info("Cleaning nw_local and nw_internet")
    cleanNetwork()
    logging.info("Network cleaned")


def main():
    global NB
    parser = ArgumentParser()
    parser.add_argument('action', choices=['build', 'stop', 'clean', 'run'], type=str,
                        help="build | stop | clean | run")
    parser.add_argument("--nb", type=int, default=10, help="Number of bot to run and/or clean")
    parser.add_argument("--nv", type=int, default=0, help="")
    parser.add_argument("--pktfreq", default=None)
    parser.add_argument("--pktsize", default=None)
    parser.add_argument("--duration", default=None)

    args = parser.parse_args()
    NB = args.nb

    if args.action == "build":
        buildEmulbot()

    if args.action == "run":
        startEmulbot()

    if args.action == "clean":
        cleanEmulbot()

    # buildDockerNetworks()
    # buildServersImages()
    # buildBotnetImages()
    # createEmulbot()


if __name__ == '__main__':
    main()
