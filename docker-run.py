import docker

IMAGE_TAG = 'elasticsearch:7.4.2'
CONTAINER_NAME = 'elasticsearch'


def main():
    client = docker.from_env(timeout=86400)
    container = client.containers.run(IMAGE_TAG,
                                      ports={'9300/tcp': 9300, '9200/tcp': 9200},
                                      name=CONTAINER_NAME,
                                      environment={"discovery.type": "single-node"},
                                      detach=True)
    print("Elasticsearch is running.")


if __name__ == '__main__':
    main()
