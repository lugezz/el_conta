# Entorno de desarrollo

## Aplicacion local

```bash
# Descargar repositorio
git clone git@github.com:lugezz/el_conta.git

# Crear entorno virtual
python3 -m venv env

# Activamos el entorno virtual
source env/bin/activate

# Instalar requerimientos
pip install -r requirements.txt

```

## Base de datos

Crea el archivo `el_conta/local_settings.py` y actualiza `DATABASES`
segun tu entorno y el motor que quieres usar (por ejemplo PostgreSQL o MySQL)

```
# Requerimientos segun motor de base de datos

pip install -r requirements.mysql.txt
# o
pip install -r requirements.psql.txt
```

### PostgreSQL

Crear usuario y base de datos por terminal


sudo -u postgres psql\
**postgres=#** CREATE DATABASE myproject;\
**postgres=#** CREATE USER my_user WITH PASSWORD 'my_password';\
**postgres=#** ALTER ROLE my_user SET client_encoding TO 'utf8';\
**postgres=#** ALTER ROLE my_user SET default_transaction_isolation TO 'read committed';\
**postgres=#** ALTER ROLE my_user SET timezone TO 'UTC';\
**postgres=#** GRANT ALL PRIVILEGES ON DATABASE el_conta_db TO my_user;
**postgres=#** ```\q```\


En local_settings.py

```python
MY_DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'el_conta_db',
        'USER': 'my_user',
        'PASSWORD': 'my_password',
        'HOST': 'localhost',
        'PORT': '',
    }
}
```

### MySQL

Creación Base de Datos MySQL
```
mysql -u root -p
CREATE DATABASE el_conta_db CHARACTER SET utf8;
CREATE USER my_user IDENTIFIED BY 'my_password';
GRANT ALL PRIVILEGES ON el_conta_db.* TO my_user ;
exit
```

En local_settings.py

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'el_conta_db',
        'USER': 'my_user',
        'PASSWORD': 'my_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

## Iniciar entorno local

Aplicar migraciones
```
./manage.py migrate
```
Cargar archivos estáticos

```
./manage.py collectstatic
```

Iniciar la aplicacion

```
./manage.py runserver
```
