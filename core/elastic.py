import docker
from config import IMAGE_TAG, CONTAINER_NAME


def start_container():
    client = docker.from_env(timeout=86400)
    container = client.containers.run(IMAGE_TAG,
                                      ports={'9300/tcp': 9300, '9200/tcp': 9200},
                                      name=CONTAINER_NAME,
                                      environment={"discovery.type": "single-node"},
                                      detach=True)
    print("Elasticsearch is running.")


def stop_rm_container():
    client = docker.from_env(timeout=86400)
    container = client.containers.get(CONTAINER_NAME)
    container.stop()
    container.remove()
    print('Removed container!')
    client.images.remove(IMAGE_TAG)
    print('Removed image!')