import datetime
import re
import time
from docker_methods.init import (
    create_container,
    start_container,
    stop_container,
    pause_container,
)
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


# Algoritmo de planificacion Round Robin
def round_robin(comandos: list, quantum: int = 2):
    comandos = sorted(comandos, key=lambda x: x[3])

    tiempo_actual = 0
    tiempos = []
    cola = []

    for comando in comandos:
        (
            comando_id,
            comando_str,
            contenedor,
            tiempo_inicio,
            tiempo_fin,
            registro_tiempo_id,
        ) = comando
        cola.append(
            [
                comando_id,
                comando_str,
                contenedor,
                tiempo_inicio,
                tiempo_fin,
                registro_tiempo_id,
                0,
            ]
        )

    while cola:
        comando = cola.pop(0)
        (
            comando_id,
            comando_str,
            contenedor,
            tiempo_inicio,
            tiempo_fin,
            registro_tiempo_id,
            tiempo_ejecutado,
        ) = comando

        if tiempo_actual < tiempo_inicio:
            time.sleep(tiempo_inicio - tiempo_actual)
            tiempo_actual = tiempo_inicio

        print(f"Comando {comando_id}: {comando_str}")

        start_container(contenedor)

        if tiempo_ejecutado + quantum >= tiempo_fin:
            time.sleep(tiempo_fin - tiempo_ejecutado)
            stop_container(contenedor)
            tiempo_actual += tiempo_fin - tiempo_ejecutado

            # Turnaround time
            turnaround_time = tiempo_actual - tiempo_inicio

            # Response time
            response_time = turnaround_time - tiempo_fin

            tiempos.append([registro_tiempo_id, turnaround_time, response_time])

            print(f"Turnaround time: {turnaround_time}")
            print(f"Response time: {response_time}")
        else:
            time.sleep(quantum)
            pause_container(contenedor)
            tiempo_actual += quantum
            comando[6] = tiempo_ejecutado + quantum
            cola.append(comando)        

    intert_turnaround_time_and_response_time(tiempos)

    # Añadir el turnaround time y response time promedio a la base de datos
    avg_turnaround_time = sum(
        [turnaround_time[1] for turnaround_time in tiempos]
    ) / len([turnaround_time[1] for turnaround_time in tiempos])
    avg_response_time = sum([response_time[2] for response_time in tiempos]) / len(
        [response_time[2] for response_time in tiempos]
    )

    print(f"Turnaround time promedio: {avg_turnaround_time}")
    print(f"Response time promedio: {avg_response_time}")

    return avg_turnaround_time, avg_response_time

# Algoritmo de planificacion SPN (Shortest Process Next)
def spn(comandos: list):
    comandos = sorted(comandos, key=lambda x: x[4]) # Ordenar en base al tiempo_fin
    tiempo_actual = 0
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

# Algoritmo de planificación SRT (Shortest Response Time)
def srt(comandos: list):
    tiempo_actual = 0
    tiempos = []
    cola = []
    
    # Ordenamos los comandos por tiempo de inicio
    comandos = sorted(comandos, key=lambda x: x[3])
    
    while comandos or cola:
        # Agregamos a la cola los comandos que ya pueden comenzar
        while comandos and comandos[0][3] <= tiempo_actual:
            comando = comandos.pop(0)
            cola.append([*comando, 0])  # Agregamos tiempo_ejecutado al final
        
        if not cola:
            # Si no hay comandos en la cola, avanzamos el tiempo
            tiempo_actual = comandos[0][3]
            continue
        
        # Seleccionamos el proceso con el menor tiempo restante
        cola.sort(key=lambda x: x[4] - x[6])
        comando = cola[0]
        
        comando_id, comando_str, contenedor, tiempo_inicio, tiempo_fin, registro_tiempo_id, tiempo_ejecutado = comando
        
        print(f"Comando {comando_id}: {comando_str}")
        
        start_container(contenedor)
        
        # Calculamos cuánto tiempo ejecutar
        tiempo_restante = tiempo_fin - tiempo_ejecutado
        tiempo_a_ejecutar = min(tiempo_restante, 1)  # Ejecutamos en intervalos de 1 segundo
        
        time.sleep(tiempo_a_ejecutar)
        tiempo_actual += tiempo_a_ejecutar
        comando[6] += tiempo_a_ejecutar
        
        if comando[6] >= tiempo_fin:
            # El comando ha terminado
            stop_container(contenedor)
            
            turnaround_time = tiempo_actual - tiempo_inicio
            response_time = turnaround_time - tiempo_fin
            
            tiempos.append((registro_tiempo_id, turnaround_time, response_time))
            
            print(f"Turnaround time: {turnaround_time}")
            print(f"Response time: {response_time}")
            
            cola.pop(0)
        else:
            pause_container(contenedor)
    
    intert_turnaround_time_and_response_time(tiempos)
    
    avg_turnaround_time = sum(t[1] for t in tiempos) / len(tiempos)
    avg_response_time = sum(t[2] for t in tiempos) / len(tiempos)
    
    print(f"Turnaround time promedio: {avg_turnaround_time}")
    print(f"Response time promedio: {avg_response_time}")
    
    return avg_turnaround_time, avg_response_time
    

# Comandos de prueba
insertar_comando("ps ef", 0, 1)
insertar_comando("sleep 5", 5, 5)
insertar_comando("ls -l", 5, 1)

# print(fcfs(comandos_a_ejecutar))
# print(round_robin(comandos_a_ejecutar, 2))
# print(spn(comandos_a_ejecutar))
print(srt(comandos_a_ejecutar))

