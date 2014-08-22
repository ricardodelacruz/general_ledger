# coding: utf8
# intente algo como
import csv
from datetime import datetime
db=empresas.dbs[int(session.instancias)]

def index(): return dict(message="hello from configuracion/reportes.py")
def estado_resultados():
    msg=''
    tipo_msg=''
    nombre_reporte= db(db.reporte.nombre=='estado_resultados').select(db.reporte.ALL)
    desc_ingresos= db(db.seccion_reporte.nombre=='ingresos').select(db.seccion_reporte.ALL)
    desc_costos= db(db.seccion_reporte.nombre=='costos').select(db.seccion_reporte.ALL)
    desc_gastos= db(db.seccion_reporte.nombre=='gastos').select(db.seccion_reporte.ALL)
    desc_otros= db(db.seccion_reporte.nombre=='otros').select(db.seccion_reporte.ALL)
    desc_impuestos= db(db.seccion_reporte.nombre=='impuestos').select(db.seccion_reporte.ALL)
    cuentas_ingresos=db( (db.seccion_reporte.nombre=='ingresos')
                        & (db.cuentas_seccion_reporte.seccion_reporte_id==db.seccion_reporte.id )
                        & (db.cc_empresa.id==db.cuentas_seccion_reporte.cc_empresa_id)).select(db.cc_empresa.ALL,groupby=db.cc_empresa.id)
    cuentas_costos=db( (db.seccion_reporte.nombre=='costos')
                        & (db.cuentas_seccion_reporte.seccion_reporte_id==db.seccion_reporte.id )
                        & (db.cc_empresa.id==db.cuentas_seccion_reporte.cc_empresa_id)).select(db.cc_empresa.ALL,groupby=db.cc_empresa.id)
    cuentas_gastos=db( (db.seccion_reporte.nombre=='gastos')
                        & (db.cuentas_seccion_reporte.seccion_reporte_id==db.seccion_reporte.id )
                        & (db.cc_empresa.id==db.cuentas_seccion_reporte.cc_empresa_id)).select(db.cc_empresa.ALL,groupby=db.cc_empresa.id)
    cuentas_otros=db( (db.seccion_reporte.nombre=='otros')
                        & (db.cuentas_seccion_reporte.seccion_reporte_id==db.seccion_reporte.id )
                        & (db.cc_empresa.id==db.cuentas_seccion_reporte.cc_empresa_id)).select(db.cc_empresa.ALL,groupby=db.cc_empresa.id)
    cuentas_impuestos=db( (db.seccion_reporte.nombre=='impuestos')
                        & (db.cuentas_seccion_reporte.seccion_reporte_id==db.seccion_reporte.id )
                        & (db.cc_empresa.id==db.cuentas_seccion_reporte.cc_empresa_id)).select(db.cc_empresa.ALL,groupby=db.cc_empresa.id)
    cc_empresa = db.executesql("SELECT node.num_cc, node.descripcion,(COUNT(parent.descripcion) - 1) AS depth, "\
                   "node.id, node.cc_vista_id "\
                   "FROM cc_empresa AS node , cc_empresa AS parent "\
                   "WHERE node.lft BETWEEN parent.lft AND parent.rgt "\
                   "GROUP BY node.id "\
                   "ORDER BY node.lft;")
    
    if request.vars:
        if request.vars.nombre_reporte == '':
            tipo_msg='error'
            msg='Asigne un nombre al reporte'
        elif request.vars.etiqueta_ingresos=='':
            tipo_msg='error'
            msg='Asigne una etiqueta a los ingresos'
        elif not request.vars.sel_ingresos:
            tipo_msg='error'
            msg='Asigne al menos una cuenta a las cuentas de ingresos'
        elif request.vars.etiqueta_costos=='':
            tipo_msg='error'
            msg='Asigne una etiqueta a los costos'
        elif not request.vars.sel_costos:
            tipo_msg='error'
            msg='Asigne al menos una cuenta a las cuentas de costos'
        elif request.vars.etiqueta_gastos=='':
            tipo_msg='error'
            msg='Asigne una etiqueta a los gastos'
        elif not request.vars.sel_gastos:
            tipo_msg='error'
            msg='Asigne al menos una cuenta a las cuentas de gastos'
        elif request.vars.etiqueta_otros=='':
            tipo_msg='error'
            msg='Asigne una etiqueta a los otros ingresos y costos'
        elif not request.vars.sel_otros:
            tipo_msg='error'
            msg='Asigne al menos una cuenta a las cuentas de otros ingresos y costos'
        elif request.vars.etiqueta_impuestos=='':
            tipo_msg='error'
            msg='Asigne una etiqueta a los impuestos'
        elif not request.vars.sel_impuestos:
            tipo_msg='error'
            msg='Asigne al menos una cuenta a las cuentas de impuestos'
        else:
            #try:
                #Nombre del reporte
                msg='Error en el nombre del reporte'
                reporte=db.reporte.update_or_insert(db.reporte.nombre=='estado_resultados', nombre='estado_resultados', descripcion=request.vars.nombre_reporte)
                nombre_reporte= db(db.reporte.nombre=='estado_resultados').select(db.reporte.ALL)
                #ingresos
                msg='Error en la etiqueta de ingresos'
                ingresos=db.seccion_reporte.update_or_insert(((db.seccion_reporte.reporte_id==nombre_reporte[0].id) & (db.seccion_reporte.nombre=='ingresos')), reporte_id=nombre_reporte[0].id, nombre='ingresos', descripcion=request.vars.etiqueta_ingresos)
                desc_ingresos= db(db.seccion_reporte.nombre=='ingresos').select(db.seccion_reporte.ALL)
                msg='Error al eliminar las cuentas de ingresos'
                db(db.cuentas_seccion_reporte.seccion_reporte_id==desc_ingresos[0].id).delete()
                if isinstance(request.vars.sel_ingresos, list):
                    msg='Error en la seccion de ingresos (1)'
                    for cc_ingresos in request.vars.sel_ingresos:
                        db.cuentas_seccion_reporte.insert(seccion_reporte_id=desc_ingresos[0].id,
                                                      cc_empresa_id=cc_ingresos)
                else:
                    msg='Error en la seccion de ingresos (2)'
                    db.cuentas_seccion_reporte.insert(seccion_reporte_id=desc_ingresos[0].id,
                                                      cc_empresa_id=request.vars.sel_ingresos)
                #costos
                msg='Error en la etiqueta de costos'
                costos=db.seccion_reporte.update_or_insert(((db.seccion_reporte.reporte_id==nombre_reporte[0].id) & (db.seccion_reporte.nombre=='costos')), reporte_id=nombre_reporte[0].id, nombre='costos', descripcion=request.vars.etiqueta_costos)
                desc_costos= db(db.seccion_reporte.nombre=='costos').select(db.seccion_reporte.ALL)
                msg='Error al eliminar las cuentas de costos'
                db(db.cuentas_seccion_reporte.seccion_reporte_id==desc_costos[0].id).delete()
                if isinstance(request.vars.sel_costos, list):
                    msg='Error en la sección de costos (1) '
                    for cc_costos in request.vars.sel_costos:
                        db.cuentas_seccion_reporte.insert(seccion_reporte_id=desc_costos[0].id, cc_empresa_id=cc_costos)
                else:
                    msg='Error en la sección de costos (2)'
                    db.cuentas_seccion_reporte.insert(seccion_reporte_id=desc_costos[0].id, cc_empresa_id=request.vars.sel_costos)
                #gastos
                msg='Error en la etiqueta de gastos'
                gastos=db.seccion_reporte.update_or_insert(((db.seccion_reporte.reporte_id==nombre_reporte[0].id) & (db.seccion_reporte.nombre=='gastos')), reporte_id=nombre_reporte[0].id, nombre='gastos', descripcion=request.vars.etiqueta_gastos)
                desc_gastos= db(db.seccion_reporte.nombre=='gastos').select(db.seccion_reporte.ALL)
                msg='Error al eliminar las cuentas de gastos'
                db(db.cuentas_seccion_reporte.seccion_reporte_id==desc_gastos[0].id).delete()
                if isinstance(request.vars.sel_gastos, list):
                    msg='Error en la seccion de gastos (1)'
                    for cc_gastos in request.vars.sel_gastos:
                        db.cuentas_seccion_reporte.insert(seccion_reporte_id=desc_gastos[0].id, cc_empresa_id=cc_gastos)
                else:
                    msg='Error en la seccion de gastos (2)'
                    db.cuentas_seccion_reporte.insert(seccion_reporte_id=desc_gastos[0].id, cc_empresa_id=request.vars.sel_gastos)
                #otros
                msg='Error en la etiqueta de otros'
                otros=db.seccion_reporte.update_or_insert(((db.seccion_reporte.reporte_id==nombre_reporte[0].id) & (db.seccion_reporte.nombre=='otros')), reporte_id=nombre_reporte[0].id, nombre='otros', descripcion=request.vars.etiqueta_otros)
                desc_otros= db(db.seccion_reporte.nombre=='otros').select(db.seccion_reporte.ALL)
                db(db.cuentas_seccion_reporte.seccion_reporte_id==desc_otros[0].id).delete()
                if isinstance(request.vars.sel_otros, list):
                    msg='Error en la seccion de otros (1)'
                    for cc_otros in request.vars.sel_otros:
                        db.cuentas_seccion_reporte.insert(seccion_reporte_id=desc_otros[0].id, cc_empresa_id=cc_otros)
                else:
                    msg='Error en la seccion de otros (2)'
                    db.cuentas_seccion_reporte.insert(seccion_reporte_id=desc_otros[0].id, cc_empresa_id=request.vars.sel_otros)
                #impuestos
                msg='Error en la etiqueta de impuestos'           
                impuestos=db.seccion_reporte.update_or_insert((db.seccion_reporte.reporte_id==nombre_reporte[0].id) & (db.seccion_reporte.nombre=='impuestos'), reporte_id=nombre_reporte[0].id, nombre='impuestos', descripcion=request.vars.etiqueta_impuestos)
                desc_impuestos= db(db.seccion_reporte.nombre=='impuestos').select(db.seccion_reporte.ALL)
                db(db.cuentas_seccion_reporte.seccion_reporte_id==desc_impuestos[0].id).delete()
                if isinstance(request.vars.sel_impuestos, list):
                    msg='Error en la seccion de impuestos (1)'
                    for cc_impuestos in request.vars.sel_impuestos:
                        db.cuentas_seccion_reporte.insert(seccion_reporte_id=desc_impuestos[0].id, cc_empresa_id=cc_impuestos)
                else:
                    msg='Error en la seccion de impuestos (2)'
                    db.cuentas_seccion_reporte.insert(seccion_reporte_id=desc_impuestos[0].id, cc_empresa_id=request.vars.sel_impuestos)
                msg='Configuración del reporte realizada'
            #    db.commit()
                tipo_msg='exito'
            #except:
            #    tipo_msg='error'
            #    db.rollback()
                
    
    return dict(cc_empresa=cc_empresa, nombre_reporte=nombre_reporte, desc_ingresos=desc_ingresos, desc_costos=desc_costos, desc_gastos=desc_gastos, desc_otros=desc_otros, desc_impuestos=desc_impuestos, cuentas_ingresos=cuentas_ingresos, cuentas_costos=cuentas_costos, cuentas_gastos=cuentas_gastos, cuentas_otros=cuentas_otros, cuentas_impuestos=cuentas_impuestos, msg=XML(msg), tipo_msg=XML(tipo_msg))

def cambiar_catalogo():
    db(db.cc_empresa).delete()
    db.executesql('delete from sqlite_sequence where name="cc_empresa";')
    if type(request.vars.csv_catalogo) != str:
        try:
            msg= 'Error al insertar la póliza'
            campos=['lft','rgt', 'clave_usuario','descripcion', 'nivel']
            file = request.vars.csv_catalogo.file
            reader = csv.reader(file)
            for row in reader:
                    
                    valores=[]
                    valores.append(int(row[0]))
                    valores.append(int(row[1]))
                    valores.append(row[2])
                    valores.append(row[3])
                    valores.append(int(row[4]))
                    dictionary = dict(zip(campos, valores))
                    db[db.asiento].insert(**dictionary)
        except:
            db.rollback()
            tipo_msg='error'
        else:
            db.commit()
            tipo_msg='exito'
            msg= 'Catálogo actualizado'
    else:
        tipo_msg='error'
        msg= 'Elija un archivo para subir'
    return dict(tipo_msg=tipo_msg,msg=msg)

def saldo_inicial():
    tipo_msg='error'
    
    tipo = type(request.vars.csv_saldo_inicial)
    msg='No entra '+str(tipo)
   
    if type(request.vars.csv_saldo_inicial)!='str' and request.vars:
        tipo = type(request.vars.csv_saldo_inicial)
        msg = 'Entra '+str(tipo)
        try:
        
            file = request.vars.csv_saldo_inicial.file
            reader = csv.reader(file)
            
            campos=['poliza_id','cc_empresa_id', 'concepto_asiento','debe', 'haber']
            
            for row in reader:
                    folio_externo=row[0]
                    fecha_poliza=row[1]
                    concepto_general=row[2]
                    poliza = db(db.poliza.folio_externo==folio_externo).select(db.poliza.ALL).first()
                    msg= 'Error al insertar la póliza'
                    
                    if not poliza:
                        poliza_id = agregar_poliza(folio_externo, fecha_poliza, concepto_general)
                    else:
                        poliza_id = poliza.id
                    cc=db(db.cc_empresa.num_cc==row[3]).select(db.cc_empresa.id).first()
                    if not cc:
                        msg= 'El número de cuenta '+row[3]+' no existe'
                    valores=[]
                    valores.append(poliza_id)
                    valores.append(int(cc.id))
                    valores.append(row[4])
                    valores.append(float(row[5]))
                    valores.append(float(row[6]))
                    msg= 'Error al insertar los asientos'
                    dictionary = dict(zip(campos, valores))
                    db[db.asiento].insert(**dictionary)
                    
        except:
            db.rollback()
            tipo_msg='error'
            
        else:
            db.commit()
            tipo_msg='exito'
            msg= 'Saldo inicial guardado'
    else:

        tipo_msg='info'
        msg= 'Elija un archivo para subir'
    return dict(tipo_msg=tipo_msg,msg=msg)

def agregar_poliza(folio_externo, fecha_usuario, concepto_general):
    """
    Agrega un elemento a la tabla `póliza`
    """

    ultimo = db(db.poliza.id > 0).select(
            db.poliza.id,
            db.poliza.creada_en,
            orderby =~ db.poliza.id
        ).first()

    # en caso de que no existan pólizas
    if ultimo:
        ultimo = int(ultimo.creada_en.strftime('%m'))
    else:
        ultimo = int(datetime.now().strftime('%m'))
    # fin-en caso de que no existan pólizas

    id = db.poliza.insert(
            folio = '',
            concepto_general = '',
            importe = 0,
            )

    fila = db(db.poliza.id == id).select(
            db.poliza.tipo,
            db.poliza.creada_en,
            ).first()
    ahora = int(fila.creada_en.strftime('%m'))

    consecutivo_actual = db(db.misc.id > 0).select(
            db.misc.consecutivo_polizas
            ).first().consecutivo_polizas

    if ultimo < ahora:
        # cambio de mes
        consecutivo = 1 
        db(db.misc.consecutivo_polizas == consecutivo_actual).update(
                consecutivo_polizas = 1
                )
    else:
        consecutivo = consecutivo_actual 
        db(db.misc.consecutivo_polizas == consecutivo_actual).update(
                consecutivo_polizas = consecutivo + 1
                )
        consecutivo += 1

    folio = armar_folio(consecutivo, fila.tipo, fila.creada_en)
    db(db.poliza.id == id).update(folio = folio, folio_externo=folio_externo, fecha_usuario=fecha_usuario,concepto_general=concepto_general)
    return id
