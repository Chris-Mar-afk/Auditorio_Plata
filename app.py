
from flask import Flask, render_template, request, send_from_directory
import re
import threading

from concurrencia import procesar_solicitud
from generador_pdf import generar_boleto_pdf

app = Flask(__name__)
@app.route("/boletos/<path:nombre_archivo>")
def descargar_boleto(nombre_archivo):

    return send_from_directory(
        "boletos",
        nombre_archivo,
        as_attachment=True
    )
# Asignacion de los cinco filosofos
contador_filosofos = 0
candado_filosofos = threading.Lock()


def ejecutar_hilo(cantidad, nombre, correo, telefono):

    global contador_filosofos

    # Asignar un filosofo a esta solicitud
    with candado_filosofos:
        filosofo = contador_filosofos % 5
        contador_filosofos += 1

    resultado = {}

    def trabajo():
        resultado.update(
            procesar_solicitud(
                filosofo,
                cantidad,
                nombre,
                correo,
                telefono
            )
        )

    # Crear e iniciar el hilo
    hilo = threading.Thread(target=trabajo)
    hilo.start()
    hilo.join()

    return resultado


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/solicitar", methods=["GET", "POST"])
def solicitar():

    if request.method == "POST":

        nombre = request.form.get("nombre", "").strip()
        correo = request.form.get("correo", "").strip()
        telefono = request.form.get("telefono", "").strip()
        cantidad_texto = request.form.get("cantidad", "").strip()

        datos = {
            "nombre": nombre,
            "correo": correo,
            "telefono": telefono,
            "cantidad": cantidad_texto
        }

        if not nombre or not correo or not telefono or not cantidad_texto:
            return render_template(
                "solicitar.html",
                error="Todos los campos son obligatorios.",
                datos=datos
            )

        if len(nombre) > 100:
            return render_template(
                "solicitar.html",
                error="El nombre es demasiado largo.",
                datos=datos
            )

        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", correo):
            return render_template(
                "solicitar.html",
                error="Ingresa un correo electronico valido.",
                datos=datos
            )

        if not re.fullmatch(r"[0-9+\-\s()]{7,15}", telefono):
            return render_template(
                "solicitar.html",
                error="Ingresa un numero telefonico valido.",
                datos=datos
            )

        try:
            cantidad = int(cantidad_texto)
        except ValueError:
            return render_template(
                "solicitar.html",
                error="La cantidad debe ser un numero entero.",
                datos=datos
            )

        if cantidad < 1 or cantidad > 20000:
            return render_template(
                "solicitar.html",
                error="La cantidad debe estar entre 1 y 20,000.",
                datos=datos
            )

        # Procesar la solicitud mediante un hilo
        resultado = ejecutar_hilo(
            cantidad,
            nombre,
            correo,
            telefono
        )

        if resultado["correcto"]:

            # Generar un PDF individual para cada boleto
            archivos_pdf = []

            try:
                for numero, folio in enumerate(
                    resultado["boletos"], start=1
                ):

                    ruta_pdf = generar_boleto_pdf(
                        folio,
                        nombre,
                        correo,
                        telefono,
                        numero,
                        cantidad
                    )

                    archivos_pdf.append(ruta_pdf)

            except Exception as error:
                print("Error al generar los PDF:", error)

                return render_template(
                    "solicitar.html",
                    error=(
                        "La solicitud fue registrada, pero ocurrió "
                        "un error al generar los boletos PDF."
                    ),
                    datos=datos
                )

            mensaje = (
                f"¡Solicitud validada! Solicitante: {nombre}. "
                f"Cantidad de boletos: {cantidad}. "
                f"Boletos disponibles: "
                f"{resultado['boletos_restantes']}. "
                f"Se generaron {len(archivos_pdf)} boletos PDF."
            )

            return render_template(
                "solicitar.html",
                mensaje=mensaje,
                datos=datos,
                archivos_pdf=archivos_pdf
            )

        return render_template(
            "solicitar.html",
            error=resultado["mensaje"],
            datos=datos
        )

    return render_template("solicitar.html")


if __name__ == "__main__":
    app.run(debug=True)
