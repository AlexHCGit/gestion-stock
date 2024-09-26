from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'some_secret_key'

# Conectar a la base de datos
def conectar_db():
    return sqlite3.connect('inventario.db')

# Crear las tablas si no existen
def crear_tablas():
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hospital (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            ubicacion TEXT
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS maquina (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            hospital_id INTEGER,
            FOREIGN KEY(hospital_id) REFERENCES hospital(id)
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS repuesto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            stock INTEGER DEFAULT 0,
            maquina_id INTEGER,
            FOREIGN KEY(maquina_id) REFERENCES maquina(id)
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimiento_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repuesto_id INTEGER,
            cantidad INTEGER,
            tipo TEXT,
            fecha TEXT,
            FOREIGN KEY(repuesto_id) REFERENCES repuesto(id)
        );
    ''')
    conexion.commit()
    conexion.close()

# Página de inicio
@app.route('/')
def index():
    return render_template('index.html')

# Página para agregar hospital
@app.route('/agregar_hospital', methods=['GET', 'POST'])
def agregar_hospital():
    if request.method == 'POST':
        nombre = request.form['nombre']
        ubicacion = request.form['ubicacion']
        if nombre and ubicacion:
            conexion = conectar_db()
            cursor = conexion.cursor()
            cursor.execute('INSERT INTO hospital (nombre, ubicacion) VALUES (?, ?)', (nombre, ubicacion))
            conexion.commit()
            conexion.close()
            flash('Hospital agregado correctamente')
            return redirect(url_for('agregar_hospital'))
        else:
            flash('Todos los campos son obligatorios')
    return render_template('agregar_hospital.html')

# Página para ver hospitales
@app.route('/ver_hospitales')
def ver_hospitales():
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute('SELECT nombre, ubicacion FROM hospital')
    hospitales = cursor.fetchall()
    conexion.close()
    return render_template('ver_hospitales.html', hospitales=hospitales)

# Página para agregar una máquina
@app.route('/agregar_maquina', methods=['GET', 'POST'])
def agregar_maquina():
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute('SELECT id, nombre FROM hospital')
    hospitales = cursor.fetchall()
    conexion.close()

    if request.method == 'POST':
        nombre_maquina = request.form['nombre_maquina']
        hospital_id = request.form['hospital_id']
        if nombre_maquina and hospital_id:
            conexion = conectar_db()
            cursor = conexion.cursor()
            cursor.execute('INSERT INTO maquina (nombre, hospital_id) VALUES (?, ?)', (nombre_maquina, hospital_id))
            conexion.commit()
            conexion.close()
            flash('Máquina agregada correctamente')
            return redirect(url_for('agregar_maquina'))
        else:
            flash('Todos los campos son obligatorios')
    
    return render_template('agregar_maquina.html', hospitales=hospitales)

#Página para ver máquinas por hospital
@app.route('/ver_maquinas')
def ver_maquinas():
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute('SELECT id, nombre FROM hospital')
    hospitales = cursor.fetchall()
    conexion.close()
    return render_template('ver_maquinas.html', hospitales = hospitales)

@app.route('/ver_maquinas/<int:hospital_id>')
def ver_maquinas_por_hospital(hospital_id):
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute('SELECT nombre FROM maquina WHERE hospital_id = ?', (hospital_id,))
    maquinas = cursor.fetchall()
    conexion.close()
    return render_template('maquinas_por_hospital.html', maquinas = maquinas)

# Página para agregar repuestos
# Agregar repuesto
@app.route('/agregar_repuesto', methods=['GET', 'POST'])
def agregar_repuesto():
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute('SELECT id, nombre FROM maquina')
    maquinas = cursor.fetchall()
    conexion.close()

    if request.method == 'POST':
        nombre_repuesto = request.form['nombre_repuesto']
        descripcion = request.form['descripcion']
        stock_inicial = request.form['stock_inicial']
        maquina_id = request.form['maquina_id']

        if nombre_repuesto and descripcion and stock_inicial and maquina_id:
            conexion = conectar_db()
            cursor = conexion.cursor()
            cursor.execute('INSERT INTO repuesto (nombre, descripcion, stock, maquina_id) VALUES (?, ?, ?, ?)',
                           (nombre_repuesto, descripcion, stock_inicial, maquina_id))
            conexion.commit()
            conexion.close()
            flash('Repuesto agregado correctamente')
            return redirect(url_for('agregar_repuesto'))
        else:
            flash('Todos los campos son obligatorios')

    return render_template('agregar_repuesto.html', maquinas=maquinas)


# Página para buscar repuesto
@app.route('/buscar_repuesto', methods=['GET', 'POST'])
def buscar_repuesto():
    if request.method == 'POST':
        nombre_repuesto = request.form['nombre_repuesto']
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute('''
            SELECT repuesto.nombre, maquina.nombre, hospital.nombre, repuesto.stock, repuesto.descripcion
            FROM repuesto
            JOIN maquina ON repuesto.maquina_id = maquina.id
            JOIN hospital ON maquina.hospital_id = hospital.id
            WHERE repuesto.nombre LIKE ?
        ''', ('%' + nombre_repuesto + '%',))
        resultados = cursor.fetchall()
        conexion.close()

        if resultados:
            return render_template('resultados_repuesto.html', resultados=resultados)
        else:
            flash('No se encontró el repuesto')
            return redirect(url_for('buscar_repuesto'))

    return render_template('buscar_repuesto.html')

# Ver stock de repuestos por máquina
@app.route('/ver_stock', methods=['GET', 'POST'])
def ver_stock():
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute('SELECT id, nombre FROM maquina')
    maquinas = cursor.fetchall()
    conexion.close()

    if request.method == 'POST':
        maquina_id = request.form['maquina_id']
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute('SELECT nombre, stock FROM repuesto WHERE maquina_id = ?', (maquina_id,))
        repuestos = cursor.fetchall()
        conexion.close()
        return render_template('stock_repuestos.html', repuestos = repuestos)
                           
    return render_template('ver_stock.html', maquinas = maquinas)

# Página registro entrada de datos
@app.route('/registrar_entrada', methods=['GET', 'POST'])
def registrar_entrada():
    conexion = conectar_db()
    cursor = conexion.cursor()

    # Obtener la lista de hospitales
    cursor.execute('SELECT id, nombre FROM hospital')
    hospitales = cursor.fetchall()

    # Inicializar variables
    maquinas = []
    repuestos = []

    if request.method == 'POST':
        # Obtener el hospital seleccionado
        hospital_id = request.form.get('hospital_id')

        # Si el hospital ha sido seleccionado, obtenemos las máquinas asociadas
        if hospital_id:
            cursor.execute('SELECT id, nombre FROM maquina WHERE hospital_id = ?', (hospital_id,))
            maquinas = cursor.fetchall()

        # Si la máquina ha sido seleccionada, obtenemos los repuestos asociados
        maquina_id = request.form.get('maquina_id')
        if maquina_id:
            cursor.execute('SELECT id, nombre FROM repuesto WHERE maquina_id = ?', (maquina_id,))
            repuestos = cursor.fetchall()

        # Si se ha seleccionado repuesto y cantidad, registramos la entrada
        repuesto_id = request.form.get('repuesto_id')
        cantidad = request.form.get('cantidad')
        if repuesto_id and cantidad:
            cursor.execute('UPDATE repuesto SET stock = stock + ? WHERE id = ?', (cantidad, repuesto_id))
            cursor.execute('INSERT INTO movimiento_stock (repuesto_id, cantidad, tipo, fecha) VALUES (?, ?, "entrada", date("now"))',
                           (repuesto_id, cantidad))
            conexion.commit()
            flash('Entrada de stock registrada correctamente')
            return redirect(url_for('registrar_entrada'))

    conexion.close()
    return render_template('registrar_entrada.html', hospitales=hospitales, maquinas=maquinas, repuestos=repuestos)


# Registrar salida de stock
@app.route('/registrar_salida', methods=['GET', 'POST'])
def registrar_salida():
    conexion = conectar_db()
    cursor = conexion.cursor()

    # Obtener la lista de hospitales
    cursor.execute('SELECT id, nombre FROM hospital')
    hospitales = cursor.fetchall()

    # Inicializar variables
    maquinas = []
    repuestos = []

    if request.method == 'POST':
        # Obtener el hospital seleccionado
        hospital_id = request.form.get('hospital_id')

        # Si el hospital ha sido seleccionado, obtenemos las máquinas asociadas
        if hospital_id:
            cursor.execute('SELECT id, nombre FROM maquina WHERE hospital_id = ?', (hospital_id,))
            maquinas = cursor.fetchall()

        # Si la máquina ha sido seleccionada, obtenemos los repuestos asociados
        maquina_id = request.form.get('maquina_id')
        if maquina_id:
            cursor.execute('SELECT id, nombre FROM repuesto WHERE maquina_id = ?', (maquina_id,))
            repuestos = cursor.fetchall()

        # Si se ha seleccionado repuesto y cantidad, registramos la salida
        repuesto_id = request.form.get('repuesto_id')
        cantidad = request.form.get('cantidad')
        if repuesto_id and cantidad:
            cursor.execute('UPDATE repuesto SET stock = stock - ? WHERE id = ?', (cantidad, repuesto_id))
            cursor.execute('INSERT INTO movimiento_stock (repuesto_id, cantidad, tipo, fecha) VALUES (?, ?, "salida", date("now"))',
                           (repuesto_id, cantidad))
            conexion.commit()
            flash('Salida de stock registrada correctamente')
            return redirect(url_for('registrar_salida'))

    conexion.close()
    return render_template('registrar_salida.html', hospitales=hospitales, maquinas=maquinas, repuestos=repuestos)

        

if __name__ == '__main__':
    crear_tablas()
    app.run(debug=True)
