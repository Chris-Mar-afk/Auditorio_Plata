
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
import time

URL = "http://127.0.0.1:5000/solicitar"


def enviar_solicitud(numero):

    datos = {
        "nombre": f"Usuario Prueba {numero}",
        "correo": f"usuario{numero}@prueba.com",
        "telefono": "4921234567",
        "cantidad": "1"
    }

    contenido = urllib.parse.urlencode(datos).encode("utf-8")

    solicitud = urllib.request.Request(
        URL,
        data=contenido,
        method="POST"
    )

    try:
        with urllib.request.urlopen(solicitud, timeout=60) as respuesta:

            pagina = respuesta.read().decode("utf-8")

            # Detectar solicitud aceptada
            if "Solicitud validada" in pagina:
                return "Aceptada"

            # Detectar falta de boletos
            if "No hay suficientes boletos disponibles." in pagina:
                return "Rechazada"

            print("\nRESPUESTA INESPERADA EN SOLICITUD:", numero)
            print("Contenido recibido:", pagina[:1000])

            return "Respuesta inesperada"

    except Exception as error:

        print("\nERROR EN SOLICITUD:", numero)
        print("Detalle:", error)

        return f"Error: {error}"


print("Iniciando prueba de concurrencia...")
print("Solicitudes programadas: 100")
print("Trabajadores simultáneos: 20")

inicio = time.perf_counter()

# Enviar 100 solicitudes utilizando 20 trabajadores
with ThreadPoolExecutor(max_workers=20) as ejecutor:

    resultados = list(
        ejecutor.map(enviar_solicitud, range(1, 101))
    )

fin = time.perf_counter()

tiempo_total = fin - inicio

aceptadas = resultados.count("Aceptada")
rechazadas = resultados.count("Rechazada")
errores = sum(r.startswith("Error:") for r in resultados)
inesperadas = resultados.count("Respuesta inesperada")

print("\nRESULTADOS DE LA PRUEBA")
print("-------------------------")
print("Solicitudes enviadas:", len(resultados))
print("Aceptadas:", aceptadas)
print("Rechazadas:", rechazadas)
print("Errores:", errores)
print("Respuestas inesperadas:", inesperadas)
print("Tiempo total:", round(tiempo_total, 2), "segundos")

# Comprobar los requisitos de la prueba
if (
    len(resultados) == 100
    and aceptadas == 100
    and errores == 0
    and inesperadas == 0
    and tiempo_total <= 60
):
    print("\nPRUEBA DE CONCURRENCIA: APROBADA")
else:
    print("\nPRUEBA DE CONCURRENCIA: NO APROBADA")
