# stop if any error occurs
set -e

echo "Iniciando todos los inits"

echo "init Formato F931"
python manage.py init_formato_f931

echo "init Orden Registro"
python manage.py init_orden_registro

echo "init tabla Tipo de Registro"
python manage.py init_tipo_registro

echo "FIN init"
