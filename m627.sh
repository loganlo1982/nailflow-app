#!/bin/bash
# LAMWEB 627 – chay test tien tren MySQL TEST rieng. CHAT dat bien moi truong (KHONG ghi mat khau vao file):
#   export NF_TEST_DB_NAME=nf_test626 NF_TEST_DB_USER=nf_test626 NF_TEST_DB_HOST=127.0.0.1
#   read -rs NF_TEST_DB_PASS; export NF_TEST_DB_PASS
#   bash m627.sh <ban app da cai 627 (vd ban sao release)>   2>&1 | tee ket-qua-m627.txt
set -u; K=$(cd "$(dirname "$0")" && pwd)
[ $# -eq 1 ] || { echo "usage: $0 <app folder>"; exit 2; }
command -v php >/dev/null || { echo "khong co php"; exit 2; }
php -m | grep -qi pdo_mysql || { echo "PHP thieu pdo_mysql"; exit 2; }
exec python3 "$K/m627.py" "$1"
