import docker

client = docker.DockerClient(base_url='unix://var/run/docker.sock')

def buildDockerNetworks():
    ipam_pool_local = docker.types.IPAMPool(
        subnet='10.0.0.0/8',
        gateway='10.255.255.254'
    )
    ipam_config = docker.types.IPAMConfig(
        pool_configs=[ipam_pool_local]
    )
    client.networks.create("nw_local",
                           driver="bridge",
                           ipam=ipam_config
    )
    ipam_pool_internet = docker.types.IPAMPool(
        subnet='193.168.0.0/24',
        gateway='193.168.0.254'
    )
    ipam_config = docker.types.IPAMConfig(
        pool_configs=[ipam_pool_internet]
    )
    client.networks.create("nw_internet",
                           driver="bridge",
                           ipam=ipam_config
    )

def buildServersImages():
    client.images.build(path="servers/dns",
                        tag="dns"
    )
    client.images.build(path="servers/http",
                        tag="http"
    )
    client.images.build(path="servers/firewall",
                        tag="firewall"
    )
    client.images.build(path="servers/ftp",
                        tag="ftp"
    )

def buildBotnetImages():
    client.images.build(path="botnet/botmaster",
                        tag="merlinserver"
                        )
    client.images.build(path="botnet/bots",
                        tag="merlinagent"
                        )

def buildEmulbot():
    buildDockerNetworks()
    buildServersImages()
    buildBotnetImages()

def createServersContainer():
    client.containers.create("dns",
                             network="nw_internet"
                             )


def startServersContainer():
    client.containers.run("dns",
                          detach=True,
                          network="nw_internet")

def createBotnetContainer():
    client.containers.create("merlinserver",
                             network="nw_internet"
                             )
    client.containers.create("merlinagent",
                             network="nw_local"
                             )
def startBotnetContainer():
    client.containers.run("merlinserver",
                          detach=True,
                          network="nw_internet"
                          )
    client.containers.run("merlinagent",
                          detach=True,
                          network="nw_local"
                          )

def createEmulbot():
    createServersContainer()
    startServersContainer()
    createBotnetContainer()
    startBotnetContainer()

def main():
    # buildDockerNetworks()
    buildServersImages()
    buildBotnetImages()
    createEmulbot()

if __name__ == '__main__':
    main()
