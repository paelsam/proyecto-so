import PySimpleGUI as sg
import datetime
from app import insertar_comando, fcfs, round_robin, spn, srt, hrrn, comandos_a_ejecutar
from db.config import get_comandos_por_ejecucion, insert_comandos_ejecucion, get_historial_ejecuciones, get_average_turnaround_time_and_response_time
from docker_methods.init import remove_container

# Algoritmos de planificación
algorithms = ["First Come First Served (FCFS)", "Round Robin (RR)", "Shortest Process Next (SPN)", 
            "Shortest Remaining Time (SRT)", "Highest Response Ratio Next (HRRN)"]

sg.theme('DarkGreen6')

# Layout de la ventana principal
layout = [
    [sg.Text('Comando a ejecutar'), sg.InputText(key='-COMANDO-')],
    [sg.Text('Tiempo de inicio (segundos)'), sg.InputText(key='-TIEMPO_INICIO-')],
    [sg.Text('Tiempo estimado de ejecución (segundos)'), sg.InputText(key='-TIEMPO_ESTIMADO-')],
    [sg.Button('Agregar Comando', button_color=('green', 'white'))],
    [sg.Text('Comandos agregados:')],
    [sg.Listbox(values=[], size=(60, 5), key='-LISTA_COMANDOS-')],
    [sg.Button('Borrar Comando Seleccionado', button_color=('red', 'white')), sg.Button('Borrar Todos los Comandos', button_color=('red', 'white'))],
    [sg.Text('Algoritmo de planificación'), sg.Combo(algorithms, key='-ALGORITMO-')],
    [sg.Button('Ejecutar', button_color=('green', 'white')), sg.Button('Mostrar Historial', button_color=('blue', 'white')), sg.Button('Salir', button_color=('red', 'white'))],
    [sg.Text('Resultados de Ejecución', size=(40, 1))],
    [sg.Output(size=(80, 20), key = '-RESULTADOS-')]
]

# Create the Window
window = sg.Window('Planificador de Contenedores', layout)

# Loop de eventos de la ventana principal
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Salir'):
        break

    if event == 'Agregar Comando':
        comando = values['-COMANDO-']
        tiempo_inicio = values['-TIEMPO_INICIO-']
        tiempo_estimado = values['-TIEMPO_ESTIMADO-']
        
        if comando and tiempo_inicio and tiempo_estimado:
            try:
                tiempo_inicio = int(tiempo_inicio)
                tiempo_estimado = int(tiempo_estimado)
                insertar_comando(comando, tiempo_inicio, tiempo_estimado)
                window['-LISTA_COMANDOS-'].update(values=[f"{comando[1]} (Inicio: {comando[3]}s, Estimado: {comando[4]}s)" for comando in comandos_a_ejecutar])
                print(f"Comando agregado: {comando}, Tiempo de inicio: {tiempo_inicio}s, Tiempo estimado: {tiempo_estimado}s")
                
                # Limpiar los input de -COMANDO-, -TIEMPO_INICIO- y -TIEMPO_ESTIMADO-
                window['-COMANDO-'].update(value='')
                window['-TIEMPO_INICIO-'].update(value='')
                window['-TIEMPO_ESTIMADO-'].update(value='')
            except ValueError:
                print("Por favor, ingrese valores numéricos para los tiempos.")
        else:
            print("Por favor, complete todos los campos.")
    if event == 'Borrar Comando Seleccionado':
        seleccion = values['-LISTA_COMANDOS-']
        if seleccion:
            indice = window['-LISTA_COMANDOS-'].GetIndexes()[0]
            remove_container(comandos_a_ejecutar[indice][2])
            del comandos_a_ejecutar[indice]
            window['-LISTA_COMANDOS-'].update(values=[f"{comando[1]} (Inicio: {comando[3]}s, Estimado: {comando[4]}s)" for comando in comandos_a_ejecutar])
            print("Comando seleccionado borrado.")
        else:
            print("Por favor, seleccione un comando para borrar.")

    if event == 'Borrar Todos los Comandos':
        for comando in comandos_a_ejecutar:
            remove_container(comando[2])
        comandos_a_ejecutar.clear()
        window['-LISTA_COMANDOS-'].update(values=[])
        print("Todos los comandos han sido borrados.")

    if event == 'Ejecutar':
        # Limpiar el output anterior
        window['-RESULTADOS-'].update(value='')
        algoritmo = values['-ALGORITMO-'].strip()
        avg_turnaround, avg_response = None, None
        if algoritmo and comandos_a_ejecutar:
            print(f"Ejecutando con algoritmo: {algoritmo}")
            print("Espere, por favor...\n")
            
            if "FCFS" in algoritmo:
                avg_turnaround, avg_response = fcfs(comandos_a_ejecutar)
            elif "RR" in algoritmo:
                avg_turnaround, avg_response = round_robin(comandos_a_ejecutar, 2)
            elif "SPN" in algoritmo:
                avg_turnaround, avg_response = spn(comandos_a_ejecutar)
            elif "SRT" in algoritmo:
                avg_turnaround, avg_response = srt(comandos_a_ejecutar)
            elif "HRRN" in algoritmo:
                avg_turnaround, avg_response = hrrn(comandos_a_ejecutar)
            
            insert_comandos_ejecucion(comandos_a_ejecutar, algoritmo, datetime.datetime.now(), avg_turnaround, avg_response)
            
            print(f"Turnaround time promedio: {avg_turnaround}")
            print(f"Response time promedio: {avg_response}")
            
            comandos_a_ejecutar.clear()
            window['-LISTA_COMANDOS-'].update(values=[])
        else:
            print("Por favor, seleccione un algoritmo y agregue comandos antes de ejecutar.")

    if event == 'Mostrar Historial':
        
        historial_ejecuciones = get_historial_ejecuciones()
        
        # Crear el layout para la ventana de historial
        layout_historial = [
            [sg.Text('Historial de Ejecuciones')],
            [sg.Listbox(values=[f"ID: {h[0]}, Algoritmo: {h[1]}, Fecha: {h[2]}" for h in historial_ejecuciones], 
                        size=(60, 10), key='-HISTORIAL-')],
            [sg.Button('Ver Detalles'), sg.Button('Reejecutar'), sg.Button('Cerrar')]
        ]

        # Crear la ventana de historial
        window_historial = sg.Window('Historial', layout_historial)

        # Loop de eventos de la ventana de historial
        while True:
            event_hist, values_hist = window_historial.read()
            if event_hist in (sg.WIN_CLOSED, 'Cerrar'):
                break

            if event_hist == 'Ver Detalles':
                seleccion = values_hist['-HISTORIAL-']
                if seleccion:
                    ejecucion_id = int(seleccion[0].split(',')[0].split(':')[1].strip())
                    comandos = get_comandos_por_ejecucion(ejecucion_id)
                    detalles = ""
                    # Mostrar los comandos, su turnaround time y response time; y el promedio de turnaround time y response time
                    for c in comandos:
                        detalles += f"Comando: {c[2]}, Inicio: {c[4]}s, Fin: {c[5]}s, Turnaround time: {c[6]}s, Response time: {c[7]}s\n"
                    
                    turnaround_time_promedio, response_time_promedio = get_average_turnaround_time_and_response_time(ejecucion_id)
                    
                    detalles += f"Turnaround time promedio: {turnaround_time_promedio}\nResponse time promedio: {response_time_promedio}\n\n"
                    
                    sg.popup_scrolled(detalles, title='Detalles de la Ejecución')

            if event_hist == 'Reejecutar':
                seleccion = values_hist['-HISTORIAL-']
                if seleccion:
                    ejecucion_id = int(seleccion[0].split(',')[0].split(':')[1].strip())
                    comandos = get_comandos_por_ejecucion(ejecucion_id)
                    for c in comandos:
                        insertar_comando(c[2], c[4], c[5])
                    comandos_agregados = [(c[2], c[4], c[5]) for c in comandos]
                    window['-LISTA_COMANDOS-'].update(values=[f"{cmd} (Inicio: {ti}s, Estimado: {te}s)" for cmd, ti, te in comandos_agregados])
                    # Limpiar el output anterior
                    window['-RESULTADOS-'].update(value='')
                    print("Comandos cargados para reejecutar. Seleccione un algoritmo y presione 'Ejecutar'.")
                    window_historial.close()
        window_historial.close()

window.close()