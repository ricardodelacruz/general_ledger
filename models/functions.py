# coding: utf8

"""
Colección de funciones/hacks
"""

def comparar_flotantes(a, b):
    """
    compara flotantes que en apariencia son iguales D:
    """
    if abs(a-b) < 0.0000000001:
        return True
    else:
        return False
    

def agrega_cuadrar(items):
    """
    agrega un TR al final
    """

    row = TR(_class='fila-final')
    for x in xrange(8):
        row.append(TD(''))

    items.append(row)

    return items


def calcula_importe(poliza_id):
    """
    calcula el importe de la póliza, esto es, la suma de los asientos
    """

    asientos = db(db.asiento.poliza_id == poliza_id).select(
            db.asiento.debe, db.asiento.haber
            )

    if asientos:
        deb = reduce(lambda x,y: (x if x else 0) + (y if y else 0), [asi.debe for asi in asientos])
        hab = reduce(lambda x,y: (x if x else 0) + (y if y else 0), [asi.haber for asi in asientos])

        if comparar_flotantes(deb, hab):
            flag = DIV('{}'.format(locale.currency(deb, grouping=True )), _class='verde')
        else:
            flag = DIV('{} <> {}'.format(locale.currency(deb, grouping=True ), locale.currency(hab, grouping=True )), _class='rojo')

    else:
        flag = DIV('Póliza sin asientos', _class='rojo')

    return flag


def obtener_tipo_poliza(tipo_poliza_id):
    """
    Retorna el tipo de poliza a partir de un id
    """
    resultado = db(db.tipo_poliza.id == tipo_poliza_id).select(
            db.tipo_poliza.nombre
            ).first()

    return resultado.nombre


def eliminar(ids):
    """
    Recibe una lista de ids y los elimina
    """
    [db(db.poliza.id == id).delete() for id in ids]


def editar(ids):
    """
    Recibe una lista de ids, edita el primero que toma
    """
    print ids[0]
