import matplotlib.pyplot as plt
import os, io, base64 
from flask import Flask, render_template, request, session, redirect, url_for, flash
from pymysql.cursors import DictCursor
from datetime import datetime
import pymysql

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

def get_bd():
        connection=pymysql.connect(
            host='sql10.freesqldatabase.com', 
            user='sql10760754',          
            password='dGEnawEkQF', 
            database='sql10760754',
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
        return redirect(url_for('dashboard_trabajador'))
    else:
        # Si es un usuario común, redirigimos a la pagina prinicpal
        return redirect (url_for('index'))
    
@app.route('/dashboard_trabajador', methods=['GET', 'POST'])
def dashboard_trabajador():
    if 'user_id' not in session:  # Verificar si el usuario está autenticado
        return redirect(url_for('login'))

    connection = get_bd()
    cursor = connection.cursor()

    # Obtener las fechas del formulario (si se enviaron)
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')

    # Consulta SQL para obtener ingresos con filtro de fechas
    if fecha_inicio and fecha_fin:
        query_ingresos = """
            SELECT DATE(fecha) AS fecha_ingreso, SUM(monto) AS total_dia
            FROM ingresos
            WHERE fecha BETWEEN %s AND %s
            GROUP BY DATE(fecha)
            ORDER BY fecha_ingreso DESC
        """
        cursor.execute(query_ingresos, (fecha_inicio, fecha_fin))
    else:
        # Si no se seleccionaron fechas, traer todos los ingresos
        query_ingresos = """
            SELECT DATE(fecha) AS fecha_ingreso, SUM(monto) AS total_dia
            FROM ingresos
            GROUP BY DATE(fecha)
            ORDER BY fecha_ingreso DESC
        """
        cursor.execute(query_ingresos)
    
    ingresos = cursor.fetchall()       

    # Convertir los ingresos en un formato manejable para la plantilla
    ingresos_format = [{'fecha': ingreso[0], 'total': ingreso[1]} for ingreso in ingresos]

    # 📌 **Consulta SQL para obtener penalizaciones**
    query_penalizaciones = """
        SELECT p.id, a.id AS id_alquiler, p.monto, p.motivo 
        FROM penalizaciones p
        INNER JOIN alquileres a ON p.id_alquiler = a.id
        ORDER BY p.id DESC
    """
    cursor.execute(query_penalizaciones)
    penalizaciones = cursor.fetchall()

    # Convertir penalizaciones a diccionario para la plantilla
    penalizaciones_format = [{'id': p[0], 'id_alquiler': p[1], 'monto': p[2], 'motivo': p[3]} for p in penalizaciones]

    cursor.close()
    connection.close()

    return render_template(
        'dashboard_trabajador.html',
        ingresos=ingresos_format,
        penalizaciones=penalizaciones_format
    )


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
            
         # Manejar la lógica de devolución
        fecha_devolucion = request.form.get('fecha_devolucion')
        estado = request.form.get('estado')
        if fecha_devolucion and estado:
            query = """
                INSERT INTO devoluciones (id_alquiler, fecha_devolucion, estado)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (id_vehiculo, fecha_devolucion, estado))
            connection.commit()
            # Actualizar el estado del alquiler a 'finalizado'
            update_query = """
                UPDATE alquileres
                SET estado = 'Disponible'
                WHERE id = %s
            """
            cursor.execute(update_query, (id_vehiculo,))
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

@app.route('/reserva/<int:vehiculo_id>', methods=['GET', 'POST'])
def reserva(vehiculo_id):
    connection = get_bd()
    cursor = connection.cursor(DictCursor)

    # Obtener datos del vehículo
    cursor.execute("SELECT * FROM vehiculo WHERE Id_vehiculo = %s", (vehiculo_id,))
    vehiculo = cursor.fetchone()

    if not vehiculo:
        cursor.close()
        connection.close()
        return "Auto no encontrado", 404

    costo_total = None  # Inicializar el costo total

    if request.method == 'POST' and 'calcular_costo' in request.form:
        try:
            # Obtener las fechas del formulario
            fecha_inicio = request.form['fecha_inicio']
            fecha_fin = request.form['fecha_fin']
            precio_por_dia = float(vehiculo['precio_por_dia'])

            print(f"FECHA INICIO: {fecha_inicio}, FECHA FIN: {fecha_fin}, PRECIO POR DÍA: {precio_por_dia}")  # <-- DEPURACIÓN

            # Calcular la diferencia de días
            from datetime import datetime
            inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
            diff_days = (fin - inicio).days

            if diff_days > 0:
                costo_total = diff_days * precio_por_dia
                print(f"COSTO TOTAL CALCULADO: {costo_total}")  # <-- DEPURACIÓN
            else:
                flash("Las fechas ingresadas no son válidas.", "danger")
                return redirect(url_for('reserva', vehiculo_id=vehiculo_id))

        except Exception as e:
            flash(f"Error al calcular el costo: {e}", "danger")
            print(f"ERROR: {e}")  # <-- DEPURACIÓN

    # Obtener datos del usuario
    user_data = {
        'id': session.get('user_id', ''),
        'nombre_compl': session.get('nombre_compl', 'Usuario no identificado'),
        'apellidop': session.get('apellidop', ''),
        'apellidom': session.get('apellidom', ''),
        'tipo_doc': session.get('tipo_doc', ''),
        'num_doc': session.get('num_doc', ''),
        'direccion': session.get('direccion', '')
    }

    cursor.close()
    connection.close()

    print(f"ENVIANDO A PLANTILLA: {costo_total}")  # <-- DEPURACIÓN

    return render_template('reserva.html', vehiculo=vehiculo, user=user_data, costo_total=costo_total)


@app.route('/pagar', methods=['POST'])
def pagar():
    if 'user_id' not in session:
        return "Usuario no autenticado", 403

    connection = get_bd()
    cursor = connection.cursor()

    try:
        # Obtener datos del formulario y de la sesión
        id_usuario = session['user_id']
        id_vehiculo = request.form['id_vehiculo']
        monto = request.form['monto']
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']

        # Insertar el ingreso en la base de datos
        query_ingreso = """
            INSERT INTO ingresos (id_usuario, id_vehiculo, monto, fecha)
            VALUES (%s, %s, %s, NOW())
        """
        cursor.execute(query_ingreso, (id_usuario, id_vehiculo, monto))

        # Verificar si el vehículo existe antes del UPDATE
        cursor.execute("SELECT * FROM vehiculo WHERE Id_vehiculo = %s", (id_vehiculo,))
        vehiculo = cursor.fetchone()
        
        if vehiculo:
            # Insertar el alquiler en la base de datos (corregido `id_cliente`)
            query_alquiler = """
                INSERT INTO alquileres (id_cliente, Id_vehiculo, fecha_inicio, fecha_fin, estado)
                VALUES (%s, %s, %s, %s, 'activo')
            """
            cursor.execute(query_alquiler, (id_usuario, id_vehiculo, fecha_inicio, fecha_fin))

            # Actualizar el estado del vehículo a "Alquilado"
            query_update = """
                UPDATE vehiculo
                SET estado = 'Alquilado'
                WHERE Id_vehiculo = %s
            """
            cursor.execute(query_update, (id_vehiculo,))
            
            connection.commit()
        else:
            connection.rollback()
            return "ERROR: Vehículo no encontrado, no se pudo actualizar el estado.", 400

    except Exception as e:
        connection.rollback()
        print("Error en la base de datos:", e)
        return f"Error: {e}", 500

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('index'))    

@app.route('/menu_alquileres', methods=['GET', 'POST'])
def menu_alquileres():
    connection = get_bd()
    cursor = connection.cursor(DictCursor)

    # **Procesar acción de eliminar alquiler**
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'eliminar':  # Eliminar alquiler
            alquiler_id = request.form['alquiler_id']
            sql = "DELETE FROM alquileres WHERE id = %s"
            cursor.execute(sql, (alquiler_id,))
            connection.commit()

    # **Obtener filtros desde el request**
    sucursal = request.args.get('sucursal', '')
    tipo_cliente = request.args.get('tipo_cliente', '')
    tipo_vehiculo = request.args.get('tipo_vehiculo', '')
    estado = request.args.get('estado', '')

    # **Consulta para obtener alquileres con filtros**
    query = """
        SELECT a.id AS id_alquiler, 
               c.nombres AS cliente, 
               c.tipo AS tipo_cliente, 
               v.placa, 
               v.marca, 
               v.modelo, 
               v.tipo AS tipo_vehiculo, 
               v.sucursal, 
               a.fecha_inicio, 
               a.fecha_fin, 
               a.fecha_devolucion, 
               COALESCE(p.monto, 0) AS penalizacion, 
               a.estado
        FROM alquileres a
        JOIN vehiculo v ON a.Id_vehiculo = v.Id_vehiculo
        JOIN clientes c ON a.id_cliente = c.id_cliente
        LEFT JOIN penalizaciones p ON a.id = p.id_alquiler
        WHERE 1=1
    """

    params = []

    if sucursal:
        query += " AND v.sucursal = %s"
        params.append(sucursal)

    if tipo_cliente:
        query += " AND c.tipo = %s"
        params.append(tipo_cliente)

    if tipo_vehiculo:
        query += " AND v.tipo = %s"
        params.append(tipo_vehiculo)

    if estado:
        query += " AND a.estado = %s"
        params.append(estado)

    cursor.execute(query, tuple(params))
    alquileres = cursor.fetchall()

    # **Obtener valores únicos para los filtros**
    cursor.execute("SELECT DISTINCT sucursal FROM vehiculo WHERE sucursal IS NOT NULL")
    sucursales = [row['sucursal'] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT tipo FROM clientes WHERE tipo IS NOT NULL")
    tipos_clientes = [row['tipo'] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT tipo FROM vehiculo WHERE tipo IS NOT NULL")
    tipos_vehiculos = [row['tipo'] for row in cursor.fetchall()]

    cursor.close()
    connection.close()

    return render_template(
        'menu_alquileres.html',
        alquileres=alquileres,
        sucursales=sucursales,
        tipos_clientes=tipos_clientes,
        tipos_vehiculos=tipos_vehiculos
    )


@app.route('/marcar_devuelto/<int:id>', methods=['POST'])
def marcar_devuelto(id):
    connection = get_bd()
    cursor = connection.cursor()

    try:
        # Obtener la fecha de devolución esperada y el ID del vehículo
        cursor.execute("SELECT fecha_fin, Id_vehiculo FROM alquileres WHERE id = %s", (id,))
        alquiler = cursor.fetchone()

        if not alquiler:
            flash("Error: Alquiler no encontrado.", "danger")
            return redirect(url_for('menu_alquileres'))

        fecha_fin = alquiler[0]  # Fecha límite de devolución
        id_vehiculo = alquiler[1]  # ID del vehículo alquilado
        fecha_actual = datetime.now().date()  # Fecha actual corregida

        # Verificar si hay retraso y calcular penalización
        dias_retraso = 0
        penalizacion = 0
        if fecha_actual > fecha_fin:
            dias_retraso = (fecha_actual - fecha_fin).days
            penalizacion = dias_retraso * 25  # Penalización de 25 por día de retraso

        # Marcar el alquiler como "Finalizado" y guardar la fecha real de devolución
        cursor.execute("UPDATE alquileres SET estado = 'finalizado', fecha_devolucion = %s WHERE id = %s", (fecha_actual, id))

        # Registrar la penalización si hay retraso
        if penalizacion > 0:
            cursor.execute(
                "INSERT INTO penalizaciones (id_alquiler, monto, motivo) VALUES (%s, %s, 'Retraso en devolución')",
                (id, penalizacion)
            )

        # Cambiar el estado del vehículo a "Disponible"
        cursor.execute("UPDATE vehiculo SET estado = 'Disponible' WHERE Id_vehiculo = %s", (id_vehiculo,))

        connection.commit()

        # Mensajes flash dependiendo del retraso
        if dias_retraso > 0:
            flash(
                f"El alquiler fue marcado como devuelto con un retraso de {dias_retraso} días. Penalización aplicada: S/. {penalizacion}.",
                "warning"
            )
        else:
            flash("El alquiler fue marcado como devuelto sin retrasos.", "success")

    except Exception as e:
        connection.rollback()
        flash(f"Error al procesar la solicitud: {e}", "danger")
        return redirect(url_for('menu_alquileres'))

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('menu_alquileres'))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)