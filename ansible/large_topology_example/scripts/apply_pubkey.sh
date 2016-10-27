#!/bin/bash

source /pkg/bin/ztp_helper.sh

apply_linux_pubkey() {

  cat /home/vagrant/$1 >> /home/vagrant/.ssh/authorized_keys
}

apply_xr_pubkey() {
  cp /home/vagrant/$1 /disk0:/$1
  xrcmd "show ipcrypto key import authentication rsa $1"
}


apply_linux_pubkey "id_rsa.pub"
apply_xr_pubkey "id_rsa_pub.b64"
