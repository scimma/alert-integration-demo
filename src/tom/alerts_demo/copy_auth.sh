#!/bin/bash

set -e

cp /tmp/auth.toml /home/worker/.config/hop/auth.toml
chmod 0600 /home/worker/.config/hop/auth.toml
chown 1000:1000 /home/worker/.config/hop/auth.toml
touch /tmp/hop_auth_ready
