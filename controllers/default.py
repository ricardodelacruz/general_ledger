# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db_maestro (does streaming)
## - call exposes all registered services (none by default)
#########################################################################
import time
from datetime import datetime
import csv

db = None
if session.instancias:
    db=empresas.dbs[int(session.instancias)]

def register():
    from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
    auth = Auth(db_maestro)
    form = auth.register()
    return dict(form=form)

def login():
    from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
    auth = Auth(db_maestro)
    ## configure email
    mail = auth.settings.mailer
    mail.settings.server = 'smtp.gmail.com:587'
    mail.settings.sender = 'datawork.mx@gmail.com'
    mail.settings.login = 'datawork.mx:d4t4w0rk'
    form = auth.login()
    return dict(form=form, formReset = auth.retrieve_password())

def user():

    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    if request.args(0)=='logout':

        [empresas.dbs[instancia].close() for instancia in empresas.dbs]
        cookieDelete()

    elif request.args(0)=='login':
        auth.settings.login_form=GoogleAccount()
    return dict(form=auth())

def empresa():
    empresa_id = request.args(0)
   
    if empresa_id:
        session.instancias = empresa_id
        global db
        db = empresas.dbs[int(session.instancias)]
        
    fecha=time.strftime("%Y-%m-%d")
    nivel='0'
    cc_empresa = catalogo_nivel(nivel)
    total=0
    lista=[]
    for num_cc in cc_empresa:
        cantidad=importe_cuenta_balanza(num_cc[0], num_cc[5], fecha)
        total+=cantidad
        lista.append(cantidad)
    return dict(lista=lista)

def insertar_pais(nombre):
    """
    Inserta un registro `pais` si no existe,
    en caso contrario retorna su id
    """
    pais = db(db.pais.nombre == nombre).select(db_maestro.pais.id).first()
    if not pais:
        return db_maestro.pais.insert(nombre = nombre)
    else:
        return pais.id


def insertar_estado(nombre, clave_interna, pais_id):
    """
    Inserta un registro `estado` si no existe,
    en caso contrario retorna su id
    """
    estado = db_maestro(db_maestro.estado.nombre == nombre).select(db_maestro.estado.id).first()
    if not estado:
        return db_maestro.estado.insert(
                nombre = nombre,
                clave_interna = clave_interna,
                pais_id = pais_id
                )
    else:
        return estado.id


def insertar_municipio(nombre, clave_interna, estado_id):
    """
    Inserta un registro `municipio` si no existe,
    en caso contrario retorna su id
    """

    municipio = db_maestro(
            (db_maestro.municipio.nombre == nombre) &
            (db_maestro.municipio.estado_id == estado_id)
            ).select(db_maestro.municipio.id).first()
    if not municipio:
        return db_maestro.municipio.insert(
                nombre = nombre,
                clave_interna = clave_interna,
                estado_id = estado_id
                )
    else:
        return municipio.id


def insertar_localidad(
        nombre,
        clave_interna,
        lat_grad,
        lon_grad,
        lat_dec,
        lon_dec,
        municipio_id
        ):
    """
    Inserta un registro `localidad`
    """

    db_maestro.localidad.insert(
            nombre = nombre,
            clave_interna = clave_interna,
            lat_grad = lat_grad,
            lon_grad = lon_grad,
            lat_dec = lat_dec,
            lon_dec = lon_dec,
            municipio_id = municipio_id
        )


def precargar():
    pais_id = insertar_pais('MÉXICO')

    # precargar estados
    with open('localidades.csv', 'rb') as f:

        reader = csv.reader(f)

        for line in reader:

            estado_id = insertar_estado(line[1], line[0], pais_id)
            municipio_id = insertar_municipio(line[3], line[2], estado_id)
            insertar_localidad(
                    line[5], line[4],
                    float(line[6]), float(line[7]),
                    float(line[8]), float(line[9]),
                    municipio_id
                    )
    return dict()


def cargar_paises():
    """
    Genera un objeto SELECT de los países que ya existen en la BD.
    """

    opciones = [OPTION(pais.nombre, _value=pais.id) for pais in\
               db_maestro().select(
                   db_maestro.pais.ALL,
                   #cache=(cache.ram, 3600) #problemas SQLite
                   )
               ]

    #opciones[:0] = [OPTION('TODOS', _value='')]

    resultado = SELECT(
        _id='pais_id',
        *opciones,
        **dict(
            _name='paises',
            requires = IS_IN_DB(db_maestro,'pais.nombre')
        )
    )
    return resultado


def cargar_estados():
    """
    Genera un objeto SELECT de los estados del pais X.
    """

    opciones = [OPTION(estado.nombre, _value=estado.id) for estado in\
               db_maestro(db_maestro.estado.pais_id == request.vars.pais_id).select(
                   db_maestro.estado.ALL,
                   #cache=(cache.ram, 3600) #problemas SQLite
                   )
               ]
    #opciones[:0] = [OPTION('TODOS', _value='')]

    resultado = SELECT(
        _id='estado_id',
        *opciones,
        **dict(
            _name='estados',
            requires = IS_IN_DB(db_maestro, 'estado.nombre')
        )
    )
    return resultado


def cargar_municipios():
    """
    Genera un objeto SELECT de los municipios del estado X.
    """

    opciones = [OPTION(municipio.nombre, _value=municipio.id) for municipio in\
               db_maestro(db_maestro.municipio.estado_id == request.vars.estado_id).select(
                   db_maestro.municipio.ALL,
                   #cache=(cache.ram, 3600) #problemas SQLite
                   )
               ]

    #opciones[:0] = [OPTION('TODOS', _value='')]

    resultado = SELECT(
        _id='municipio_id',
        *opciones,
        **dict(
            _name='municipios',
            requires = IS_IN_DB(db_maestro, 'municipio.nombre')
        )
    )
    return resultado


def cargar_localidades():
    """
    Genera un objeto SELECT de las localidades del municipio X.
    """

    opciones = [OPTION(localidad.nombre, _value=localidad.id) for localidad in\
               db_maestro(db_maestro.localidad.municipio_id == request.vars.municipio_id).select(
                   db_maestro.localidad.ALL,
                   #cache=(cache.ram, 3600) #problemas SQLite
                   )
               ]

    # opciones[:0] = [OPTION('TODOS', _value='')]

    resultado = SELECT(
        _id='localidad_id',
        *opciones,
        **dict(
            _name='localidad',
            requires = IS_IN_DB(db_maestro, 'localidad.nombre')
        )
    )
    return resultado


@auth.requires_login()
def empresa_wizard():
    """
    Útil para introducir los datos iniciales de una empresa
    """

    campos = [
        Field('pais_id', 'string', label=T('País')),
        Field('estado_id', 'string', label=T('Estado')),
        Field('municipio_id', 'string', label=T('Municipio')),
        Field('localidad_id', 'string', label=T('Localidad')),
        Field('registro_fiscal', 'string', label='Registro Fiscal'),
        Field('dir_calle', 'string', label=T('Calle')),
        Field('dir_num_ext', 'string', label=T('Número Exterior')),
        Field('dir_num_int', 'string', label=T('Número Interior')),
        Field('dir_colonia', 'string', label='Colonia'),
        Field('dir_cp', 'string', label='Código Postal'),
        Field('dir_telefono', 'string', label='Teléfono'),
        Field('dir_movil', 'string', label='Móvil'),
        Field('dir_email', requires=IS_EMAIL(), label='Email'),
        Field('razon_social', 'string', label='Razón Social'),
        Field('nombre_comercial', 'string', label='Nombre Comercial'),
    ]

    form = SQLFORM.factory(*campos)

    #if form.process().accepted:
    if request.vars:
        # generar hash :/ crear función para esto

        nombre = request.vars.razon_social
        email = auth.user['email']

        empresa_id = db_maestro.empresa.insert(
                **db_maestro.empresa._filter_fields(request.vars)
                )
        vars = {'empresa_id': empresa_id}

        db_maestro.mi_empresa.insert(user_id=auth.user['id'], empresa_id=empresa_id)

        instancia = Web2Postgres()
        instancia.crear_db(nombre, email)

        empresas.cargar_modelo_de_instancia(email, nombre, vez_primera=True)

        redirect(URL('cc_empresa', 'cc_wizard', vars=vars))

    elif form.errors:
        print form.errors
    else:
        pass

    return dict(form=form)


def index3():
    """
    Útil para introducir los datos iniciales de una sucursal y departamento
    """

    campos = [
        Field('pais_id', 'string', label=T('País')),
        Field('estado_id', 'string', label=T('Estado')),
        Field('municipio_id', 'string', label=T('Municipio')),
        Field('localidad_id', 'string', label=T('Localidad')),
        Field('registro_fiscal', 'string', label='Registro Fiscal'),
        Field('dir_calle', 'string', label=T('Calle')),
        Field('dir_num_ext', 'string', label=T('Número Exterior')),
        Field('dir_num_int', 'string', label=T('Número Interior')),
        Field('dir_colonia', 'string', label=T('Colonia')),
        Field('dir_cp', 'string', label=T('Código Postal')),
        Field('dir_telefono', 'string', label=T('Teléfono')),
        Field('dir_movil', 'string', label=T('Móvil')),
        Field('dir_email', requires=IS_EMAIL(), label=T('Email')),
        Field('nombre_suc', 'string', label=T('Nombre Sucursal')),
    ]

    form = SQLFORM.factory(*campos)

    if form.process().accepted:

        form.vars.empresa_id = request.vars.empresa_id
        form.vars.nombre = request.vars.nombre_suc
        sucursal_id = db_maestro.sucursal.insert(**db_maestro.sucursal._filter_fields(form.vars))

        vars = {'sucursal_id': sucursal_id, 'empresa_id': request.vars.empresa_id}

        response.flash = 'Se han configurado correctamente los datos de la sucursal'
        session.flash = 'Se han configurado correctamente los datos de la sucursal'
        redirect(URL('default', 'index4', vars=vars))

    elif form.errors:
        response.flash = 'Errores en el formulario'
    else:
        response.flash = 'Formulario incompleto'

    return dict(form=form)


def index4():
    """
    Útil para introducir los datos iniciales del departamento y usuario
    """

    fields = [
        Field('pais_id', 'string', label=T('País')),
        Field('estado_id', 'string', label=T('Estado')),
        Field('municipio_id', 'string', label=T('Municipio')),
        Field('localidad_id', 'string', label=T('Localidad')),
        Field('registro_fiscal', 'string', label='Registro Fiscal'),
        Field('dir_calle', 'string', label=T('Calle')),
        Field('dir_num_ext', 'string', label=T('Número Exterior')),
        Field('dir_num_int', 'string', label=T('Número Interior')),
        Field('dir_colonia', 'string', label=T('Colonia')),
        Field('dir_cp', 'string', label=T('Código Postal')),
        Field('dir_telefono', 'string', label=T('Teléfono')),
        Field('dir_movil', 'string', label=T('Móvil')),
        Field('dir_email', requires=IS_EMAIL(), label=T('Email')),
        Field('nombre_emp', 'string', label=T('Nombre Empleado')),
        Field('ap_paterno', 'string', label=T('Apellido Paterno')),
        Field('ap_materno', 'string', label=T('Apellido Materno')),
        Field('nombre_pue', 'string', label=T('Puesto')),
        Field('nombre_dep', 'string', label=T('Departamento')),
    ]

    form = SQLFORM.factory(*fields)

    if form.process().accepted:

        # insertar departamento
        form.vars.sucursal_id = request.vars.sucursal_id
        form.vars.nombre = request.vars.nombre_dep
        departamento_id = db_maestro.departamento.insert(
                **db_maestro.departamento._filter_fields(form.vars)
                )

        # insertar puesto
        form.vars.nombre = request.vars.nombre_pue
        puesto_id = db_maestro.puesto.insert(**db_maestro.puesto._filter_fields(form.vars))

        # insertar empleado
        form.vars.nombre = form.vars.nombre_emp
        form.vars.departamento_id = departamento_id
        form.vars.puesto_id = puesto_id
        empleado_id = db_maestro.empleado.insert(
                **db_maestro.empleado._filter_fields(form.vars)
                )

        vars = {'empresa_id': request.vars.empresa_id}

        session.flash = 'Se han configurado correctamente los datos de la sucursal'
        #redirect(URL('default', 'index5', vars=vars))

    elif form.errors:
        response.flash = 'Errores en el formulario'
    else:
        response.flash = 'Formulario incompleto'

    return dict(form=form)

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db_maestro)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())

def cookieCreate():
        response.cookies['login_general_ledger'] = auth.user['email']
        response.cookies['login_general_ledger']['expires'] = 24 * 3600
        response.cookies['login_general_ledger']['path'] = '/'

        response.cookies['picture_usr'] = session.picture
        response.cookies['picture_usr']['expires'] = 24 * 3600
        response.cookies['picture_usr']['path'] = '/'

        response.cookies['id_usuario']= auth.user['id']
        response.cookies['id_usuario']['expires'] = 24 * 3600
        response.cookies['id_usuario']['path'] = '/'

def cookieDelete():
        response.cookies['login_general_ledger'] = 'invalid'
        response.cookies['login_general_ledger']['expires'] = -10
        response.cookies['login_general_ledger']['path'] = '/'

        response.cookies['id_usuario']= 'invalid'
        response.cookies['id_usuario']['expires'] = 24 * 3600
        response.cookies['id_usuario']['path'] = '/'

        response.cookies['picture_usr'] = 'invalid'
        response.cookies['picture_usr']['expires'] = -10
        response.cookies['picture_usr']['path'] = '/'


def index():
    import urllib
    import urllib2
    import gluon.contrib.simplejson
    import time
    from gluon.storage import Storage
    from uuid import uuid4
    from gluon.storage import Storage

    login =''
    hoy = time.strftime("%A %d de %B del %Y.")
    empresa_id = request.args(0)
    if empresa_id:
        session.instancias = empresa_id

    if session.auth:
        if not request.cookies.has_key('login_general_ledger'):
            cookieCreate()
            #session.instancias = []
            session.instancias = 0

        #código repetido, digno de eliminarse
        mias = db_maestro(
                (db_maestro.mi_empresa.user_id == auth.user['id']) &\
                (db_maestro.mi_empresa.empresa_id == db_maestro.empresa.id) &\
                (db_maestro.mi_empresa.tipo == 1)
           ).select(
                   db_maestro.empresa.razon_social,
                   db_maestro.empresa.id
                   )

        compartidas = db_maestro(
                (db_maestro.mi_empresa.user_id == auth.user['id']) &\
                (db_maestro.mi_empresa.empresa_id == db_maestro.empresa.id) &\
                (db_maestro.mi_empresa.tipo == 2)
            ).select(
                    db_maestro.empresa.razon_social,
                    db_maestro.empresa.id
                    )

    elif request.cookies.has_key('login_general_ledger'):
        usuario = db_maestro(db_maestro.auth_user.email==request.cookies['login_general_ledger'].value).select()
        #if 'picture' in data:
        #    session.picture = data['picture']
        user = db_maestro(db_maestro.auth_user.id==usuario[0].id).select().first()
        auth.settings.long_expiration = 3600*24*30 # one month
        auth.settings.remember_me_form = True
        auth.user = Storage(auth.settings.table_user._filter_fields(user, id=True))
        session.auth = Storage(user=auth.user, last_visit=request.now, expiration=auth.settings.expiration)
        session.picture = request.cookies['picture_usr'].value

        #session.instancias = []
        session.instancias = 0

        mias = db_maestro(
                (db_maestro.mi_empresa.user_id == auth.user['id']) &\
                (db_maestro.mi_empresa.empresa_id == db_maestro.empresa.id) &\
                (db_maestro.mi_empresa.tipo == 1)
           ).select(
                   db_maestro.empresa.razon_social,
                   db_maestro.empresa.id
                   )

        compartidas = db_maestro(
                (db_maestro.mi_empresa.user_id == auth.user['id']) &\
                (db_maestro.mi_empresa.empresa_id == db_maestro.empresa.id) &\
                (db_maestro.mi_empresa.tipo == 2)
            ).select(
                    db_maestro.empresa.razon_social,
                    db_maestro.empresa.id
                    )

    else:
        # the user is not logged
        mias = ''
        compartidas = ''        

    return dict(mias=mias, compartidas=compartidas, hoy=hoy)


def catalogo_nivel(nivel):
    catalogo = db.executesql("SELECT node.num_cc, node.descripcion,(COUNT(parent.descripcion) - 1) AS depth, "\
                   " node.id, node.cc_vista_id, node.cc_naturaleza_id "\
                   " FROM cc_empresa AS node , cc_empresa AS parent "\
                   " WHERE node.lft BETWEEN parent.lft AND parent.rgt "\
                   " GROUP BY node.id "\
                   " HAVING (COUNT(parent.descripcion) - 1)  <= "+nivel+""\
                   " ORDER BY node.lft;"\
                   )
    return catalogo

def importe_cuenta_balanza(num_cc, cc_naturaleza_id, fecha):
    filtro=" AND poliza.fecha_usuario <= '"+str(fecha)+"'"
    cantidad = db.executesql("SELECT SUM(debe) as suma_debe, SUM(haber) as suma_haber  "\
                                 " FROM poliza, asiento, cc_empresa "\
                                 " WHERE asiento.cc_empresa_id = cc_empresa.id "\
                                 " AND poliza.id = asiento.poliza_id "\
                                 " AND poliza.estatus= 3 "\
                                 " AND cc_empresa.num_cc like '"+num_cc+"%'"\
                                 +filtro)
    debe=cantidad[0][0] if cantidad[0][0]!=None else 0.0
    haber=cantidad[0][1] if cantidad[0][1]!=None else 0.0
    if cc_naturaleza_id==2: #Deudora
        importe=debe-haber
    else:
        importe=haber-debe
    return importe
