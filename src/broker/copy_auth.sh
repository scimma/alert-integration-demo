#!/bin/bash

set -e

mkdir -p /home/broker/.config/hop
cp /tmp/auth.toml /home/broker/.config/hop/auth.toml
chmod 0600 /home/broker/.config/hop/auth.toml
chown 1006:1003 /home/broker/.config/hop/auth.toml
touch /tmp/hop_auth_ready
