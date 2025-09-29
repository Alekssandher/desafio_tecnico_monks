echo "Configurando MySQL para permitir LOAD DATA LOCAL INFILE..."

mysql -u root -p"$MYSQL_ROOT_PASSWORD" <<-EOSQL
    SET GLOBAL local_infile = 1;
    FLUSH PRIVILEGES;
EOSQL

echo "MySQL configurado "