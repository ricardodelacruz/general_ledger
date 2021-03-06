# coding: utf8
(auth.user or request.args(0) == 'login') or redirect(URL('default', 'login'))
import csv
from json import dumps
from datetime import datetime, date

empresa_id = session.instancias
db = empresas.dbs[int(empresa_id)]


# For referencing static and views from other application
def index(): return dict(message="hello from poliza.py")

def listar():
    """
    Crea un objeto `smartgrid` para editar las pólizas y sus respectivos asientos
    """

    db.asiento.cc_empresa_id.represent = lambda value, row: \
            DIV(
                db.cc_empresa(value).num_cc + ' ' + db.cc_empresa(value).descripcion if value else '-',
                _class='cc_empresa_id',
                _id=str(row.id)+'-cc_empresa_id'
                )
    
    db.asiento.concepto_asiento.represent = lambda value, row:\
            DIV(value if value!='' else '-',
                    _class='concepto_asiento',
                    _id=str(row.id)+'-concepto_asiento'
                    )

    db.asiento.debe.represent = lambda value, row:\
            DIV(locale.currency(value, grouping=True) if value!='' else '-',
                    _class='debe derecha',
                    _id='{}-debe'.format(row.id)
                    )
    db.asiento.haber.represent = lambda value, row:\
            DIV(locale.currency(value, grouping=True) if value!='' else '-',
                    _class='haber derecha',
                    _id='{}-haber'.format(row.id)
                    )

    # modificaciones a campos de la tabla `poliza`
    db.poliza.id.readable = False
    db.poliza.importe.writable = False
    db.poliza.concepto_general.represent = lambda value, row:\
            DIV(
                value or '-',
                _class='concepto_general',
                _id=str(row.id)+'-concepto_general'
                )

    # Columna `fecha`
    db.poliza.fecha_usuario.represent = lambda value, row:\
            selector_fecha(row.id)

    # Columna `fecha`
    db.poliza.folio_externo.represent = lambda value, row: value or '-'

    # Columna `periodo`
    db.poliza.periodo_id.represent = lambda value, row:\
            db.periodo(value).clave if value else '-'
    
    # Columna `folio`
    db.poliza.folio.represent = lambda value, row:\
            DIV(value, _class='folio', _id='{}folio'.format(row.id))

    # Columna `tipo_poliza`
    db.poliza.tipo.represent = lambda value, row:\
            crear_selector_tipo(row.id)

    # Columna `estatus_poliza`
    db.poliza.estatus.represent = lambda value, row:\
            crear_selector_status(row.id)

    #selectable = [
            #('Editar', lambda ids, table: [accion(ids, table)]),
            #('Editar', lambda ids: [accion(ids)]),
            #]

    query = db.poliza.periodo_id == request.vars.id

    periodo = obtener_estatus(request.vars.id, request.args(2))

    if request.vars.id:

        links = [lambda row: A(
            SPAN(_class='fa fa-plus-square'), 
            _id = '{}-agregar'.format(row.id),
            _class = 'agregar',
            _href=URL(
                'poliza', 
                'agregar_poliza', 
                vars={'id': request.vars.id}
            ))]
    else:

        links = [lambda row: A(
            SPAN(_class='fa fa-plus-square'), 
            _id = '{}-agregar'.format(row.id),
            _class = 'agregar',
            _href=URL(
                'poliza',
                'agregar_asiento',
                args=['poliza', request.args(2)]
            ))]

    polizas = SQLFORM.smartgrid(
            db.poliza,
            linked_tables=['asiento'],
            constraints = dict(poliza=query),
            #selectable=selectable,
            #deletable=auth.has_permission('delete_poliza') or False,
            deletable=True if periodo != 'CERRADO' else False,
            searchable=False,
            links=links if periodo != 'CERRADO' else None,
            editable=False,
            details=False,
            create=False,
            user_signature=True,
            _class="web2py_grid",
            exportclasses=dict(
                #csv=False,
                csv_with_hidden_cols=False,
                #html=False,
                json=False,
                tsv_with_hidden_cols=False,
                tsv=False,
                #xml=False
                )
            )
    
    # corregir breadcrumb
    polizas.element('.w2p_grid_breadcrumb_elem', replace = lambda items:\
            cambia_breadcrumb(items))

    if request.args(-3) == 'poliza' and request.args(-2) == 'asiento.poliza_id':

        boton_agregar_asiento = DIV(A(
                SPAN(_class="fa fa-plus-square"),
                ' Agregar Asiento',
                _class="button btn btn-primary",
                _href=URL(
                    "poliza",
                    "agregar_asiento",
                    args=["poliza", request.args(-1)]
                    )
                ), BR(), BR())

        if periodo != 'CERRADO':
            polizas[2].insert(-1, boton_agregar_asiento)

        polizas.element('tbody', replace = lambda items: agrega_cuadrar(items))

    else:
        boton_agregar_poliza = DIV(A(
                SPAN(_class="fa fa-plus-square"),
                ' Agregar Póliza',
                _class="button btn btn-primary",
                _href=URL(
                    "poliza",
                    "agregar_poliza",
                    vars={'id':request.vars.id}
                    )
                ), BR(), BR())

        if periodo != 'CERRADO':
            polizas[2].insert(-1, boton_agregar_poliza)

    return dict(polizas=polizas)


def agregar_poliza():
    """
    Agrega un elemento a la tabla `póliza`
    #ToDo: ¿bloquear la inserción por URL?
    """

    periodo_estatus = estatus_periodo(request.vars.id)

    if periodo_estatus != 'CERRADO':

        periodo_id = request.vars.id
        periodo = db(db.periodo.id == periodo_id).select(
                db.periodo.consecutivo,
                db.periodo.inicio,
                db.periodo.estatus_periodo_id
                ).first()

        consecutivo_actual = periodo.consecutivo

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
                fecha_usuario = date.today(),
                periodo_id=periodo_id
                )

        fila = db(db.poliza.id == id).select(
                db.poliza.tipo,
                db.poliza.creada_en,
                ).first()
        ahora = int(fila.creada_en.strftime('%m'))


        """
        if ultimo < ahora:
            # cambio de mes
            consecutivo = 1 
            db(db.periodo.consecutivo == consecutivo_actual).update(
                    consecutivo_polizas = 1
                    )
        else:
        """

        consecutivo = int(consecutivo_actual)

        query = (db.periodo.consecutivo == consecutivo_actual) &\
                (db.periodo.id == periodo_id)

        db(query).update(consecutivo = consecutivo + 1)
        consecutivo += 1

        folio = armar_folio(consecutivo, fila.tipo, periodo.inicio)
        db(db.poliza.id == id).update(folio = folio)

    redirect(URL('poliza', 'listar', vars={'id': request.vars.id}))


def cuadrar_poliza():
    """
    Actualiza un debe/haber
    Compara la suma de los `deberes` y `haberes`
    """

    poliza_id = request.vars.id

    asientos = db(db.asiento.poliza_id == poliza_id).select(
            db.asiento.debe,
            db.asiento.haber
            )

    if asientos:
        deb = reduce(lambda x,y: (x if x else 0) + (y if y else 0), [asi.debe for asi in asientos])
        hab = reduce(lambda x,y: (x if x else 0) + (y if y else 0), [asi.haber for asi in asientos])

        row = TR(_class='fila-final')
        for x in xrange(3):
            row.append(TD(''))

        if comparar_flotantes(deb, hab):
            row.append(TD('Póliza Cuadrada', _class='verde'))
            row.append(TD(DIV(locale.currency(deb, grouping=True ), _class='verde derecha')))
            row.append(TD(DIV(locale.currency(hab, grouping=True ), _class='verde derecha')))
        else:
            row.append(TD('Póliza No Cuadrada', _class='rojo'))
            row.append(TD(DIV(locale.currency(deb, grouping=True ), _class='rojo derecha')))
            row.append(TD(DIV(locale.currency(hab, grouping=True ), _class='rojo derecha')))

        row.append(TD(''))

        return row


def actualiza_poliza():
    """
    Actualiza un campo de la tabla `poliza`
    """

    if request.post_vars:

        id, column = request.post_vars.id.split('-')
        value = request.post_vars.value

        db(db.poliza.id == id).update(**{
            column:value,
            'actualizada_en':datetime.now(),
            'actualizada_por':auth.user['id']
            })

        return value
    else:
        return 'Forbidden Access'


def actualiza_tipo_poliza():
    """
    Actualiza los campos:
    - `tipo`
    - `actualizada_en`
    - `actualizada por`
    de la tabla `poliza`
    Retorna el valor de un nuevo folio
    """

    if request.post_vars:

        id, column = request.post_vars.id.split('-')
        value = request.post_vars.value

        db(db.poliza.id == id).update(**{column:value})

        resultado = db(db.tipo_poliza.id == value).select(
                db.tipo_poliza.id,
                ).first()

        db(db.poliza.id == id).update(**{
            'tipo':resultado.id,
            'actualizada_en':datetime.now(),
            'actualizada_por':auth.user['id']
            })

        # reducir el código aquí
        fila = db(db.poliza.id == id).select(
                db.poliza.folio,
                db.poliza.tipo,
                db.poliza.creada_en
                ).first()
        consecutivo = int(fila.folio[2:8])
        folio = armar_folio(consecutivo, fila.tipo, fila.creada_en)
        db(db.poliza.id == id).update(folio = folio)
        # fin-reducir el código aquí

        return folio
    else:
        return 'Forbidden Access'


def carga_tipo_poliza():
    """
    Carga el catálogo de los tipos de póliza a un objeto JSON, función auxiliar
    """
    from json import loads, dumps

    query = (db.tipo_poliza.id > 0)

    resultado = db(query).select(
            db.tipo_poliza.id,
            db.tipo_poliza.nombre
            )

    diccionario = dict()

    [diccionario.update({r.id: '{}'.format(r.nombre)})\
            for r in resultado]

    return dumps(diccionario)


def verificar_estatus_periodo():
    """
    Función auxiliar, genera un archivo JSON que recibe la vista
    """

    if request.vars.id_poliza:
        estatus = obtener_estatus_periodo(request.vars.id_poliza)
    else:
        poliza_id = request.vars.id_asiento

        id = db(db.poliza.id == poliza_id).select(
                db.poliza.periodo_id
                ).first().periodo_id
        estatus = obtener_estatus_periodo(id)

    diccionario = {'id': estatus}

    return dumps(diccionario, sort_keys=True)


def agregar_asiento():
    """
    Agrega un registro a la tabla `asiento`
    """

    estatus = obtener_estatus(request.vars.id, request.args(1))

    if estatus != 'CERRADO':

        db.asiento.insert(
                poliza_id = request.args(1),
                concepto_asiento = '',
                debe = 0,
                haber = 0
                )

    redirect(URL(
        'poliza/listar/poliza',
        'asiento.poliza_id',
        args=request.args(1)
        ))


def actualiza_asiento():
    """
    Actualiza un campo de la tabla `asiento`
    `post_vars` previene inserciones por URL
    """
    if request.post_vars:

        id, column = request.post_vars.id.split('-')
        value = request.post_vars.value

        db(db.asiento.id == id).update(**{
            column:value,
            'actualizada_en':datetime.now(),
            'actualizada_por':auth.user['id']
            })

        return value
    else:
        return 'Forbidden Access'


def actualiza_debe_haber():
    """
    Actualiza los campos `debe` y `haber` de la tabla `asientos`
    """
    import numbers

    if request.post_vars:

        id, column = request.post_vars.id.split('-')
        value = request.post_vars.value

        valor_retornar = value

        if '$' in value:
            value = value.replace('$', '')

        if ',' in value:
            value = value.replace(',', '') 

        try:
            value = float(value)
            value = abs(value)
        except:
            # si el formato es incorrecto, regresar el valor actual en el registro
            ex = db(db.asiento.id == id).select(
                    db.asiento[column].with_alias('valor')
                    ).first().valor
            value = ex

        valor_retornar = locale.currency(float(value), grouping=True)

        db(db.asiento.id == id).update(**{
            column:value,
            'actualizada_en':datetime.now(),
            'actualizada_por':auth.user['id']
            })

        return valor_retornar
    else:
        return 'Forbidden Access'


def actualiza_descripcion():
    """
    Actualiza el campo `descripcion` de la tabla `asiento`.
    Obtiene
    """
    if request.post_vars:

        id, column = request.post_vars.id.split('-')
        valor = request.post_vars.value

        num_cc = valor.split()[0]

        resultado = db(db.cc_empresa.num_cc == num_cc).select(
                db.cc_empresa.id,
                db.cc_empresa.num_cc,
                db.cc_empresa.descripcion
                ).first()

        db(db.asiento.id == id).update(**{
            column:resultado.id,
            'actualizada_en': datetime.now(),
            'actualizada_por': auth.user['id']
            })

        return "%s %s" % (resultado.num_cc, resultado.descripcion)
    else:
        return 'Forbidden Access'


def carga_cc():
    """
    Carga el catálogo de cuentas a un objeto JSON, función auxiliar
    """
    from json import loads, dumps

    query = ((db.cc_empresa.id > 0) & (db.cc_empresa.cc_vista_id==2))

    result = db(query).select(
            db.cc_empresa.id,
            db.cc_empresa.num_cc,
            db.cc_empresa.descripcion,
            )

    diccionario = dict()

    [diccionario.update({r.id: '{} {}'.format(r.num_cc, r.descripcion)})\
            for r in result]

    return dumps(diccionario)


def validar_periodo(fecha_usuario):
    periodo = db(
                (db.periodo.inicio <=fecha_usuario) &
                (db.periodo.fin >=fecha_usuario) &
                (db.periodo.estatus_periodo_id != 2)).select(
            db.periodo.ALL,
        ).first()
    if periodo:
        activo=True
    else:
        activo=False
    return activo

def importar_polizas():
    tipo_msg='error'
    tipo = type(request.vars.csv_saldo_inicial)
    if type(request.vars.csv_saldo_inicial)!='str' and request.vars:
        tipo = type(request.vars.csv_saldo_inicial)
        file = request.vars.csv_saldo_inicial.file
        reader = csv.reader(file)
        campos=['poliza_id','cc_empresa_id', 'concepto_asiento','debe', 'haber']
        for row in reader:
            folio_externo=row[0]
            tipo_poliza=int(row[1])
            fecha_poliza=row[2]
            concepto_general=row[3]
            estatus = validar_periodo(fecha_poliza)
            if not estatus:
                msg = 'El periodo de la fecha '+fecha_poliza+' de la póliza '+folio_externo +' no se encuentra activo'
                break
            else:
                poliza = db(db.poliza.folio_externo==folio_externo).select(db.poliza.ALL).first()
                validacion_poliza=True
                if not poliza:
                    try:
                        poliza_id = agregar_poliza_csv(folio_externo, tipo_poliza, fecha_poliza, concepto_general)
                    except:
                        msg = 'Error al insertar la póliza. Verifique el formato del archivo CSV'
                        validacion_poliza=False
                        db.rollback()
                    else:
                        db.commit()
                else:
                    poliza_id = poliza.id
                print "Termina poliza_id "+str(poliza_id)
                if validacion_poliza:
                    num_cc=row[4]
                    concepto=row[5]
                    debe=float(row[6])
                    haber=float(row[7])
                    cc=db(db.cc_empresa.num_cc==num_cc).select(db.cc_empresa.id).first()
                    if not cc:
                        msg= 'El número de cuenta '+num_cc+' no existe'
                    else:
                        valores=[]
                        valores.append(poliza_id)
                        valores.append(int(cc.id))
                        valores.append(concepto)
                        valores.append(debe)
                        valores.append(haber)
                        msg= 'Error al insertar los asientos'
                        dictionary = dict(zip(campos, valores))
                        db[db.asiento].insert(**dictionary)
                        tipo_msg='exito'
                        msg= 'Polizas guardadas'
    else:
        tipo_msg='info'
        msg= 'Elija un archivo para subir'
    return dict(tipo_msg=tipo_msg,msg=msg)

def agregar_poliza_csv(folio_externo, tipo, fecha_usuario, concepto_general):
    """
    Agrega un elemento a la tabla `póliza`
    """
    periodo = db(
                (db.periodo.inicio <=fecha_usuario)&
                (db.periodo.fin >=fecha_usuario)).select(
            db.periodo.ALL,
        ).first()
    
    db(db.periodo.id == periodo.id).update(
                consecutivo = periodo.consecutivo+1
                )
    folio = armar_folio(periodo.consecutivo+1, tipo, periodo.inicio)
    id = db.poliza.insert(
            folio = folio,
            tipo=tipo,
            folio_externo=folio_externo,
            fecha_usuario=fecha_usuario,
            concepto_general=concepto_general
                )
    return id
