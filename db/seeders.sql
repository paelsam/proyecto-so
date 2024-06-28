-- Contenedor
INSERT INTO contenedor (contenedor) VALUES
('ls_20240627120000'),
('ps_20240627120100'),
('cat_etc_passwd_20240627120200'),
('echo_hello_world_20240627120300'),
('whoami_20240627120400');

-- Comando
INSERT INTO comando (comando, contenedor_id) VALUES
('ls', 1),
('ps', 2),
('cat /etc/passwd', 3),
('echo "Hello, World!"', 4),
('whoami', 5);

-- Registro_tiempo
INSERT INTO registro_tiempo (comando_id, tiempo_inicio, tiempo_fin, turnaround_time, response_time) VALUES
(1, 0, 2, 2.000, 0.000),
(2, 1, 4, 3.000, 1.000),
(3, 2, 7, 5.000, 2.000),
(4, 3, 5, 2.000, 3.000),
(5, 4, 6, 2.000, 4.000);

-- Ejecucion
INSERT INTO ejecucion (algoritmo_planificacion, fecha_ejecucion, turnaround_time_promedio, response_time_promedio) VALUES
('First Come First Served (FCFS)', '2024-06-27 12:05:00', 2.800, 2.000),
('Round Robin (quantum de 2 segundos)', '2024-06-27 12:10:00', 3.200, 1.800),
('Shortest Process Next (SPN)', '2024-06-27 12:15:00', 2.600, 1.600),
('Shortest Remaining Time (SRT)', '2024-06-27 12:20:00', 2.400, 1.400),
('HRRN', '2024-06-27 12:25:00', 3.000, 2.200);

-- Comando_ejecucion
INSERT INTO comando_ejecucion (ejecucion_id, registro_tiempo_id) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4),
(5, 5);