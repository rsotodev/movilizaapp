import os
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
from pymysql.cursors import DictCursor
import pymysql

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

def get_bd():
        connection=pymysql.connect(
            host='sql3.freesqldatabase.com', 
            user='sql3757216',          
            password='6BUYsnedVP', 
            database='sql3757216',
            port=3306           
        )
        return connection

@app.route('/')
def index():
    connection = get_bd()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM promociones")
    promociones = cursor.fetchall()

    # Convertir los datos a diccionario
    column_names = [column[0] for column in cursor.description]
    promociones_dict = [dict(zip(column_names, record)) for record in promociones]

    cursor.close()
    connection.close()

    # Pasar las promociones al template
    return render_template('index.html', promociones=promociones_dict, enumerate=enumerate)

@app.route("/MovilizaVehiculos", methods=['GET'])
def cli_vehiculos():
    # Obtener filtros de la solicitud
    marca = request.args.get('marca', 'todos')
    color = request.args.get('color', 'todos')
    transmision = request.args.get('transmision', 'todos')
    nro_asientos = request.args.get('nro_asientos', 'todos')  
 
    # Conectar a la base de datos
    connection = get_bd()
    cur = connection.cursor()

    # Construir consulta SQL con filtros
    consulta = "SELECT * FROM vehiculo WHERE 1=1"
    parametros = []

    if marca and marca != "todos":
        consulta += " AND marca = %s"
        parametros.append(marca)
    if color and color != "todos":
        consulta += " AND color = %s"
        parametros.append(color)
    if transmision and transmision != "todos":
        consulta += " AND transmision = %s"
        parametros.append(transmision)
    if nro_asientos and nro_asientos != "todos":
        consulta += " AND nro_asientos = %s"
        parametros.append(nro_asientos)

    # Ejecutar consulta
    cur.execute(consulta, parametros)
    vehiculo = cur.fetchall()

    # Convertir los datos a diccionario
    column_names = [column[0] for column in cur.description]
    vehiculo_dict = [dict(zip(column_names, record)) for record in vehiculo]

    # Consultar en la DB
    cur.execute("SELECT DISTINCT marca FROM vehiculo")
    marcas = cur.fetchall()

    cur.execute("SELECT DISTINCT color FROM vehiculo")
    colores = cur.fetchall()

    cur.execute("SELECT DISTINCT transmision FROM vehiculo")
    transmisiones = cur.fetchall()

    cur.execute("SELECT DISTINCT nro_asientos FROM vehiculo")
    nro_asientoss = cur.fetchall()

    cur.close()
    connection.close()

    # Renderizar plantilla
    return render_template("vehiculos.html", vehiculo=vehiculo_dict, marcas=marcas, colores=colores,transmisiones=transmisiones,nro_asientoss=nro_asientoss)

@app.route('/MovilizaPromociones', methods=['GET'])
def cli_promociones():
    connection = get_bd()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM promociones")
    promociones = cursor.fetchall()

    # Convertir los datos a diccionario
    column_names = [column[0] for column in cursor.description]
    promociones_dict = [dict(zip(column_names, record)) for record in promociones]

    cursor.close()
    connection.close()

    # Pasar las promociones al template
    return render_template('promociones.html', promociones=promociones_dict)

@app.route('/MovilizaRegistro', methods=['GET','POST'])
def cli_registro():
    nombres = request.form['nombres']
    apellido_paterno = request.form['apellido_paterno']
    apellido_materno = request.form['apellido_materno']
    tipo_documento = request.form['tipo_documento']
    numero_documento = request.form['numero_documento']
    celular = request.form['celular']    
    fecha_nacimiento = request.form['fecha_nacimiento']
    usuario = request.form['usuario']
    contrasena = request.form['contrasena']
    direccion= request.form['direccion']

    if nombres and apellido_paterno and apellido_materno and tipo_documento and numero_documento and fecha_nacimiento and celular and usuario and contrasena and direccion:
        connection = get_bd()
        cursor = connection.cursor()
        sql = """
                INSERT INTO clientes
                (nombres, apellido_paterno, apellido_materno, tipo_documento, numero_documento, celular, fecha_nacimiento, usuario, contrasena, direccion) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        data = (nombres, apellido_paterno, apellido_materno, tipo_documento, numero_documento, celular, fecha_nacimiento, usuario, contrasena, direccion)
        cursor.execute(sql, data)
        connection.commit()

        cursor.close()
        connection.close()

        flash('Cliente registrado correctamente', 'success')
    else:
        flash('Faltan datos, no se pudo registrar el cliente', 'danger')

    return redirect(url_for('registro'))

@app.route('/Registro')
def registro():
    return render_template('registro.html')

@app.route("/Login", methods=["GET", "POST"]) 
def login():
    if request.method == "POST":
        tipo_usuario = request.form['tipo_usuario']
        username = request.form['username']
        password = request.form['password']

        # Conectar a la base de datos
        connection = get_bd()
        cur = connection.cursor()

        if tipo_usuario == "trabajador":
            # Consultar en la base de datos para el empleado
            cur.execute("SELECT * FROM empleados WHERE usuario = %s AND contrasena = %s", (username, password))
        else:
            # Consultar en la base de datos para el usuario común
            cur.execute("SELECT * FROM clientes WHERE usuario = %s AND contrasena = %s", (username, password))
        
        user = cur.fetchone()
        cur.close()
        connection.close()

        if user:
            # Guardar información de usuario en sesión
            full_name=user[1]
            first_name=full_name.split()[0]
            cargo=user[8]
            session['user_id'] = user[0]
            session['tipo_usuario'] = tipo_usuario
            session['nombres'] = first_name
            session['nombre_compl']=user[1]
            session['apellidop']=user[2]
            session['apellidom']=user[3]
            session['tipo_doc']=user[4]
            session['num_doc']=user[5]
            session['direccion']=user[10]
            session['cargo'] = cargo
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')

    return render_template("login.html")
    
@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    tipo_usuario = session['tipo_usuario']

    if tipo_usuario == 'trabajador':
        # Si es trabajador, mostramos su dashboard
        return render_template('dashboard_trabajador.html')
    else:
        # Si es un usuario común, redirigimos a la pagina prinicpal
        return redirect (url_for('index'))
    
@app.route('/dashboard_trabajador')
def dashboard_trabajador():
    if 'user_id' in session:  # Asegurarse de que el usuario esté autenticado
        connection = get_bd()
        cursor = connection.cursor()

        # Consulta para obtener el total de ingresos por día
        query = """
            SELECT DATE(fecha) AS fecha_ingreso, SUM(monto) AS total_dia
            FROM ingresos
            GROUP BY DATE(fecha)
            ORDER BY fecha_ingreso DESC
        """
        cursor.execute(query)
        ingresos = cursor.fetchall()

        print(ingresos)

        
        cursor.close()
        connection.close()

        # Convertir los datos en un formato más manejable para la plantilla
        ingresos_format = [
            {'fecha': ingreso[0], 'total': ingreso[1]} for ingreso in ingresos
        ]

        return render_template('dashboard_trabajador.html', ingresos=ingresos_format)
    else:
        return redirect(url_for('login'))

@app.route('/menu_vehiculos') 
def menu_vehiculos():
    connection = get_bd()
    cursor = connection.cursor()
    cursor.execute("""
                   SELECT v.*, 
               CASE WHEN p.id_vehiculo IS NOT NULL THEN 1 ELSE 0 END AS en_promocion
        FROM vehiculo v
        LEFT JOIN promociones p ON v.id_vehiculo = p.id_vehiculo
        """)
    vehiculos = cursor.fetchall()

    # Convertir los datos a diccionario
    column_names = [column[0] for column in cursor.description]
    vehiculos_dict = [dict(zip(column_names, record)) for record in vehiculos]

    cursor.close()
    connection.close()

    # Pasar los vehículos al template
    return render_template('menu_vehiculos.html', vehiculos=vehiculos_dict)

@app.route('/vehiculo', methods=['POST'])
def addVehiculo():
    # Obtener datos del formulario
    placa = request.form['placa']
    marca = request.form['marca']
    modelo = request.form['modelo']
    fabricacion = request.form['fabricacion']
    color = request.form['color']
    fecha_ultimo_mantenimiento = request.form['fecha_ultimo_mantenimiento']
    kilometraje = request.form['kilometraje']
    precio_por_dia = request.form['precio_por_dia']
    estado = request.form['estado']
    sucursal = request.form['sucursal']

    if placa and marca and modelo and fabricacion and color and fecha_ultimo_mantenimiento and kilometraje and precio_por_dia and estado and sucursal:
        # Conectar a la base de datos
        connection = get_bd()
        cursor = connection.cursor()

        # Insertar el vehículo en la base de datos
        sql = """
            INSERT INTO vehiculo 
            (placa, marca, modelo, fabricacion, color, fecha_ultimo_mantenimiento, kilometraje, precio_por_dia, estado, sucursal) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        data = (placa, marca, modelo, fabricacion, color, fecha_ultimo_mantenimiento, kilometraje, precio_por_dia, estado, sucursal)
        cursor.execute(sql, data)
        connection.commit()

        cursor.close()
        connection.close()

        flash('Cliente registrado correctamente', 'success')
    else:
        flash('Faltan datos, no se pudo registrar el cliente', 'danger')

    return redirect(url_for('menu_vehiculos'))

@app.route('/editar/<int:id_vehiculo>', methods=['POST'])
def editarVehiculo(id_vehiculo):
    # Obtener datos del formulario
    placa = request.form['placa']
    marca = request.form['marca']
    modelo = request.form['modelo']
    fabricacion = request.form['fabricacion']
    color = request.form['color']
    transmision = request.form['transmision']
    nro_asientos = request.form['nro_asientos']
    fecha_ultimo_mantenimiento = request.form['fecha_ultimo_mantenimiento']
    kilometraje = request.form['kilometraje']
    precio_por_dia = request.form['precio_por_dia']
    estado = request.form['estado']
    sucursal = request.form['sucursal']
    promocion = request.form.get('promocion')

    if placa and marca and modelo and fabricacion and color and transmision and nro_asientos and fecha_ultimo_mantenimiento and kilometraje and precio_por_dia and estado and sucursal:
        # Conectar a la base de datos
        connection = get_bd()
        cursor = connection.cursor()

         # Obtener la URL de la imagen actual del vehículo
        cursor.execute("SELECT imagen FROM vehiculo WHERE id_vehiculo = %s", (id_vehiculo,))
        imagen_url = cursor.fetchone()[0]

        # Actualizar los datos del vehículo
        sql = """
            UPDATE vehiculo 
            SET placa = %s, marca = %s, modelo = %s, fabricacion = %s, color = %s, 
                transmision = %s, nro_asientos = %s, fecha_ultimo_mantenimiento = %s, 
                kilometraje = %s, precio_por_dia = %s, estado = %s, sucursal = %s
            WHERE id_vehiculo = %s
        """
        data = (placa, marca, modelo, fabricacion, color, transmision, nro_asientos, fecha_ultimo_mantenimiento, kilometraje, precio_por_dia, estado, sucursal, id_vehiculo)
        cursor.execute(sql, data)
        connection.commit()
        
        # Verificar si el vehículo ya está en promociones
        cursor.execute("SELECT COUNT(*) FROM promociones WHERE id_vehiculo = %s", (id_vehiculo,))
        en_promocion = cursor.fetchone()[0] > 0

        # Si el checkbox de promoción está marcado y el vehículo no está en promociones, agregarlo
        if promocion and not en_promocion:
            sql_promocion = """
                INSERT INTO promociones (id_vehiculo, placa, marca, modelo, fabricacion, color, transmision, nro_asientos, fecha_ultimo_mantenimiento, kilometraje, precio_por_dia, estado, sucursal, imagen)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            data_promocion = (id_vehiculo, placa, marca, modelo, fabricacion, color, transmision, nro_asientos, fecha_ultimo_mantenimiento, kilometraje, precio_por_dia, estado, sucursal, imagen_url)
            cursor.execute(sql_promocion, data_promocion)
            connection.commit()
        # Si el checkbox de promoción no está marcado y el vehículo está en promociones, eliminarlo
        elif not promocion and en_promocion:
            cursor.execute("DELETE FROM promociones WHERE id_vehiculo = %s", (id_vehiculo,))
            connection.commit()

        cursor.close()
        connection.close()

        flash('Vehículo actualizado correctamente', 'success')
    else:
        flash('Faltan datos, no se pudo actualizar el vehículo', 'danger')

    return redirect(url_for('menu_vehiculos'))

@app.route('/eliminar/<int:id_vehiculo>', methods=['POST'])
def eliminarVehiculo(id_vehiculo):
    # Eliminar el vehículo de la base de datos
    connection = get_bd()
    cursor = connection.cursor()

    sql = "DELETE FROM vehiculo WHERE id_vehiculo = %s"
    cursor.execute(sql, (id_vehiculo,))
    connection.commit()

    cursor.close()
    connection.close()

    flash('Vehículo eliminado correctamente', 'danger')
    return redirect(url_for('menu_vehiculos'))

@app.route('/menu_clientes')
def menu_clientes():
    connection = get_bd()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()    

    # Convertir los datos a diccionario
    column_names = [column[0] for column in cursor.description]
    clientes_dict = [dict(zip(column_names, record)) for record in clientes]
        
    connection.close()
    cursor.close()

    return render_template('menu_clientes.html', clientes=clientes_dict)

@app.route('/cliente', methods=['POST'])
def addCliente():
    nombres = request.form['nombres']
    apellido_paterno = request.form['apellido_paterno']
    apellido_materno = request.form['apellido_materno']
    tipo_documento = request.form['tipo_documento']
    numero_documento = request.form['numero_documento']
    celular = request.form['celular']    
    fecha_nacimiento = request.form['fecha_nacimiento']
    correo_electronico = request.form['correo_electronico']
    contrasena = request.form['contrasena']

    if nombres and apellido_paterno and apellido_materno and tipo_documento and numero_documento and fecha_nacimiento and celular and correo_electronico and contrasena:
        connection = get_bd()
        cursor = connection.cursor()
        sql = """
                INSERT INTO clientes
                (nombres, apellido_paterno, apellido_materno, tipo_documento, numero_documento, celular, fecha_nacimiento, correo_electronico, contrasena) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        data = (nombres, apellido_paterno, apellido_materno, tipo_documento, numero_documento, celular, fecha_nacimiento, correo_electronico, contrasena)
        cursor.execute(sql, data)
        connection.commit()

        cursor.close()
        connection.close()

        flash('Cliente registrado correctamente', 'success')
    else:
        flash('Faltan datos, no se pudo registrar el cliente', 'danger')

    return redirect(url_for('menu_clientes'))

@app.route('/eliminar_cliente/<int:id_cliente>', methods=['POST'])
def eliminarCliente(id_cliente):
    connection = get_bd()
    cursor = connection.cursor()
    
    sql = "DELETE FROM clientes WHERE id_cliente = %s"
    cursor.execute(sql, (id_cliente,))
    connection.commit()
    
    cursor.close()
    connection.close()

    # Mensaje para la eliminación exitosa
    flash('Cliente eliminado', 'danger')

    return redirect(url_for('menu_clientes'))

@app.route('/editar_cliente/<int:id_cliente>', methods=['POST'])
def editarCliente(id_cliente):
    nombres = request.form['nombres']
    apellido_paterno = request.form['apellido_paterno']
    apellido_materno = request.form['apellido_materno']
    tipo_documento = request.form['tipo_documento']
    numero_documento = request.form['numero_documento']
    fecha_nacimiento = request.form['fecha_nacimiento']
    celular = request.form['celular']
    correo_electronico = request.form['correo_electronico']
    contrasena = request.form['contrasena']

    if nombres and apellido_paterno and apellido_materno and tipo_documento and numero_documento and fecha_nacimiento and celular and correo_electronico and contrasena:
        
        connection = get_bd()
        cursor = connection.cursor()
        
        sql = """
        UPDATE clientes SET nombres = %s, apellido_paterno = %s, apellido_materno = %s, tipo_documento = %s, 
                 numero_documento = %s, fecha_nacimiento = %s, celular = %s, correo_electronico = %s, contrasena = %s 
                 WHERE id_cliente = %s
        """
        data = (nombres, apellido_paterno, apellido_materno, tipo_documento, numero_documento, fecha_nacimiento, celular, correo_electronico, contrasena, id_cliente)
        
        cursor.execute(sql, data)
        connection.commit()

        cursor.close()
        connection.close()

        # Mensaje para la edición exitosa
        flash('Cambios guardados', 'success')

    return redirect(url_for('menu_clientes'))

@app.route("/menu_promociones") 
def menu_promociones():
    connection = get_bd()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM promociones")
    promociones = cursor.fetchall()

    # Convertir los datos a diccionario
    column_names = [column[0] for column in cursor.description]
    promociones_dict = [dict(zip(column_names, record)) for record in promociones]

    cursor.close()
    connection.close()

    # Pasar los vehículos al template
    return render_template('menu_promociones.html', promociones=promociones_dict)

@app.route('/editar_promocion/<int:id_promocion>', methods=['POST'])
def editarPromocion(id_promocion):
    # Obtener datos del formulario
    placa = request.form['placa']
    marca = request.form['marca']
    modelo = request.form['modelo']
    fabricacion = request.form['fabricacion']
    color = request.form['color']
    transmision = request.form['transmision']
    nro_asientos = request.form['nro_asientos']
    fecha_ultimo_mantenimiento = request.form['fecha_ultimo_mantenimiento']
    kilometraje = request.form['kilometraje']
    precio_por_dia = request.form['precio_por_dia']
    estado = request.form['estado']
    sucursal = request.form['sucursal']

    if placa and marca and modelo and fabricacion and color and transmision and nro_asientos and fecha_ultimo_mantenimiento and kilometraje and precio_por_dia and estado and sucursal:
        # Conectar a la base de datos
        connection = get_bd()
        cursor = connection.cursor()

        # Actualizar los datos de la promoción
        sql = """
            UPDATE promociones 
            SET placa = %s, marca = %s, modelo = %s, fabricacion = %s, color = %s, 
                transmision = %s, nro_asientos = %s, fecha_ultimo_mantenimiento = %s, 
                kilometraje = %s, precio_por_dia = %s, estado = %s, sucursal = %s
            WHERE id_promocion = %s
        """
        data = (placa, marca, modelo, fabricacion, color, transmision, nro_asientos, fecha_ultimo_mantenimiento, kilometraje, precio_por_dia, estado, sucursal, id_promocion)
        cursor.execute(sql, data)
        connection.commit()

        cursor.close()
        connection.close()

        flash('Promoción actualizada correctamente', 'success')
    else:
        flash('Faltan datos, no se pudo actualizar la promoción', 'danger')

    return redirect(url_for('menu_promociones'))

@app.route('/eliminar_promocion/<int:id_promocion>', methods=['POST'])
def eliminarPromocion(id_promocion):
    # Conectar a la base de datos
    connection = get_bd()
    cursor = connection.cursor()

    # Eliminar la promoción
    sql = "DELETE FROM promociones WHERE id_promocion = %s"
    cursor.execute(sql, (id_promocion,))
    connection.commit()

    cursor.close()
    connection.close()

    flash('Promoción eliminada correctamente', 'success')
    return redirect(url_for('menu_promociones'))

@app.route('/logout')
def logout():
    # Eliminar datos de la sesión
    session.pop('user_id', None)
    session.pop('tipo_usuario', None)
    # Redirigir al usuario a la página de inicio de sesión
    return redirect(url_for('index'))

@app.route('/reserva/<int:vehiculo_id>', methods =['GET','POST'])
def reserva(vehiculo_id):
    connection=get_bd()
    cursor=connection.cursor(DictCursor)
    cursor.execute("SELECT * FROM vehiculo WHERE Id_vehiculo = %s", (vehiculo_id,))
    vehiculo=cursor.fetchone()
    cursor.close()
    connection.close()
    
    costo_total=None
    if request.method == 'POST':
            # Obtener las fechas del formulario
            fecha_inicio = request.form['fecha_inicio']
            fecha_fin = request.form['fecha_fin']
            precio_por_dia = float(vehiculo['precio_por_dia'])

            # Calcular la diferencia de días
            from datetime import datetime
            inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
            diff_days = (fin - inicio).days

            if diff_days > 0:
                costo_total = diff_days * precio_por_dia
            else:
                costo_total = "Fechas inválidas, verifica tu selección."
    
    if 'user_id' in session and vehiculo:  
        user_data = {
                'id': session.get('user_id'),
                'nombre_compl': session.get('nombre_compl'),
                'apellidop':session.get('apellidop'),
                'apellidom':session.get('apellidom'),
                'tipo_doc':session.get('tipo_doc'),
                'num_doc':session.get('num_doc'),
                'direccion':session.get('direccion')
            }
        
        return render_template('reserva.html', vehiculo=vehiculo, user=user_data, costo_total=costo_total)
    else:
        return "Auto no encontrado", 404

@app.route('/pagar', methods=['POST'])
def pagar():
    if 'user_id' in session:
        connection = get_bd()
        cursor = connection.cursor()

        # Obtener datos del formulario y de la sesión
        id_usuario = session['user_id']
        id_vehiculo = request.form['id_vehiculo']
        monto = request.form['monto']

        # Insertar el ingreso en la base de datos
        query = """
            INSERT INTO ingresos (id_usuario, id_vehiculo, monto)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (id_usuario, id_vehiculo, monto))
        connection.commit()

        cursor.close()
        connection.close()

        return redirect (url_for('index'))
    else:
        return "Usuario no autenticado", 403


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)