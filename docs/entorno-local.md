# Entorno de desarrollo

## Aplicacion local

```bash
# Descargar repositorio
git clone git@github.com:lugezz/siradig.git

# Crear entorno virtual
python3 -m venv env

# Activamos el entorno virtual
source env/bin/activate

# Instalar requerimientos
pip install -r requirements.txt

```

## Base de datos

Crea el archivo `siradig/local_settings.py` y actualiza `DATABASES`
segun tu entorno y el motor que quieres usar (por ejemplo PostgreSQL o MySQL)

```
# Requerimientos segun motor de base de datos

pip install -r requirements.mysql.txt
# o
pip install -r requirements.psql.txt
```

### PostgreSQL

Crear usuario y base de datos

```
CREATE USER siradig WITH PASSWORD 'siradig';
ALTER ROLE siradig SUPERUSER;
CREATE DATABASE siradig OWNER siradig;
```

En local-settings.py

```python
DATABASES = {
    'default': {
         'ENGINE': 'django.contrib.gis.db.backends.postgis',
         'NAME': 'siradig',
         'USER': 'siradig',
         'PASSWORD': 'siradig',
         'HOST': 'localhost',
         'PORT': 5432
    },
}
```

### MySQL

Creación Base de Datos MySQL
```
mysql -u root -p
CREATE DATABASE siradig CHARACTER SET utf8;
```
En archivo my_db.cnf cambiar usuario y contraseña del usuario de MySQL con privilegios
Ejemplo de archivo my_db.cnf:

```ini
[client]
database = siradig
user = root
password = root
HOST = localhost
PORT = 3306
```

En local-settings.py

```python
BD_CONFIG_PATH = str(BASE_DIR / 'my_db.cnf')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': BD_CONFIG_PATH,
        },
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
