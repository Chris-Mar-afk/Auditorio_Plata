
import threading
import time
from concurrent.futures import ThreadPoolExecutor


# Configuración de la prueba
INVENTARIO_INICIAL = 20000
TOTAL_SOLICITUDES = 100
TRABAJADORES = 20
CANTIDAD_POR_SOLICITUD = 1


def prueba_sin_sincronizacion():

    inventario = [INVENTARIO_INICIAL]

    def procesar():
        disponibles = inventario[0]

        # Simular el tiempo de procesamiento
        time.sleep(0.001)

        inventario[0] = disponibles - CANTIDAD_POR_SOLICITUD

    inicio = time.perf_counter()

    with ThreadPoolExecutor(max_workers=TRABAJADORES) as ejecutor:
        list(ejecutor.map(
            lambda _: procesar(),
            range(TOTAL_SOLICITUDES)
        ))

    tiempo = time.perf_counter() - inicio

    return inventario[0], tiempo


def prueba_con_sincronizacion():

    inventario = [INVENTARIO_INICIAL]

    # Recursos del algoritmo de los cinco filósofos
    tenedores = [threading.Lock() for _ in range(5)]
    sala = threading.Semaphore(4)

    # Bloqueo del inventario, equivalente a proteger
    # la fila compartida de Oracle con SELECT FOR UPDATE
    candado_inventario = threading.Lock()

    contador = [0]
    candado_contador = threading.Lock()

    def procesar():

        # Asignar un filósofo
        with candado_contador:
            filosofo = contador[0] % 5
            contador[0] += 1

        izquierdo = filosofo
        derecho = (filosofo + 1) % 5

        with sala:
            with tenedores[izquierdo]:
                with tenedores[derecho]:
                    with candado_inventario:

                        disponibles = inventario[0]

                        time.sleep(0.001)

                        inventario[0] = (
                            disponibles - CANTIDAD_POR_SOLICITUD
                        )

    inicio = time.perf_counter()

    with ThreadPoolExecutor(max_workers=TRABAJADORES) as ejecutor:
        list(ejecutor.map(
            lambda _: procesar(),
            range(TOTAL_SOLICITUDES)
        ))

    tiempo = time.perf_counter() - inicio

    return inventario[0], tiempo


# Ejecutar las dos pruebas
print("COMPARACIÓN DE CONCURRENCIA")
print("----------------------------")

disponibles_sin, tiempo_sin = prueba_sin_sincronizacion()

disponibles_con, tiempo_con = prueba_con_sincronizacion()

esperado = INVENTARIO_INICIAL - TOTAL_SOLICITUDES

print("\nSIN SINCRONIZACIÓN")
print("Inventario final:", disponibles_sin)
print("Inventario esperado:", esperado)
print("Tiempo:", round(tiempo_sin, 4), "segundos")

print("\nCON SINCRONIZACIÓN")
print("Inventario final:", disponibles_con)
print("Inventario esperado:", esperado)
print("Tiempo:", round(tiempo_con, 4), "segundos")

print("\nRESULTADO")
print("----------------------------")

if disponibles_sin != esperado:
    print("Sin sincronización: se detectó una inconsistencia.")
else:
    print("Sin sincronización: no se detectó inconsistencia.")

if disponibles_con == esperado:
    print("Con sincronización: inventario correcto.")
else:
    print("Con sincronización: inventario incorrecto.")
