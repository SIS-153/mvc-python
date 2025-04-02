# app/app/controllers/auth_controller.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.usuario import Usuario
from app import db
from app.forms.auth_forms import LoginForm, RegistroForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario and usuario.check_password(form.password.data):
            login_user(usuario, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        flash('Email o contraseña incorrectos')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente')
    return redirect(url_for('index'))

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    form = RegistroForm()
    if form.validate_on_submit():
        # Verificar si el email ya existe
        usuario_existente = Usuario.query.filter_by(email=form.email.data).first()
        if usuario_existente:
            flash('Este email ya está registrado')
            return render_template('auth/registro.html', form=form)
            
        usuario = Usuario(
            nombre=form.nombre.data,
            apellido=form.apellido.data,
            email=form.email.data,
            telefono=form.telefono.data,
            direccion=form.direccion.data
        )
        usuario.set_password(form.password.data)
        
        db.session.add(usuario)
        db.session.commit()
        
        flash('Te has registrado correctamente. Ya puedes iniciar sesión.')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/registro.html', form=form)