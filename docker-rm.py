import docker

IMAGE_TAG = 'elasticsearch:7.4.2'
CONTAINER_NAME = 'elasticsearch'


def main():
    client = docker.from_env(timeout=86400)
    container = client.containers.get(CONTAINER_NAME)
    container.stop()
    container.remove()
    print('Removed container!')
    client.images.remove(IMAGE_TAG)
    print('Removed image!')


if __name__ == '__main__':
    main()
