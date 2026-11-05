#!/bin/bash
# Undo deploy-646.sh: an, lovenails, showapp back to 2.99.353 (the 2.99.646 folder is kept for a look).
set -euo pipefail; A=/home/uyurpyzubx0m/app
for s in an lovenails showapp; do ln -sfn ../../releases/2.99.353 "$A/sites/$s/current.new" && mv -T "$A/sites/$s/current.new" "$A/sites/$s/current"; chown -h uyurpyzubx0m:uyurpyzubx0m "$A/sites/$s/current"; echo "$s -> $(readlink "$A/sites/$s/current")"; done
echo ROLLBACK646-OK
