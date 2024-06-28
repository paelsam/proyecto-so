CREATE TABLE contenedor(
    contenedor_id SERIAL PRIMARY KEY,
    contenedor VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE comando(
    comando_id SERIAL PRIMARY KEY,
    comando VARCHAR(255) NOT NULL UNIQUE,
    contenedor_id INT NOT NULL,
    FOREIGN KEY (contenedor_id) REFERENCES contenedor(contenedor_id)    
);

CREATE TABLE registro_tiempo(
    registro_tiempo_id SERIAL PRIMARY KEY,
    comando_id INT NOT NULL,
    tiempo_inicio INT NOT NULL,
    tiempo_fin INT NOT NULL,
    turnaround_time DECIMAL(5,3),
    response_time DECIMAL(5,3),
    FOREIGN KEY (comando_id) REFERENCES comando(comando_id)
)

CREATE TABLE ejecucion(
    ejecucion_id SERIAL PRIMARY KEY,
    algoritmo_planificacion VARCHAR(255) NOT NULL,
    fecha_ejecucion TIMESTAMP NOT NULL,
    turnaround_time_promedio DECIMAL(5,3) NOT NULL,
    response_time_promedio DECIMAL(5,3) NOT NULL
);

CREATE TABLE comando_ejecucion(
    ejecucion_id INT NOT NULL,
    registro_tiempo_id INT NOT NULL,
    FOREIGN KEY (ejecucion_id) REFERENCES ejecucion(ejecucion_id),
    FOREIGN KEY (registro_tiempo_id) REFERENCES registro_tiempo(registro_tiempo_id),
    PRIMARY KEY (ejecucion_id, registro_tiempo_id)
);
