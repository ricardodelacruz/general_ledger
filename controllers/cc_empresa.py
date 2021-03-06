# coding: utf8
if session.instancias:
    db = empresas.dbs[int(session.instancias)]
(auth.user or request.args(0) == 'login') or redirect(URL('default', 'user', args='login'))

import csv



def index():
    tipo="config"
    empresa_id = request.args(0)

    if empresa_id:
        session.instancias = empresa_id
        
    cc_empresa = ul_list(tipo)
    return dict(cc_empresa = cc_empresa)

def ancestor(num_cc):
    tabla = db['cc_empresa']
    node = db(tabla.num_cc == num_cc).select().first()
    return db( (tabla.lft < node.lft) & (tabla.rgt > node.rgt) ).select(tabla.num_cc, orderby=tabla.lft).last()

def cc_wizard():
    tipo="wizard"
    empresa_id = request.vars.empresa_id
    cc_empresa = ul_list(tipo, empresa_id)
    return dict(cc_empresa=cc_empresa)


##@auth.requires_permission('cc_grid')
def balanza():
    tipo="grid"
    cc_empresa = ul_list2()
    return dict(cc_empresa=cc_empresa)

def cc_grid():
    tipo="config"
    empresa_id=int(session.instancias)
    cc_empresa = ul_list(tipo)
    return dict(cc_empresa=cc_empresa)

def ul_list2():
    tipo_cuentas=request.vars.tipo_cuentas

    categories = db.executesql("SELECT node.num_cc, node.descripcion,(COUNT(parent.descripcion) - 1) AS depth, "\
                   "node.id, node.cc_vista_id "\
                   "FROM cc_empresa AS node , cc_empresa AS parent "\
                   "WHERE node.lft BETWEEN parent.lft AND parent.rgt "\
                   "GROUP BY node.id "\
                   "ORDER BY node.lft;")


    cadena='<div class="table-responsive">'\
	'<table class="table">'\
	'	<thead>'\
	'		<tr>'\
	'			<th style="width:10px;">Op</th>'\
	'			<th>No. cuenta</th>'\
	'			<th>Descripción</th>'\
	'			<th>Debe</th>'\
	'			<th>Haber</th>'\
	'		</tr>'\
	'	</thead>'\
	'	<tbody>'

    for cat in categories:
        id_padre= ancestor(cat[0])
        if id_padre:
            padre=id_padre.num_cc
        else:
            padre=''

        padre = padre.replace('.', '')
        clase_tr= 'hijo-'+XML(str(padre))+' padre'
        #clase_tr= "child-row "+str(id_padre)+" parent"
        cantidad = db.executesql("SELECT SUM(debe) as suma_debe, SUM(haber) as suma_haber  "\
                                 "FROM asiento, cc_empresa "\
                                 "WHERE asiento.cc_empresa_id = cc_empresa.id "\
                                 "AND cc_empresa.num_cc like '"+cat[0]+"%'")
        debe=cantidad[0][0] or 0.0
        haber=cantidad[0][1] or 0.0
        id_row = cat[0]
        color=XML(color_nivel(cat[2]))
        padding=XML(str(cat[2]*20))
        if tipo_cuentas=='con_saldo':
            if (cantidad[0][0])!=None or (cantidad[0][1]!=None):
                cadena += """<tr id='{}' class='{}' style=color:'{}'>\
                <td><i class='fa fa-plus-circle'></i></td>\
                <td style="padding-left: {}px;">{}</td>\
                <td>{}</td>\
                <td>{}</td>\
                <td>{}</td>\
                </tr>""".format(XML(id_row), clase_tr, color,
                        padding, XML(cat[0]), 
                        XML(cat[1]), 
                        XML(debe), 
                        XML(haber)
                        )
        else:
            cadena += """<tr id='{}' class='{}' style=color:'{}'>\
            <td><i class='fa fa-plus-circle'></i></td>\
            <td style="padding-left: {}px;">{}</td>\
            <td>{}</td>\
            <td>{}</td>\
            <td>{}</td>\
            </tr>""".format(XML(id_row), clase_tr, color,
                    padding, XML(cat[0]), 
                    XML(cat[1]), 
                    XML(debe), 
                    XML(haber)
                    )

    cadena+='</tbody></table></div>'
    cadena=XML(cadena)
    return cadena


def ul_list(tipo):
    global db
    cadena=''
    if tipo=='wizard':
        db = db_maestro
        cadena='<div class="tree "><ul>'
    elif tipo=='grid':
        cadena='<div class="tree"><ul>'
    else:
        cadena='<div class="tree"><ul>'
        
    categories = db.executesql("SELECT node.num_cc, node.descripcion,\
                   (COUNT(parent.descripcion) - 1) AS depth,\
                   node.id, node.cc_vista_id\
                   FROM cc_empresa AS node, cc_empresa AS parent\
                   WHERE node.lft BETWEEN parent.lft AND parent.rgt\
                   GROUP BY node.id\
                   ORDER BY node.lft;")

    n=0
    for cat in categories:
        if cat[2]==0:
            display=''
        else:
            display='style="display:None"'
           
        cantidad = db.executesql("SELECT SUM(debe) as suma_debe, SUM(haber) as suma_haber  "\
                                 "FROM asiento, cc_empresa "\
                                 "WHERE asiento.cc_empresa_id = cc_empresa.id "\
                                 "AND cc_empresa.num_cc like '"+cat[0]+"%'")
        debe=cantidad[0][0] if cantidad[0][0]!=None else 0.0
        haber=cantidad[0][0] if cantidad[0][0]!=None else 0.0
        if cat[2]>n:
            cadena+='<ul><li '+display+' >'
        elif cat[2]==n:
            if n>0:
                cadena+='</li><li '+display+' >'
            else:
                cadena+='<li>'
        else:
            for i in range(cat[2],n):
                cadena+='</li></ul>'
            cadena+='<li '+display+'>'

        if tipo=="config":
            cadena+='<span><i class="fa fa-minus-circle"></i></span> '

            cadena+= '<div class="btn-group"><button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">'+cat[0]+' '+cat[1]+' <div class="fa fa-caret-down"></div></button><ul class="dropdown-menu" role="menu"><div class="menu-boton" data-toggle="modal" data-target="#modal_editar"><a href="javascript:editar_cuenta('+str(cat[3])+')" >Editar</a></div><div class="menu-boton" ><a href="javascript:eliminar_cc(\''+str(cat[0])+'\',\''+str(cat[1])+'\')" >Eliminar</a></div>'
            if cat[4]==1:
                cadena+='<div class="menu-boton" data-toggle="modal" data-target="#modal_crear"><a href="javascript:crear_cuenta('+str(cat[3])+','+str(cat[4])+')">Crear Sub-cuenta</a></div>'
            cadena+='</ul></div>'

        elif tipo=="wizard":
            cadena+='<span><i class="fa fa-minus-circle"></i> '+cat[0]+' '+cat[1]+'</span> '
        elif tipo=="grid":
            cadena+='<span><i class="fa fa-minus-circle"></i><div class="row_grid"><div class="cell_grid"></div><div class="cell_grid">   '+XML(cat[0])+' </div><div class="cell_grid"> '+cat[1]+' </div><div class="cell_grid"> '+XML(debe) +' </div><div class="cell_grid">'+XML(haber)+'</div>  </div></span> '
        n=cat[2]
    cadena+='</li></ul></div>'
    cadena=XML(cadena)
    return cadena


def ul_list_back():
    categories = db(db.cc_empresa.id>0).select(db.cc_empresa.ALL, orderby=db.cc_empresa.lft)

    rgt = []
    tree = []
    for cat in categories:
        if len(rgt) > 0:
            if rgt[-1] > cat.rgt:
                # open UL
                pass
            while rgt[-1] < cat.rgt:
                rgt.pop()
                if len(rgt) == 0:
                    break
        branch = UL(_class="branch")
        p=branch
        for i in range(len(rgt)):
            child = UL(_class="branch_leaf")
            p.append(LI(child, _class="leaf"))
            p=child
        p.append(LI(A(cat.num_cc+' '+cat.descripcion, _href='/'+cat.num_cc), _class="leaf",))
        tree.append(branch)
        rgt.append(cat.rgt)
    seed = DIV(_class="tree well")
    for branch in tree:
        seed.append(DIV(branch, _class="root_branch"))
    seed.components.extend([XML("""
        <style>
        .branch {
            padding: 0;
            margin: 0;
            padding-left: 10px;
            list-style-type: none;
        }
        .branch_leaf {
            padding: 0;
            margin: 0;
            padding-left: 20px;
            list-style-type: none;
        }
        .leaf {
            list-style-type: none;
        }

        </style>
                """)])

    return seed


def ancestors(num_cc, *fields):
    tabla = db['cc_empresa']
    node = db(tabla.num_cc == num_cc).select().first()
    return db( (tabla.lft <= node.lft) & (tabla.rgt >= node.rgt) ).select(tabla.ALL, orderby=tabla.lft, *fields)


def descendants(num_cc, *fields):
    tabla = db['cc_empresa']
    node = db(tabla.num_cc == num_cc).select().first()
    return db( (tabla.lft >= node.lft) & (tabla.rgt <= node.rgt) ).select(tabla.ALL, orderby=tabla.lft, *fields)


def add_node(
        padre_id=None,
        num_cc=None,
        descripcion=None,
        clave_sat=None,
        cc_naturaleza_id=None,
        cc_vista_id=None
        ):

    #empresa_id = request.vars.empresa_id
    #db = empresas.dbs[int(empresa_id)]
    #db = db_maestro
    tabla = db['cc_empresa']

    if padre_id:
        if isinstance(padre_id, int):
            padre = db(tabla.id == padre_id).select().first()
        else:
            padre = db(tabla.num_cc == padre_id).select().first()

        db(tabla.rgt >= padre.rgt).update(rgt=tabla.rgt+2)
        db(tabla.lft >= padre.rgt).update(lft=tabla.lft+2)

        node_id = tabla.insert(
                num_cc=num_cc,
                descripcion=descripcion,
                clave_sat=clave_sat,
                cc_naturaleza_id = cc_naturaleza_id,
                cc_vista_id = cc_vista_id,
                lft=padre.rgt,
                rgt=padre.rgt+1
                )
    else:
        top = db(tabla.lft > 0).select(orderby=tabla.rgt).last()
        if top:
            node_id = tabla.insert(
                    num_cc=num_cc,
                    descripcion=descripcion,
                    clave_sat=clave_sat,
                    cc_naturaleza_id=cc_naturaleza_id,
                    cc_vista_id=cc_vista_id,
                    lft=top.rgt+1,
                    rgt=top.rgt+2
                    )
        else:
            node_id = tabla.insert(
                    num_cc = num_cc,
                    descripcion = descripcion,
                    clave_sat = clave_sat,
                    cc_naturaleza_id = cc_naturaleza_id,
                    cc_vista_id = cc_vista_id,
                    lft = 1,
                    rgt = 2
                    )
    return node_id


def delete_node(num_cc):
    # Se elimina el nodo y también sus ramas
    tabla = db['cc_empresa']
    node = db(tabla.num_cc == num_cc).select().first()
    if node:
        children = db( (tabla.lft >= node.lft) & (tabla.rgt <= node.rgt) )

        diff = node.rgt - node.lft + 1
        rgt = node.rgt
        lft = node.lft

        children.delete() #se eliminan los hijos
        db(tabla.id == node.id).delete() #se elimina el nodo deseado

        db(tabla.lft > rgt).update(lft=tabla.lft - diff)
        db(tabla.rgt > rgt).update(rgt=tabla.rgt - diff)
        return True
    return False


def cat_cuentas_sat(empresa_id,cc_preconf):
    cc_sat=[]
    if cc_preconf=='1':
        archivo='cuentas_sat'
    else:
        archivo='cuentas_sat_nivel_uno'

    with open('applications/general_ledger/private/'+archivo+'.csv', 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            fila=[]
            fila.append(str(empresa_id))
            fila.append(row[0])
            fila.append(row[1])
            fila.append(row[2])
            fila.append(row[3])
            fila.append(row[4])
            cc_sat.append(fila)

    return cc_sat

def cat_cuentas_personal(empresa_id,archivo):
    cc_personal=[]
    file = archivo
    reader = csv.reader(file)
    for row in reader:
        fila=[]
        fila.append(str(empresa_id))
        fila.append(row[0])
        fila.append(row[1])
        fila.append(row[2])
        fila.append(row[3])
        fila.append(row[4])
        cc_personal.append(fila)
    return cc_personal

def cat_cuentas_personal(empresa_id,archivo):
    cc_personal=[]
    file = archivo
    reader = csv.reader(file)
    db(db.cc_empresa).delete()
    db.executesql('alter sequence cc_empresa_id_seq restart with 1')
    campos=['lft','rgt', 'descripcion']
    for row in reader:
        valores=[]
        valores.append(int(row[0]))
        valores.append(int(row[1]))
        valores.append(row[2])
        dictionary = dict(zip(campos, valores))
        db[db.cc_empresa].insert(**dictionary)
    return

def wiz_cc():
        
        from datetime import date
    #db_ = db_maestro
        empresa_id = request.vars.empresa_id
        db = empresas.dbs[int(empresa_id)]
        msg=""
    #try:
        tabla = db['cc_empresa']
        cc_preconf = request.vars.cc_preconf

        db(db.mes).delete()
        db.executesql('alter sequence mes_id_seq restart with 1')
        db.mes.insert(nombre = 'ENERO')
        db.mes.insert(nombre = 'FEBRERO')
        db.mes.insert(nombre = 'MARZO')
        db.mes.insert(nombre = 'ABRIL')
        db.mes.insert(nombre = 'MAYO')
        db.mes.insert(nombre = 'JUNIO')
        db.mes.insert(nombre = 'JULIO')
        db.mes.insert(nombre = 'AGOSTO')
        db.mes.insert(nombre = 'SEPTIEMBRE')
        db.mes.insert(nombre = 'OCTUBRE')
        db.mes.insert(nombre = 'NOVIEMBRE')
        db.mes.insert(nombre = 'DICIEMBRE')

        db(db.anio).delete()
        db.executesql('alter sequence mes_id_seq restart with 1')
        db.anio.insert(numero = date.today().year)

        db(db.estatus_periodo).delete()
        db.executesql('alter sequence estatus_periodo_id_seq restart with 1')
        db.estatus_periodo.insert(nombre = 'ABIERTO')
        db.estatus_periodo.insert(nombre = 'CERRADO')
        db.estatus_periodo.insert(nombre = 'ACTUAL')

        db(db.cc_vista).delete()
        db.executesql('alter sequence cc_vista_id_seq restart with 1')
        db.cc_vista.insert(nombre = 'ACUMULATIVA')
        db.cc_vista.insert(nombre = 'DETALLE')
    
        db(db.cc_naturaleza).delete()
        db.executesql('alter sequence cc_naturaleza_id_seq restart with 1')
        db.cc_naturaleza.insert(nombre = 'ACREEDORA')
        db.cc_naturaleza.insert(nombre = 'DEUDORA')
        db.cc_naturaleza.insert(nombre = 'CAPITAL')
        db.cc_naturaleza.insert(nombre = 'RESULTADO')
    
        db(db.tipo_poliza).delete()
        db.executesql('alter sequence tipo_poliza_id_seq restart with 1')
        db.tipo_poliza.insert(nombre = 'INGRESO')
        db.tipo_poliza.insert(nombre = 'EGRESO')
        db.tipo_poliza.insert(nombre = 'DIARIO')
        
        db(db.estatus_poliza).delete()
        db.executesql('alter sequence estatus_poliza_id_seq restart with 1')
        db.estatus_poliza.insert(nombre = 'EN REVISIÓN')
        db.estatus_poliza.insert(nombre = 'REVISADA')
        db.estatus_poliza.insert(nombre = 'APLICADA')

        #cc_preconf = '1'
        if type(request.vars.csvfile) != str:
        #f request.vars.csvfile!=None:
            file = request.vars.csvfile.file
            cc_sat = cat_cuentas_personal(empresa_id, file)

        else:
            cc_sat = cat_cuentas_sat(empresa_id, cc_preconf)
        
            for cuenta in cc_sat:
        
                num_cc = cuenta[1]
                len_num_cc = len(num_cc)
        
                if len_num_cc > 1:
                    num_cc_i = num_cc[::-1]
                    ultimo_punto = num_cc_i.find(".")
                    num_cc = num_cc[:-(ultimo_punto+1)]
                    padre_id = int(db(tabla.num_cc == num_cc).select().first().id)
                else:
                    padre_id = None
        
                add_node(padre_id, str(cuenta[1]), str(cuenta[2]),
                        str(cuenta[3]), cuenta[4], cuenta[5])
        
    #except:
    #    msg="Hubo un error al leer el archivo"
    #    db_.rollback()
    #else:
    #    db_.commit()
        redirect(URL('default','empresa',args=[empresa_id]))
        return XML(msg)


def crear_cc(form):
    if form.record:
        form.vars.num_cc = form.vars.num_cc
    elif (form.vars.num_cc != ''):
        empresa_id=3
        niveles_cc_empresa=db(db.niveles_cc_empresa.empresa_id==empresa_id).select()
        niveles_cc=niveles_cc_empresa[0]
        if form.vars.tipo_cc_id=='1':#Acumulativa
            num_niv=int(niveles_cc['digitos_cc_acum'])
        elif form.vars.tipo_cc_id=='2':#Auxiliar
            num_niv=int(niveles_cc['digitos_cc_aux'])

        num_cc= form.vars.num_cc
        str(num_cc).zfill(num_niv)

        form.vars.num_cc = form.vars.cuenta_padre+'.'+ num_cc
    return

def listar():
    db.cc_empresa.num_cc.represent = lambda value, row: DIV(value if value!='' else '-', _class='num_cc', _id=str(row.id)+'.num_cc')
    form = SQLFORM.smartgrid(db.cc_empresa,
                            onvalidation = crear_cc,
                            linked_tables=['empresa'])
    return dict(form=form)

def actualiza_cc_empresa():
    id, column = request.post_vars.id.split('.')
    value = request.post_vars.value
    db(db.cc_empresa.id == id).update(**{column:value})
    return value

@auth.requires_login()
def crear_cuenta():
    if request.vars.num_cc_padre:
        cc_empresa=db(db.cc_empresa.id==request.vars.num_cc_padre).select(db.cc_empresa.ALL)
    else:
        cc_empresa=db(db.cc_empresa).select(db.cc_empresa.ALL)
    cc_vista=db(db.cc_vista).select(db.cc_vista.ALL)
    cc_naturaleza=db(db.cc_naturaleza).select(db.cc_naturaleza.ALL)

    msg=""

    if request.vars.num_cc:
        
        padre_id=int(request.vars.num_cc_padre)
        num_cc=request.vars.num_cc
        descripcion=request.vars.descripcion
        clave_sat=""
        naturaleza_id=int(request.vars.cc_naturaleza_id)
        vista_id = int(request.vars.cc_vista_id)
        msg = 'Cuenta Creada'
        add_node(padre_id, num_cc, descripcion, clave_sat, naturaleza_id, vista_id)
        redirect(URL('cc_grid'))
    return dict(cc_empresa=cc_empresa,cc_vista=cc_vista,cc_naturaleza=cc_naturaleza, msg=msg)


def editar_cuenta():
    db.cc_empresa.lft.writable=False
    db.cc_empresa.lft.readable=False
    db.cc_empresa.rgt.writable=False
    db.cc_empresa.rgt.readable=False
    form=crud.update(db.cc_empresa, request.vars.id)
    form.element(_type='submit')['_class']='btn btn-primary'
    if request.vars.num_cc:
        redirect(URL('cc_grid'))
    return dict(form=form)


def obtener_empresa(usuario_id):
    empresa_id=1
    return empresa_id


def color_nivel(nivel):
    color = '#000'
    if nivel == 0:
        color = '#000'
    elif nivel == 1:
        color = '#111640'
    elif nivel == 2:
        color = '#212C7F'
    elif nivel == 3:
        color = '#3242BF'
    elif nivel == 4:
        color = '#4258FF'
    elif nivel == 5:
        color = '#168BBF'
    elif nivel == 6:
        color = '#1DBAFF'
    else:
        color = '#28DDFF'
    return color

def hijos_nivel():
    num_cc=str(request.vars.num_cc)
    nivel=request.vars.nivel
    if num_cc!='':
        cuenta= " AND node.num_cc = "+num_cc
    else:
        cuenta= " "
    query="SELECT node.num_cc, node.descripcion, (COUNT(parent.id) - (sub_tree.depthh + 1)) AS depth,"\
                               " node.id, node.cc_vista_id FROM cc_empresa AS node,"\
                               " cc_empresa AS parent,"\
                               " cc_empresa AS sub_parent,"\
                               " ("\
                               " SELECT node.id, node.num_cc, node.descripcion, (COUNT(parent.id) - 1) AS depthh"\
                               " FROM cc_empresa AS node,"\
                               " cc_empresa AS parent"\
                               " WHERE (node.lft BETWEEN parent.lft AND parent.rgt)"\
                               " "+cuenta+""\
                               " GROUP BY node.id"\
                               " ORDER BY node.lft"\
                               " )AS sub_tree"\
                               " WHERE node.lft BETWEEN parent.lft AND parent.rgt"\
                               " AND node.lft BETWEEN sub_parent.lft AND sub_parent.rgt"\
                               " AND sub_parent.id = sub_tree.id"\
                               " GROUP BY node.id"\
                               " HAVING depth = "+nivel+""\
                               " ORDER BY node.lft;"
    hijos = db.executesql(query)
    return hijos

def eliminar_cc():
    if request.vars.num_cc:
        return delete_node(request.vars.num_cc)
    else:
        return False