# coding: utf-8

from gluon.tools import Auth
from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import os
import hashlib


class EmpresaDB(object):
    """
    Recupera las bases de datos
    """

    def __init__(self, db, user_id=None):
        """
        Método init
        """
        self.db = db
        self.user_id = user_id

        #try:
        #    self.user_id = auth.user['id']
        #    empresas = EmpresaDB(db_maestro, user_id = user_id)
        #except:
        #    pass

        email = db(db.auth_user.id == self.user_id).select(
                db.auth_user.ALL
                ).first().email
        self.email = email

        lista = db(
                (db.mi_empresa.empresa_id == db.empresa.id) &\
                (db.mi_empresa.user_id == self.user_id) &\
                (db.mi_empresa.user_id == db.auth_user.id)
            ).select(
                db.empresa.id.with_alias('id'),
                db.empresa.razon_social.with_alias('razon_social'),
                db.mi_empresa.tipo.with_alias('tipo'),
            )

        dbs = {}

        for i in lista:
            instancia=i.id
            if i.tipo == 1:
                # bases de datos propias
                # email = auth.user['email']
                email = self.email
                dbs[i.id] = self.cargar_modelo_de_instancia(email, i.razon_social)

            else:
                # bases de datos que se le comparten al usuario

                # obtener email del propietario
                email = db(
                        (db.mi_empresa.empresa_id == i.id) &\
                        (db.mi_empresa.tipo == 1) &\
                        (db.mi_empresa.user_id == db.auth_user.id)
                        ).select(
                            db.auth_user.email.with_alias('email')
                        ).first().email

                dbs[i.id] = self.cargar_modelo_de_instancia(email, i.razon_social)

        self.dbs = dbs


    def cargar_modelo_de_instancia(self, email, razon_social, vez_primera=True):
        """
        Carga una sola instancia
        """
        import locale
        from gluon.sql import Table
        locale.setlocale( locale.LC_ALL, 'es_MX.UTF-8' )

        hashear = razon_social + email
        nombre_hasheado = hashlib.sha1(hashear).hexdigest()

        path = os.path.join(request.folder, 'databases/{}/'.format(nombre_hasheado))
        if not os.path.isdir(path):
            os.mkdir(path)

        db = DAL(
                'postgres://web2py:w3b2py@localhost/_{}_{}'.format(
                    email, nombre_hasheado
                    ), 
                check_reserved = ['all'],
                migrate = vez_primera,
                folder = path
                )

        # WARNING: auth.user.id es del modelo maestro
        historico = Table(None, 'tmp',
            Field('creada_en', 'datetime',
                default=request.now,
                readable=False
                ),
            Field('creada_por', 'string',
                #default = auth.user.id,
                default = self.user_id,
                readable = False
                ),
            Field('actualizada_en', 'datetime',
                default = request.now,
                readable = False
                ),
            Field('actualizada_por', 'string',
                #default=auth.user.id,
                default = self.user_id,
                readable = False
                )
        )

        db.define_table('pais',
                Field('nombre', 'string'),
                format='%(nombre)s'
                )

        db.define_table('estado',
                Field('clave_interna', 'string'),
                Field('nombre', 'string'),
                Field('pais_id', 'reference pais'),
                format='%(nombre)s'
                )

        db.define_table('municipio',
                Field('clave_interna'),
                Field('nombre', 'string'),
                Field('estado_id', 'reference estado'),
                format='%(nombre)s'
                )

        db.define_table('localidad',
                Field('clave_interna', 'string'),
                Field('nombre', 'string'),
                Field('lat_grad', 'string'),
                Field('lon_grad', 'string'),
                Field('lat_dec', 'string'),
                Field('lon_dec', 'string'),
                Field('municipio_id', 'reference municipio'),
                format='%(nombre)s'
                )

        db.define_table('banco',
                Field('nombre', 'string', label='Nombre del Banco'),
                format='%(nombre)s'
                )

        db.define_table('persona',
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

        db.define_table('empresa',
                Field('razon_social', 'string', label='Razón Social'),
                Field('nombre_comercial', 'string', label='Nombre Comercial'),
                db.persona,
                format='%(razon_social)s'
                )

        db.define_table('empresa_banco',
                Field('empresa_id','reference empresa'),
                Field('banco_id','reference banco'),
                Field('clabe','string', label='Número de Cuenta Interbancaria'),
                Field('cuenta','string', label='Número de Cuenta Bancaria'),
                format='%(banco_id)s %(cuenta)s'
                )

        db.define_table('sucursal',
                Field('empresa_id', 'reference empresa', label='Empresa'),
                Field('nombre', 'string', label='Nombre de la Sucursal'),
                db.persona,
                format='%(nombre)s'
                )

        db.define_table('departamento',
                Field('sucursal_id', 'reference sucursal', label='Sucursal'),
                Field('nombre', 'string'),
                format='%(nombre)s'
                )

        db.define_table('puesto',
                Field('departamento_id', 'reference departamento', label='Departamento'),
                Field('nombre', 'string'),
                format='%(nombre)s'
                )

        db.define_table('empleado',
                Field('puesto_id', 'reference puesto'),
                Field('nombre', 'string', label='Nombre'),
                Field('ap_paterno', 'string', label='Apellido Paterno'),
                Field('ap_materno', 'string', label='Apellido Materno'),
                db.persona,
                format='%(nombre)s %(ap_paterno)s %(ap_materno)s'
                )

        db.define_table('proveedor',
                Field('razon_social', 'string', label='Razón Social'),
                Field('nombre_comercial', 'string', label='Nombre Comercial'),
                db.persona,
                Field('producto_comercial', 'string', label='Producto comercial'),
                format='%(razon_social)s'
                )

        db.define_table('proveedor_banco',
                Field('proveedor_id','reference proveedor'),
                Field('banco_id','reference banco'),
                Field('clabe','string', label='Número de Cuenta Interbancaria'),
                Field('cuenta','string', label='Número de Cuenta Bancaria'),
                format='%(banco_id)s %(cuenta)s'
                )

        db.define_table('cc_naturaleza',
                Field('nombre','string'),
                format='%(nombre)s'
                )

        db.define_table('cc_vista',
           Field('nombre','string'),
           format='%(nombre)s'
           )

        # considerar como clave secundaria
        db.define_table('cc_empresa',
            Field('num_cc', 'string', label='Número de Cuenta Contable'),
            Field('descripcion', 'string', label='Descripción'),
            Field('clave_sat', 'string', label='Clave SAT'),
            Field('cc_naturaleza_id', 'reference cc_naturaleza'),
            Field('cc_vista_id', 'reference cc_vista'),
            Field('lft','integer', default=0),
            Field('rgt','integer', default=0),
            format='%(num_cc)s %(descripcion)s',
            )

        db.define_table('tipo_poliza',
            Field('nombre', 'string'),
            format='%(nombre)s',
        )

        db.define_table('estatus_poliza',
            Field('nombre', 'string'),
            format='%(nombre)s',
        )

        db.define_table('anio',
            Field('numero', 'integer'),
            format='%(numero)s'
        )

        db.define_table('mes',
            Field('nombre', 'string'),
            format='%(nombre)s'
        )

        db.define_table('estatus_periodo',
            Field('nombre', 'string'),
            format='%(nombre)s',
        )

        db.define_table('periodo',
            historico,
            Field('clave', 'string', writable=False),
            Field('inicio', 'date', requires=IS_DATE()),
            Field('fin', 'date', requires=IS_DATE()),
            Field('estatus_periodo_id', 'reference estatus_periodo', default=1),
            Field('anio_id', 'reference anio'),
            Field('mes_id', 'reference mes'),
            Field('consecutivo', 'integer', default=0, readable=False, writable=False),
        )

        db.define_table('poliza',
            Field('folio', 'string'),
            historico,
            Field('concepto_general', 'string', label='Concepto de la Póliza'),
            Field('tipo', 'reference tipo_poliza', default=3),
            Field('estatus', 'reference estatus_poliza', default=1),
            Field('importe', 'double',
                default = 0.0,
                represent = lambda value, row: calcula_importe(row.id) or 0.0
                ),
            Field('folio_externo', 'string', label='Folio Externo'),
            Field('periodo_id', 'reference periodo'),
            Field('fecha_usuario', 'date', label='Fecha de Póliza')
        )
        db.poliza.id.label='#Póliza'

        db.define_table('asiento',
            Field('poliza_id', 'reference poliza', label='#Póliza'),
            historico,
            Field('cc_empresa_id', 'reference cc_empresa', label='Cuenta Contable'),
            Field('concepto_asiento', 'string'),
            Field('debe', 'double', default=0.0),
            Field('haber', 'double', default=0.0)
        )
        db.asiento.id.label='#Asiento'

        # Tablas para configuración de reportes
        db.define_table('reporte',
            Field('nombre', 'string', label='Nombre'),
            Field('descripcion', 'string', label='Descripción'),
            Field('estatus', 'integer', label='Estatus'),
            format='%(descripcion)s'
            )

        db.define_table('seccion_reporte',
            Field('reporte_id', 'reference reporte', label='Reporte'),
            Field('nombre', 'string', label='Nombre de la sección'),
            Field('descripcion', 'string', label='Etiqueta'),
            format='%(nombre)s %(descripcion)s'
            )

        db.define_table('cuentas_seccion_reporte',
            Field('seccion_reporte_id', 'reference seccion_reporte', label='Etiqueta'),
            Field('cc_empresa_id', 'reference cc_empresa', label='Cuenta'),
            format='%(cc_empresa_id)s'
            )

        return db


class Web2Postgres():
    """
    Interactua con postgres
    """

    def __init__(self):
        self.egg = 'What are you looking for?'


    def crear_db(self, nombre, email):
        """
        #ToDo: crear exepciones
        """

        con = connect(
                dbname = 'postgres',
                user = 'web2py',
                host = 'localhost',
                password = 'w3b2py'
                )

        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()

        nombre_hasheado = hashlib.sha1(nombre + email).hexdigest()
        cur.execute('create database "_{}_{}"'.format(email, nombre_hasheado))

        cur.close()
        con.close()


    def eliminar_db(self, nombre, email):
        """
        #ToDo: crear exepciones
        """

        con = connect(
                dbname = 'postgres',
                user = 'web2py',
                host = 'localhost',
                password = 'w3b2py'
                )

        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()

        nombre_hasheado = hashlib.sha1(nombre + email).hexdigest()
        cur.execute('drop database "_{}_{}"'.format(email, nombre_hasheado))

        cur.close()
        con.close()


    def crear_respaldo(self, nombre, email):
        """
        Se crean respaldos
        #ToDo: crear exepciones
        """
        import os
        from datetime import datetime
        from subprocess import Popen, PIPE

        nombre_db = hashlib.sha1(nombre + email).hexdigest()
        usuario = 'web2py'
        host = 'localhost'
        fecha = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

        """
        #cmd = 'pg_dump -U web2py _{}_{} -f {}_{}.sql -h localhost'.format(
        cmd = 'pg_dump -U web2py _{}_{} -f respaldo.sql -h localhost'.format(
                email, nombre_db, nombre_db, fecha
                )
        os.system(cmd)
        """

        path = os.path.join(request.folder, 'static/download/{}/'.format(nombre_db))
        if not os.path.isdir(path):
            os.mkdir(path)

        fc = '_{}_{}'.format(email, nombre_db)
        #f = '{}_{}.sql'.format(nombre_db, fecha)
        f = 'respaldo.sql'
        
        p = Popen(
            ['pg_dump', '-U', usuario, fc, '-f', f, '-h', host],
            stdout = PIPE,
            cwd = path
            )

        #return 'download/{}/{}_{}.sql'.format(nombre_db, nombre_db, fecha)
        return 'download/{}/respaldo.sql'.format(nombre_db, nombre_db, fecha)

    def cerrar_sesiones():
        pass

try:
    user_id = auth.user['id']
    empresas = EmpresaDB(db_maestro, user_id = user_id)
except:
    pass
