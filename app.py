import datetime
import re
import time
from docker_methods.init import create_container, start_container, stop_container
from db.config import (
    get_comandos,
    get_historial_ejecuciones,
    insert_comando,
    comando_existe,
    get_comando,
    insert_comando_existente,
    intert_turnaround_time_and_response_time,
)


# Comandos que se van a ejecutar
"""
    Comando
    0: comando_id
    1: comando
    2: contenedor
    3: tiempo_inicio
    4: tiempo_fin
"""
comandos_a_ejecutar = []

# Registro de la ejecucion actual
"""
    Ejecucion
    0: algoritmo_planificacion
    1: fecha_ejecucion
    2: turnaround_time_promedio
    3: response_time_promedio
"""
ejecucion = ()

"""
    Obtener historial de comandos
    0: comando_id
    1: comando
    2: contenedor
"""
historial_comandos = get_comandos()

"""
    Obtener historial de ejecuciones
    0: ejecucion_id
    1: algoritmo_planificacion
    2: fecha_ejecucion
    3: turnaround_time_promedio
    4: response_time_promedio
    5: comandos (json)
        0: comando
        1: contenedor
        2: tiempo_inicio
        3: tiempo_fin
        4: turnaround_time
        5: response_time
"""
historial_ejecuciones = get_historial_ejecuciones()


# Insertar un comando en la base de datos y crear el contenedor
def insertar_comando(comando: str, tiempo_inicio: int, tiempo_fin: int):
    try:
        # verificar si el comando ya existe en la base de datos
        if comando_existe(comando.strip()):
            (comando_id, comando_str, contenedor_id, contenedor_str) = get_comando(
                comando
            )
            create_container(contenedor_str, comando_str)
            (comando_id, contenedor_id, registro_tiempo_id) = insert_comando_existente(
                comando, tiempo_inicio, tiempo_fin
            )
            comandos_a_ejecutar.append(
                (
                    comando_id,
                    comando_str,
                    contenedor_str,
                    tiempo_inicio,
                    tiempo_fin,
                    registro_tiempo_id,
                )
            )
        else:
            contenedor: str = comando.replace(" ", "_")
            contenedor = re.sub(
                r"[^a-zA-Z0-9_]+", "_", contenedor
            ) + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            create_container(contenedor, comando)
            (comando_id, contenedor_id, registro_tiempo_id) = insert_comando(
                comando, contenedor, tiempo_inicio, tiempo_fin
            )
            comandos_a_ejecutar.append(
                (
                    comando_id,
                    comando.strip(),
                    contenedor,
                    tiempo_inicio,
                    tiempo_fin,
                    registro_tiempo_id,
                )
            )
    except Exception as e:
        print(e)


# Algoritmos de planificacion


def fcfs(comandos: list):
    comandos = sorted(comandos, key=lambda x: x[3])
    tiempo_actual = 0
    # tripla con (registro_tiempo_id, turnaround_time, response_time)
    tiempos = []

    for comando in comandos:
        (
            comando_id,
            comando_str,
            contenedor,
            tiempo_inicio,
            tiempo_fin,
            registro_tiempo_id,
        ) = comando

        if tiempo_actual < tiempo_inicio:
            time.sleep(tiempo_inicio - tiempo_actual)
            tiempo_actual = tiempo_inicio

        # Response time
        response_time = tiempo_actual - tiempo_inicio

        print(f"Comando {comando_id}: {comando_str}")

        start_container(contenedor)

        time.sleep(tiempo_fin)

        stop_container(contenedor)

        tiempo_actual += tiempo_fin

        # Turnaround time
        turnaround_time = tiempo_actual - tiempo_inicio
        tiempos.append((registro_tiempo_id, turnaround_time, response_time))

        print(f"Turnaround time: {turnaround_time}")
        print(f"Response time: {response_time}")

    intert_turnaround_time_and_response_time(tiempos)

    avg_turnaround_time = sum(
        [turnaround_time[1] for turnaround_time in tiempos]
    ) / len([turnaround_time[1] for turnaround_time in tiempos])
    avg_response_time = sum([response_time[2] for response_time in tiempos]) / len(
        [response_time[2] for response_time in tiempos]
    )

    print(f"Turnaround time promedio: {avg_turnaround_time}")
    print(f"Response time promedio: {avg_response_time}")

    return avg_turnaround_time, avg_response_time

def round_robin(comandos:list, quantum: int = 2): 
    # TDOO: implementar el round robin
    comandos = sorted(comandos, key=lambda x: x[3])


# Comandos de prueba
print(insertar_comando("ps ef", 0, 1))
print(insertar_comando("sleep 5", 5, 5))
print(insertar_comando("ls", 5, 1))

print(fcfs(comandos_a_ejecutar))
