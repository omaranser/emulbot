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
    try:
        client.containers.create("dns", network="nw_internet")
    except docker.errors.ImageNotFound:
        logging.error("The specified DNS image does not exist")
    except docker.errors.APIError:
        logging.error("The server returns an error while creating the DNS server")

    try:
        client.containers.create("ftp", network="nw_internet")
    except docker.errors.ImageNotFound:
        logging.error("The specified FTP image does not exist")
    except docker.errors.APIError:
        logging.error("The server returns ans error while creating the FTP server")

    try:
        client.containers.create("http", network="nw_internet")
    except docker.errors.ImageNotFound:
        logging.error("The specified HTTP image does not exist")
    except docker.errors.APIError:
        logging.error("The specified HTTP image does not exist")


def startServersContainer():
    try:
        client.containers.run("dns", detach=True, network="nw_internet", name="dns_server")
    except docker.errors.ContainerError:
        logging.error("The DNS container exits with a non-zero exit code and detach is False")
    except docker.errors.ImageNotFound:
        logging.error("The specified DNS image does not exist")
    except docker.errors.APIError:
        logging.error("The server returns an error while running the DNS server")

    try:
        client.containers.run("ftp", detach=True, network="nw_internet", name="ftp_server")
    except docker.errors.ContainerError:
        logging.error("The FTP container exists with a non-zero exit code and detach is False")
    except docker.errors.ImageNotFound:
        logging.error("The specified FTP image does not exist")
    except docker.errors.APIError:
        logging.error("The server returns an error while running the FTP server")

    try:
        client.containers.run("http", detach=True, network="nw_internet", name="http_server")
    except docker.errors.ContainerError:
        logging.error("The HTTP container exists with a non-zero exit code and detach is False")
    except docker.errors.ImageNotFound:
        logging.error("The specified HTTP image does not exist")
    except docker.errors.APIError:
        logging.error("The server returns an error while running the HTTP server")


def createBotnetContainer():
    try:
        client.containers.create("merlinserver", network="nw_internet")
    except docker.errors.ImageNotFound:
        logging.error("The specified merlinserver image does not exist")
    except docker.errors.APIError:
        logging.error("The server returns an error while creating the merlinserver container")

    try:
        client.containers.create("merlinagent", network="nw_local")
    except docker.errors.ImageNotFound:
        logging.error("The specified merlinagent image does not exist")
    except docker.errors.APIError:
        logging.error("The server returns an error while creating the merlinagent container")


def startBotnetContainer():
    try:
        client.containers.run("merlinserver", detach=True, network="nw_internet", name="merlin_server")
    except docker.errors.ContainerError:
        logging.error("The merlinserver container exits with a non-zero exit code and detach is False")
    except docker.errors.ImageNotFound:
        logging.error("The specified merlinserver image does not exist")
    except docker.errors.APIError:
        logging.error("The server returns an error while running the merlinserver container")

    try:
        client.containers.run("merlinagent", detach=True, network="nw_local", name="merlin_agent")
    except docker.errors.ContainerError:
        logging.error("The merlinagent container exits with a non-zero exit code and detach is False")
    except docker.errors.ImageNotFound:
        logging.error("The specified merlinagent image does not exist")
    except docker.errors.APIError:
        logging.error("The server returns an error while running the merlinagent container")


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
    startBotnetContainer()
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
    client.containers.get("dns_server").stop()
    client.containers.get("ftp_server").stop()
    client.containers.get("http_server").stop()


def removeServersContainer():
    client.containers.prune()


def stopBotnetContainer():
    client.containers.get("merlin_server").stop()
    client.containers.get("merlin_agent").stop()


def removeBotnetContainer():
    client.containers.prune()


def cleanEmulbot():
    logging.info("Cleaning servers container")
    stopServersContainer()
    removeServersContainer()
    logging.info("Servers container cleaned")
    logging.info("Cleaning botnet container")
    stopBotnetContainer()
    removeBotnetContainer()
    logging.info("Botnet container cleaned")
    logging.info("Cleaning nw_local and nw_internet")
    cleanNetwork()
    logging.info("Network cleaned")


def main():
    parser = ArgumentParser()
    parser.add_argument('action', choices=['build', 'stop', 'clean', 'run'], type=str, help="build | stop | clean | run")
    parser.add_argument("--nb", default=50, help="Number of bot")
    parser.add_argument("--nv", default=0, help="")
    parser.add_argument("--pktfreq", default=None)
    parser.add_argument("--pktsize", default=None)
    parser.add_argument("--duration", default=None)

    args = parser.parse_args()

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
