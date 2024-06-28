import PySimpleGUI as sg
import docker
import time

client: docker.DockerClient = docker.from_env()

# Algoritmos de planificación
algorithms: list[str] = ["First Come First Served (FCFS)", "Round Robin (RR)", "Shortest Process Next (SPN)", 
            "Shortest Remaining Time (SRT)", "Highest Response Ratio Next (HRRN)"]

# Layout de la ventana principal
layout = [
    [sg.Text('Comando a ejecutar'), sg.InputText(key='-COMANDO-')],
    [sg.Text('Tiempo de inicio'), sg.InputText(key='-TIEMPO_INICIO-')],
    [sg.Text('Tiempo estimado de ejecución'), sg.InputText(key='-TIEMPO_ESTIMADO-')],
    [sg.Text('Algoritmo de planificación'), sg.Combo(algorithms, key='-ALGORITMO-')],
    [sg.Button('Agregar Comando'), sg.Button('Ejecutar'), sg.Button('Mostrar Historial'), sg.Button('Salir')],
    [sg.Text('Resultados de Ejecución', size=(40, 1))],
    [sg.Output(size=(80, 20))]
]

# Create the Window
window = sg.Window('Planificador de Contenedores', layout)

# Lista para almacenar los comandos
commands = []

# Historial de comandos y algoritmos
history = []

# Función para ejecutar comandos
def ejecutar_comando(comando, inicio, duracion):
    container = client.containers.run("ubuntu", comando, detach=True)
    container.wait()
    logs = container.logs()
    return logs.decode('utf-8')

# Función para manejar la ejecución de comandos con diferentes algoritmos de planificación
def ejecutar_con_algoritmo(commands, algoritmo):
    # Aquí deberías implementar la lógica para los diferentes algoritmos de planificación.
    # Este ejemplo solo ejecuta los comandos secuencialmente.
    results = []
    for cmd, inicio, duracion in commands:
        time.sleep(float(inicio))
        result = ejecutar_comando(cmd, inicio, duracion)
        results.append((cmd, result))
        time.sleep(float(duracion))
    return results

# Loop de eventos de la ventana principal
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Salir'):
        break

    if event == 'Agregar Comando':
        comando = values['-COMANDO-']
        tiempo_inicio = values['-TIEMPO_INICIO-']
        tiempo_estimado = values['-TIEMPO_ESTIMADO-']
        commands.append((comando, tiempo_inicio, tiempo_estimado))
        print(f"Comando agregado: {comando}, Tiempo de inicio: {tiempo_inicio}, Tiempo estimado: {tiempo_estimado}")

    if event == 'Ejecutar':
        algoritmo = values['-ALGORITMO-']
        resultados = ejecutar_con_algoritmo(commands, algoritmo)
        for cmd, result in resultados:
            print(f"Resultado para '{cmd}':\n{result}")
        # Guardar en el historial
        history.append((commands.copy(), algoritmo))

    if event == 'Mostrar Historial':
        # Crear el layout para la ventana de historial
        layout_historial = [
            [sg.Text('Historial de Comandos y Algoritmos')],
            [sg.Listbox(values=[f"Comandos: {cmds}, Algoritmo: {algo}" for cmds, algo in history], size=(80, 20), key='-HISTORIAL-')],
            [sg.Button('Reejecutar'), sg.Button('Cerrar')]
        ]

        # Crear la ventana de historial
        window_historial = sg.Window('Historial', layout_historial)

        # Loop de eventos de la ventana de historial
        while True:
            event_hist, values_hist = window_historial.read()
            if event_hist in (sg.WIN_CLOSED, 'Cerrar'):
                break

            if event_hist == 'Reejecutar':
                seleccion = values_hist['-HISTORIAL-']
                if seleccion:
                    # Obtener los comandos y el algoritmo seleccionados del historial
                    index = [f"Comandos: {cmds}, Algoritmo: {algo}" for cmds, algo in history].index(seleccion[0])
                    cmds, algo = history[index]
                    # Reejecutar los comandos con el algoritmo seleccionado
                    resultados = ejecutar_con_algoritmo(cmds, algo)
                    for cmd, result in resultados:
                        print(f"Resultado para '{cmd}':\n{result}")

        window_historial.close()

window.close()