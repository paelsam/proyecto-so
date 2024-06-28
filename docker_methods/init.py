import docker

client = docker.from_env()

def is_container_exist(container_name):
    try:
        client.containers.get(container_name)
        return True
    except docker.errors.NotFound:
        return False
    
def create_container(container_name: str, command: str, image: str = 'alpine') -> docker.models.containers.Container:
    if is_container_exist(container_name):
        print("El contenedor ya existe")
        return False
    else:
        container = client.containers.create(
            image,
            command,
            name=container_name,
            detach=True,
        )
        return container

def start_container(container_name: str):
    container = client.containers.get(container_name)
    container.start()
    return container

def stop_container(container_name: str):
    container = client.containers.get(container_name)
    container.stop()
    return container