
import threading

from database import obtener_conexion


# Cinco recursos compartidos, como los tenedores
tenedores = [threading.Lock() for _ in range(5)]

# Permite que máximo cuatro filósofos intenten
# tomar los tenedores al mismo tiempo
sala = threading.Semaphore(4)


def procesar_solicitud(filosofo, cantidad, nombre, correo, telefono):

    izquierdo = filosofo
    derecho = (filosofo + 1) % 5

    conexion = None
    cursor = None

    with sala:
        with tenedores[izquierdo]:
            with tenedores[derecho]:

                try:
                    conexion = obtener_conexion()
                    cursor = conexion.cursor()

                    # Bloquear el inventario para evitar
                    # que dos solicitudes lo modifiquen a la vez
                    cursor.execute("""
                        SELECT DISPONIBLES
                        FROM CONTROL_BOLETOS
                        WHERE ID = 1
                        FOR UPDATE
                    """)

                    fila = cursor.fetchone()

                    if fila is None:
                        conexion.rollback()
                        return {
                            "correcto": False,
                            "mensaje": "No se encontró el inventario.",
                            "boletos_restantes": 0
                        }

                    boletos_disponibles = fila[0]

                    # Comprobar que exista suficiente inventario
                    if cantidad > boletos_disponibles:
                        conexion.rollback()

                        return {
                            "correcto": False,
                            "mensaje": "No hay suficientes boletos disponibles.",
                            "boletos_restantes": boletos_disponibles
                        }

                    # Obtener identificador del solicitante
                    cursor.execute("""
                        SELECT SEQ_SOLICITANTES.NEXTVAL
                        FROM DUAL
                    """)
                    id_solicitante = cursor.fetchone()[0]

                    # Registrar al solicitante
                    cursor.execute("""
                        INSERT INTO SOLICITANTES
                        (ID_SOLICITANTE, NOMBRE, CORREO, TELEFONO)
                        VALUES (:id, :nombre, :correo, :telefono)
                    """, {
                        "id": id_solicitante,
                        "nombre": nombre,
                        "correo": correo,
                        "telefono": telefono
                    })

                    # Obtener identificador de la solicitud
                    cursor.execute("""
                        SELECT SEQ_SOLICITUDES.NEXTVAL
                        FROM DUAL
                    """)
                    id_solicitud = cursor.fetchone()[0]

                    # Registrar la solicitud
                    cursor.execute("""
                        INSERT INTO SOLICITUDES
                        (ID_SOLICITUD, ID_SOLICITANTE, CANTIDAD, ESTADO)
                        VALUES (:id, :solicitante, :cantidad, 'ACEPTADA')
                    """, {
                        "id": id_solicitud,
                        "solicitante": id_solicitante,
                        "cantidad": cantidad
                    })

                    # Crear los boletos individuales
                    boletos_generados = []

                    for numero in range(1, cantidad + 1):

                        cursor.execute("""
                            SELECT SEQ_BOLETOS.NEXTVAL
                            FROM DUAL
                        """)
                        id_boleto = cursor.fetchone()[0]

                        # Generar folio único
                        folio = f"APL-{id_solicitud}-{numero:05d}"

                        # Crear contenido del código QR
                        contenido_qr = (
                            f"AUDITORIO PLATA | "
                            f"Folio: {folio} | "
                            f"Solicitante: {nombre} | "
                            f"Correo: {correo} | "
                            f"Telefono: {telefono} | "
                            f"Boleto: {numero} de {cantidad}"
                        )

                        # Guardar boleto y contenido QR en Oracle
                        cursor.execute("""
                            INSERT INTO BOLETOS
                            (ID_BOLETO, ID_SOLICITUD, FOLIO, CODIGO_QR)
                            VALUES (:id, :solicitud, :folio, :qr)
                        """, {
                            "id": id_boleto,
                            "solicitud": id_solicitud,
                            "folio": folio,
                            "qr": contenido_qr
                        })

                        # Guardar folio para generar su PDF
                        boletos_generados.append(folio)

                    # Descontar boletos del inventario
                    cursor.execute("""
                        UPDATE CONTROL_BOLETOS
                        SET DISPONIBLES = DISPONIBLES - :cantidad
                        WHERE ID = 1
                    """, {"cantidad": cantidad})

                    # Registrar operación en la bitácora
                    cursor.execute("""
                        INSERT INTO BITACORA
                        (ID_EVENTO, ID_SOLICITUD, EVENTO, DETALLE)
                        VALUES (
                            SEQ_BITACORA.NEXTVAL,
                            :solicitud,
                            'SOLICITUD ACEPTADA',
                            :detalle
                        )
                    """, {
                        "solicitud": id_solicitud,
                        "detalle": f"Se generaron {cantidad} boletos."
                    })

                    # Confirmar todos los cambios
                    conexion.commit()

                    disponibles = boletos_disponibles - cantidad

                    return {
                        "correcto": True,
                        "mensaje": "Solicitud procesada correctamente.",
                        "boletos_restantes": disponibles,
                        "boletos": boletos_generados
                    }

                except Exception as error:

                    if conexion:
                        conexion.rollback()

                    print("Error al procesar solicitud:", error)

                    return {
                        "correcto": False,
                        "mensaje": "Ocurrió un error al guardar la solicitud en Oracle.",
                        "boletos_restantes": 0
                    }

                finally:

                    if cursor:
                        cursor.close()

                    if conexion:
                        conexion.close()
