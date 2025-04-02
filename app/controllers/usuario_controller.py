# Archivo: app/controllers/usuario_controller.py
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from app.models.usuario import Usuario
from app import db
from werkzeug.security import generate_password_hash

usuario_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

@usuario_bp.route('/')
def listar_usuarios():
    usuarios = Usuario.query.all()
    return render_template('usuarios/lista.html', usuarios=usuarios)

@usuario_bp.route('/nuevo', methods=['GET', 'POST'])
def crear_usuario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        password = request.form['password']
        es_admin = 'es_admin' in request.form
        
        # Verificar si el usuario ya existe
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            flash('El email ya está registrado.')
            return render_template('usuarios/crear.html')
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            email=email,
            telefono=telefono,
            direccion=direccion,
            es_admin=es_admin
        )
        nuevo_usuario.set_password(password)
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        flash('Usuario creado exitosamente.')
        return redirect(url_for('usuarios.listar_usuarios'))
    
    return render_template('usuarios/crear.html')

@usuario_bp.route('/<int:id>')
def ver_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    return render_template('usuarios/detalle.html', usuario=usuario)

@usuario_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
def editar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    
    if request.method == 'POST':
        usuario.nombre = request.form['nombre']
        usuario.apellido = request.form['apellido']
        usuario.telefono = request.form['telefono']
        usuario.direccion = request.form['direccion']
        
        # Solo cambiar el email si es diferente
        nuevo_email = request.form['email']
        if nuevo_email != usuario.email:
            usuario_existente = Usuario.query.filter_by(email=nuevo_email).first()
            if usuario_existente:
                flash('El email ya está registrado por otro usuario.')
                return render_template('usuarios/editar.html', usuario=usuario)
            usuario.email = nuevo_email
        
        # Cambiar contraseña solo si se proporciona
        if request.form['password']:
            usuario.set_password(request.form['password'])
        
        usuario.es_admin = 'es_admin' in request.form
        
        db.session.commit()
        flash('Usuario actualizado exitosamente.')
        return redirect(url_for('usuarios.listar_usuarios'))
    
    return render_template('usuarios/editar.html', usuario=usuario)

@usuario_bp.route('/<int:id>/eliminar', methods=['POST'])
def eliminar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuario eliminado exitosamente.')
    return redirect(url_for('usuarios.listar_usuarios'))