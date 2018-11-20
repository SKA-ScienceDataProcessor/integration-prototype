#!/usr/bin/env bash
RED='\033[0;31m'
NC='\033[0m'
echo -e "${RED}* Registering Device: ska_sip/elt/master${NC}"
./app/register_device.py
echo -e "${RED}* Starting Device Server: sdp_master_ds/1${NC}"
./app/sdp_master_ds.py "1" "-v4"
