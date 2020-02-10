import docker
from argparse import ArgumentParser
import sys
import time
import coloredlogs, logging
from console_progressbar import ProgressBar

pb = ProgressBar(total=100, prefix='Processing....', suffix='Now', decimals=3, length=50, fill='#', zfill='-')

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
        client.images.build(path="botnet/botmaster", tag="merlinserver")
    except docker.errors.BuildError:
        logging.error("Error during the build of the merlinserver")
    except docker.errors.APIError:
        logging.error("The server returns an error while building the merlinserver")
    except TypeError:
        pass
    try:
        client.images.build(path="botnet/bots", tag="merlinagent")
    except docker.errors.BuildError:
        logging.error("Error during the build of the merlinserver")
    except docker.errors.APIError:
        logging.error("The server returns an error while building the merlinserver")
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
    client.containers.create("dns", network="nw_internet")


def startServersContainer():
    client.containers.run("dns", detach=True, network="nw_internet")


def createBotnetContainer():
    client.containers.create("merlinserver", network="nw_internet")
    client.containers.create("merlinagent", network="nw_local")


def startBotnetContainer():
    client.containers.run("merlinserver", detach=True, network="nw_internet")
    client.containers.run("merlinagent", detach=True, network="nw_local")


def createEmulbot():
    createServersContainer()
    startServersContainer()
    createBotnetContainer()
    startBotnetContainer()


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


def cleanContainer():
    pass


def cleanEmulbot():
    logging.info("Cleaning nw_local and nw_internet")
    cleanNetwork()
    logging.info("Network cleaned")
    logging.info("Cleaning containers")
    cleanContainer()
    logging.info("Containers cleaned")


def main():
    parser = ArgumentParser()
    parser.add_argument('action', type=str, help="build | stop | clean | run")
    parser.add_argument("--nb", default=50, help="Number of bot")
    parser.add_argument("--nv", default=0, help="")
    parser.add_argument("--pktfreq", default=None)
    parser.add_argument("--pktsize", default=None)
    parser.add_argument("--duration", default=None)

    args = parser.parse_args()

    if args.action == "build":
        buildEmulbot()

    if args.action == "clean":
        cleanEmulbot()

    # buildDockerNetworks()
    # buildServersImages()
    # buildBotnetImages()
    # createEmulbot()


if __name__ == '__main__':
    main()
