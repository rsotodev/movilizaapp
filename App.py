import os
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
import pymysql

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

def get_bd():
        connection=pymysql.connect(
            host='sql3.freesqldatabase.com', 
            user='sql3752687',          
            password='DBZgJDwsLM', 
            database='sql3752687',
            port=3306           
        )
        return connection

@app.route("/") 
def index():
        return render_template("index.html")

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
    return render_template("vehiculos.html", vehiculo=vehiculo, marcas=marcas, colores=colores,transmisiones=transmisiones,nro_asientoss=nro_asientoss)

@app.route("/Login",methods=["GET", "POST"]) 
def login():
        if request.method == "POST":
            username = request.form['username']
            password = request.form['password']
            tipo_usuario = request.form['tipo_usuario']

            # Conectar a la base de datos
            connection = get_bd()
            cur = connection.cursor()

            if tipo_usuario == "trabajador":
                # Consultar en la base de datos para el empleado
                cur.execute("SELECT * FROM empleados WHERE usuario = %s AND contrasena = %s", (username, password))
            else:
                # Consultar en la base de datos para el usuario común
                cur.execute("SELECT * FROM clientes WHERE correo_electronico = %s AND contrasena = %s", (username, password))
            
            user = cur.fetchone()
            cur.close()
            connection.close()

            if user:
                # Guardar información de usuario en sesión
                session['user_id'] = user[0]
                session['tipo_usuario'] = tipo_usuario
                return redirect(url_for('dashboard'))
            else:
                return "Usuario o contraseña incorrectos"

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
        return render_template('index.html')
    
@app.route('/dashboard_trabajador')
def dashboard_trabajador():
    return render_template('dashboard_trabajador.html')

@app.route('/menu_vehiculos') 
def menu_vehiculos():
    connection = get_bd()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM vehiculo")
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

        flash('Vehículo registrado correctamente', 'success')
    else:
        flash('Faltan datos, no se pudo registrar el vehículo', 'danger')

    return redirect(url_for('dashboard_trabajador'))

@app.route('/editar/<int:id_vehiculo>', methods=['POST'])
def editarVehiculo(id_vehiculo):
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

        # Actualizar los datos del vehículo
        sql = """
            UPDATE vehiculo 
            SET placa = %s, marca = %s, modelo = %s, fabricacion = %s, color = %s, 
                fecha_ultimo_mantenimiento = %s, kilometraje = %s, precio_por_dia = %s, 
                estado = %s, sucursal = %s 
            WHERE id_vehiculo = %s
        """
        data = (placa, marca, modelo, fabricacion, color, fecha_ultimo_mantenimiento, kilometraje, precio_por_dia, estado, sucursal, id_vehiculo)
        cursor.execute(sql, data)
        connection.commit()

        cursor.close()
        connection.close()

        flash('Vehículo actualizado correctamente', 'success')
    else:
        flash('Faltan datos, no se pudo actualizar el vehículo', 'danger')

    return redirect(url_for('dashboard_trabajador'))

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
    return redirect(url_for('dashboard_trabajador'))

@app.route('/clientes')
def menu_clientes():
    connection = get_bd()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()

    # Convertir los datos a diccionario
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in clientes:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()

    return render_template('menu_clientes.html', data=insertObject)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)