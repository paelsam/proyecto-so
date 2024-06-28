import psycopg2
# import datetime

conn = psycopg2.connect(
    database="postgres",
    user="postgres",
    password="myStrong#Password",
    host="localhost",
    port="5432",
)

# Getters


def get_comandos():
    with conn.cursor() as cur:
        cur.execute("""
                SELECT 
                    c.comando_id,
                    c.comando,
                    con.contenedor
                FROM comando c
                JOIN contenedor con ON c.contenedor_id = con.contenedor_id
        """)
        response = cur.fetchall()
        cur.close()
        return response

def comando_existe(comando: str) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                comando_id
            FROM
                comando
            WHERE
                comando = %s
        """,
            (comando,),
        )
        response = cur.fetchone()
        cur.close()
        return response is not None

def get_comando(comando: str) -> tuple:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                c.comando_id,
                c.comando,
                con.contenedor_id,
                con.contenedor
            FROM
                comando c
            JOIN
                contenedor con ON c.contenedor_id = con.contenedor_id
            WHERE
                c.comando = %s
        """, (comando,))
        response = cur.fetchone()
        cur.close()
        return response


def get_comando_tiempos(tiempo_id, comando_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                c.comando_id,
                rt.registro_tiempo_id,
                c.comando,
                con.contenedor,
                rt.tiempo_inicio,
                rt.tiempo_fin
            FROM
                registro_tiempo rt
            JOIN
                comando c ON rt.comando_id = c.comando_id
            JOIN
                contenedor con ON c.contenedor_id = con.contenedor_id
            WHERE
                rt.registro_tiempo_id = %s
                AND rt.comando_id = %s
        """,
            (comando_id, tiempo_id),
        )
        response = cur.fetchall()
        cur.close()
        return response


def get_historial_ejecuciones():
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                e.ejecucion_id,
                e.algoritmo_planificacion,
                e.fecha_ejecucion,
                e.turnaround_time_promedio,
                e.response_time_promedio,
                json_agg(
                    json_build_object(
                        'comando', c.comando,
                        'contenedor', con.contenedor,
                        'tiempo_inicio', rt.tiempo_inicio,
                        'tiempo_fin', rt.tiempo_fin,
                        'turnaround_time', rt.turnaround_time,
                        'response_time', rt.response_time
                    )
                ) AS comandos
            FROM 
                ejecucion e
            JOIN 
                comando_ejecucion ce ON e.ejecucion_id = ce.ejecucion_id
            JOIN
                registro_tiempo rt ON ce.registro_tiempo_id = rt.registro_tiempo_id
            JOIN
                comando c ON rt.comando_id = c.comando_id
            JOIN 
                contenedor con ON c.contenedor_id = con.contenedor_id
            GROUP BY
                e.ejecucion_id, e.algoritmo_planificacion, e.fecha_ejecucion
            ORDER BY
                e.ejecucion_id
        """)
        response = cur.fetchall()
        cur.close()
        return response


def get_comandos_por_ejecucion(ejecucion_id):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                c.comando_id,
                rt.registro_tiempo_id,
                c.comando,
                con.contenedor,
                rt.tiempo_inicio,
                rt.tiempo_fin
            FROM
                comando_ejecucion ce
            JOIN
                registro_tiempo rt ON ce.registro_tiempo_id = rt.registro_tiempo_id
            JOIN
                comando c ON rt.comando_id = c.comando_id
            JOIN
                contenedor con ON c.contenedor_id = con.contenedor_id
            WHERE
                ce.ejecucion_id = %s
        """,
            (ejecucion_id,),
        )
        response = cur.fetchall()
        cur.close()
        return response


# Setters

# Se agrega un comando nuevo
def insert_comando(comando, contenedor, tiempo_inicio, tiempo_fin):
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO contenedor (contenedor)
                VALUES (%s)
                RETURNING contenedor_id;
            """,
                (contenedor,),
            )

            contenedor_id = cur.fetchone()[0]

            cur.execute(
                """
                INSERT INTO comando (comando, contenedor_id)
                VALUES (%s, %s)
                RETURNING comando_id;
            """,
                (
                    comando,
                    contenedor_id,
                ),
            )

            comando_id = cur.fetchone()[0]

            cur.execute(
                """
                INSERT INTO registro_tiempo (comando_id, tiempo_inicio, tiempo_fin)
                VALUES (%s, %s, %s)
                RETURNING registro_tiempo_id;
            """,
                (comando_id, tiempo_inicio, tiempo_fin),
            )

            registro_tiempo_id = cur.fetchone()[0]

            conn.commit()
            return comando_id, contenedor_id, registro_tiempo_id
    except (Exception, psycopg2.Error) as error:
        print(error)
        conn.rollback()
    finally:
        if cur:
            cur.close()

# Se agrega los tiempos de un comando que ya existe
def insert_comando_existente(comando: str, tiempo_inicio: int, tiempo_fin: int):
    try:
        with conn.cursor() as cur:
            comando_response = get_comando(comando)
            (comando_id, comando, contenedor_id, _) = comando_response
            
            cur.execute(
                """
                INSERT INTO registro_tiempo (comando_id, tiempo_inicio, tiempo_fin)
                VALUES (%s, %s, %s)
                RETURNING registro_tiempo_id;
            """,
                (comando_id, tiempo_inicio, tiempo_fin),
            )

            registro_tiempo_id = cur.fetchone()[0]

            conn.commit()
            return comando_id, contenedor_id, registro_tiempo_id
    except (Exception, psycopg2.Error) as error:
        print(error)
        conn.rollback()
    finally:
        if cur:
            cur.close()
            

def intert_turnaround_time_and_response_time(tiempos: list):
    try:
        with conn.cursor() as cur:
            for tiempo in tiempos:
                cur.execute("""
                    UPDATE registro_tiempo
                    SET turnaround_time = %s, response_time = %s
                    WHERE registro_tiempo_id = %s
                """, (tiempo[1], tiempo[2], tiempo[0]))
            conn.commit()
            return True
    except (Exception, psycopg2.Error) as error:
        print(error)
        conn.rollback()
        return False
    finally:
        if cur:
            cur.close()


def insert_comandos_ejecucion(
    lista_comandos,
    algoritmo_planificacion,
    fecha_ejecucion,
    turnaround_time_promedio,
    response_time_promedio,
):
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO ejecucion (algoritmo_planificacion, fecha_ejecucion, turnaround_time_promedio, response_time_promedio)
                VALUES (%s, %s, %s, %s)
                RETURNING ejecucion_id;
            """,
                (
                    algoritmo_planificacion,
                    fecha_ejecucion,
                    turnaround_time_promedio,
                    response_time_promedio,
                ),
            )

            ejecucion_id = cur.fetchone()[0]

            for comando in lista_comandos:
                (comando_id, contenedor_id, registro_tiempo_id) = insert_comando(
                    comando[0], comando[1], comando[2], comando[3]
                )

                cur.execute("""
                    INSERT INTO comando_ejecucion (ejecucion_id, registro_tiempo_id)
                    VALUES (%s, %s)
                """,
                    (ejecucion_id, registro_tiempo_id),
                )
            conn.commit()
            return ejecucion_id
    except (Exception, psycopg2.Error) as error:
        print(error)
        conn.rollback()
    finally:
        if cur:
            cur.close()




