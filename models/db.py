# -*- coding: utf-8 -*-
import os
import urllib2
from gluon.storage import Storage
import locale
locale.setlocale( locale.LC_ALL, 'es_MX.UTF-8' )

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

path = os.path.join(request.folder, 'databases/master/')
if not os.path.isdir(path):
    os.mkdir(path)

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db_maestro = DAL(
            'postgres://web2py:w3b2py@localhost/contabilidad', 
            migrate=False,
            fake_migrate=True,
            folder=path 
            )
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db_maestro = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db_maestro=db_maestro)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db_maestro)

crud, service, plugins = Crud(db_maestro), Service(), PluginManager()

## create all tables needed by auth if not custom tables
# auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'smtp.gmail.com:587'
mail.settings.sender = 'datawork.mx@gmail.com'
mail.settings.login = 'datawork.mx:d4t4w0rk'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
auth.settings.expiration = 3600 * 24 * 30
auth.settings.remember_me_form = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
#from gluon.contrib.login_methods.janrain_account import use_janrain
#use_janrain(auth, filename='private/janrain.key')

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
#from gluon.contrib.login_methods.rpx_account import use_janrain
#use_janrain(auth, filename='private/janrain.key')
from gluon.contrib.login_methods.oauth20_account import OAuthAccount

try:
    import json
except ImportError:
    from gluon.contrib import simplejson as json


class GoogleAccount(OAuthAccount):
    "OAuth 2.0 for Google"

    def __init__(self):
        with open(os.path.join(request.folder, 'private/google_auth.json'), 'rb') as f:
            gai = Storage(json.load(f)['web'])

        OAuthAccount.__init__(self, None, gai.client_id, gai.client_secret,
                              gai.auth_uri, gai.token_uri,
                              scope='https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email',
                              approval_prompt='force', state="auth_provider=google")

    def get_user(self):

        token = self.accessToken()
        if not token:
            return None

        uinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo?access_token=%s' % urllib2.quote(token, safe='')

        uinfo = None

        try:
            uinfo_stream = urllib2.urlopen(uinfo_url)
        except:
            session.token = None
            return
        data = uinfo_stream.read()
        uinfo = json.loads(data)

        username = uinfo['id']
        if 'picture' in uinfo:
            session.picture = uinfo['picture']

        return dict(first_name = uinfo['given_name'],
                    last_name = uinfo['family_name'],
                    username = username,
                    email = uinfo['email'])

auth.settings.login_form=GoogleAccount()

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db_maestro.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db_maestro.mytable.insert(myfield='value')
## >>> rows=db_maestro(db_maestro.mytable.myfield=='value').select(db_maestro.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db_maestro)

db_maestro.define_table('pais',
    Field('nombre', 'string'),
    format='%(nombre)s',
    migrate=True,fake_migrate=True
    )

db_maestro.define_table('estado',
    Field('clave_interna', 'string'),
    Field('nombre', 'string'),
    Field('pais_id', 'reference pais'),
    format='%(nombre)s'
    )

db_maestro.define_table('municipio',
    Field('clave_interna'),
    Field('nombre', 'string'),
    Field('estado_id', 'reference estado'),
    format='%(nombre)s'
    )

db_maestro.define_table('localidad',
    Field('clave_interna', 'string'),
    Field('nombre', 'string'),
    Field('lat_grad', 'string'),
    Field('lon_grad', 'string'),
    Field('lat_dec', 'string'),
    Field('lon_dec', 'string'),
    Field('municipio_id', 'reference municipio'),
    format='%(nombre)s'
    )

db_maestro.define_table('banco',
    Field('nombre', 'string', label='Nombre del Banco'),
    format='%(nombre)s'
    )

db_maestro.define_table('persona',
    Field('registro_fiscal', 'string', label='Registro Fiscal'),
    Field('dir_calle', 'string', label='Calle'),
    Field('dir_num_ext', 'string', label='Número Exterior'),
    Field('dir_num_int', 'string', label='Número Interior'),
    Field('dir_colonia', 'string', label='Colonia'),
    Field('dir_cp', 'string', label='Código Postal'),
    Field('dir_telefono', 'string', label='Teléfono'),
    Field('dir_movil', 'string', label='Móvil'),
    Field('dir_email', requires=IS_EMAIL(), label='Email'),
    Field('localidad_id', 'reference localidad', label='Localidad/Ciudad')
    )

db_maestro.define_table('empresa',
    Field('razon_social', 'string', label='Razón Social'),
    Field('nombre_comercial', 'string', label='Nombre Comercial'),
    db_maestro.persona,
    format='%(razon_social)s'
    )

db_maestro.define_table('empresa_banco',
    Field('empresa_id','reference empresa'),
    Field('banco_id','reference banco'),
    Field('clabe','string', label='Número de Cuenta Interbancaria'),
    Field('cuenta','string', label='Número de Cuenta Bancaria'),
    format='%(banco_id)s %(cuenta)s'
    )

db_maestro.define_table('sucursal',
    Field('empresa_id', 'reference empresa', label='Empresa'),
    Field('nombre', 'string', label='Nombre de la Sucursal'),
    db_maestro.persona,
    format='%(nombre)s'
    )

db_maestro.define_table('departamento',
    Field('sucursal_id', 'reference sucursal', label='Sucursal'),
    Field('nombre', 'string'),
    format='%(nombre)s'
    )

db_maestro.define_table('puesto',
    Field('departamento_id', 'reference departamento', label='Departamento'),
    Field('nombre', 'string'),
    format='%(nombre)s'
    )

db_maestro.define_table('empleado',
    Field('puesto_id', 'reference puesto'),
    Field('nombre', 'string', label='Nombre'),
    Field('ap_paterno', 'string', label='Apellido Paterno'),
    Field('ap_materno', 'string', label='Apellido Materno'),
    db_maestro.persona,
    format='%(nombre)s %(ap_paterno)s %(ap_materno)s'
    )

db_maestro.define_table('proveedor',
    Field('razon_social', 'string', label='Razón Social'),
    Field('nombre_comercial', 'string', label='Nombre Comercial'),
    db_maestro.persona,
    Field('producto_comercial', 'string', label='Producto comercial'),
    format='%(razon_social)s'
    )

db_maestro.define_table('proveedor_banco',
    Field('proveedor_id','reference proveedor'),
    Field('banco_id','reference banco'),
    Field('clabe','string', label='Número de Cuenta Interbancaria'),
    Field('cuenta','string', label='Número de Cuenta Bancaria'),
    format='%(banco_id)s %(cuenta)s'
    )

auth.define_tables(username=False, signature=False)
db_maestro.auth_user._format = '%(first_name)s %(last_name)s (%(email)s)'
## auth.settings.everybody_group_id = 1 ##asignar a nuevos usuarios a un grupo por default 1=ADMIN, 2=BASICO, 3=ETC
## auth.settings.create_user_groups = None

db_maestro.define_table('cc_naturaleza',
   Field('nombre','string'),
   format='%(nombre)s'
   )

#Lo siguiente eliminar en PRODUCCION
if not db_maestro(db_maestro.cc_naturaleza.id>0).count():
    db_maestro.cc_naturaleza.insert(
        nombre = 'ACREEDORA',
    )
    db_maestro.cc_naturaleza.insert(
        nombre = 'DEUDORA',
    )
    db_maestro.cc_naturaleza.insert(
        nombre = 'CAPITAL',
    )
    db_maestro.cc_naturaleza.insert(
        nombre = 'RESULTADO',
    )

db_maestro.define_table('cc_vista',
   Field('nombre','string'),
   format='%(nombre)s'
   )

if not db_maestro(db_maestro.cc_vista.id>0).count():
    db_maestro.cc_vista.insert(
        nombre = 'ACUMULATIVA',
    )
    db_maestro.cc_vista.insert(
        nombre = 'DETALLE',
    )
# ##

# Nested Set Model
db_maestro.define_table('cc_empresa',
    Field('empresa_id', 'reference empresa', label='Empresa'),
    Field('num_cc', 'string', label='Número de Cuenta Contable'), #considerar como clave secundaria
    Field('descripcion', 'string', label='Descripción'),
    Field('clave_sat', 'string', label='Clave SAT'),
    Field('cc_naturaleza_id', 'reference cc_naturaleza'), ##ACREEDORA, DEUDORA, DE RESULTADO
    Field('cc_vista_id', 'reference cc_vista'), ## DETALLE, ACUMULATIVA
    Field('lft','integer', default=0),
    Field('rgt','integer', default=0),
    format='%(num_cc)s %(descripcion)s'
    )

db_maestro.define_table('tipo_poliza',
    Field('nombre','string'),
    format='%(nombre)s'
    )

# Eliminar en PRODUCCION
if not db_maestro(db_maestro.tipo_poliza.id>0).count():
    db_maestro.tipo_poliza.insert(
        nombre = 'INGRESO',
    )
    db_maestro.tipo_poliza.insert(
        nombre = 'EGRESO',
    )
    db_maestro.tipo_poliza.insert(
        nombre = 'DIARIO',
    )
# ///

db_maestro.define_table('poliza',
    Field('f_poliza', 'datetime', default=request.now, label='Fecha de Póliza'),
    Field('concepto_general', 'string', label='Concepto de la Póliza'),
    Field('tipo', 'reference tipo_poliza'),
    Field(
        'importe',
        'double', 
        default=0.0,
        represent = lambda value, row: calcula_importe(row.id) if row.id else 0.0
        )
)
db_maestro.poliza.id.label='#Póliza'

db_maestro.define_table('asiento',
    Field('poliza_id', 'reference poliza', label='#Póliza'),
    Field('f_asiento', 'datetime', default=request.now, label='Fecha de Asiento'),
    Field('cc_empresa_id', 'reference cc_empresa', label='Cuenta Contable'),
    Field('concepto_asiento', 'string'),
    Field('debe', 'double', default=0.0, represent = lambda value, row: DIV(locale.currency(value, grouping=True ), _style='text-align: right;') if row else 0.0),
    Field('haber', 'double', default=0.0, represent = lambda value, row: DIV(locale.currency(value, grouping=True ), _style='text-align: right;') if row else 0.0)
)
db_maestro.asiento.id.label='#Asiento'

# Tablas para configuración de reportes
db_maestro.define_table('reporte',
    Field('nombre', 'string', label='Nombre'),
    Field('descripcion', 'string', label='Descripción'),
    migrate=False,
    format='%(descripcion)s',
    )
db_maestro.define_table('seccion_reporte',
    Field('reporte_id', 'reference reporte', label='Reporte'),
    Field('nombre', 'string', label='Nombre de la sección'),
    Field('descripcion', 'string', label='Etiqueta'),
    migrate=False,
    format='%(nombre)s %(descripcion)s',
    )
db_maestro.define_table('cuentas_seccion_reporte',
    Field('seccion_reporte_id', 'reference seccion_reporte', label='Etiqueta'),
    Field('cc_empresa_id', 'reference cc_empresa', label='Cuenta'),
    migrate=False,
    format='%(cc_empresa_id)s',
    )

db_maestro.define_table('mi_empresa',
                Field('user_id','reference auth_user'),
                Field('empresa_id','reference empresa'),
                Field('tipo','integer', default=1, requires=IS_IN_SET({1:'PROPIA',2:'COMPARTIDA'})),
                )

db_maestro.define_table('invitacion',
        Field('user_id', 'reference auth_user'),
        Field('empresa_id', 'reference empresa'),
        #Field('email_invitado', requires=IS_EMAIL(), label='Email'),
        Field('email_invitado', label='Email'),
        Field('fecha', 'datetime'),
        Field('url_hash', 'string')
)


#from applications.general_ledger.modules.DBs import *
#EmpresaDB = local_import(EmpresaDB)
#empresas = EmpresaDB(db_maestro, user_id = auth.user['id'])
