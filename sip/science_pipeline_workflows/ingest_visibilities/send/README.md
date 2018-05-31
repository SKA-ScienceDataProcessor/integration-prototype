# CSP emulator: Visibility sender

## Introduction

CSP emulator to send visibilities in the form of SPEAD streams.

This sender makes use of asyncio and threads to send multiple streams from
same process.

The sender process is configured using a JSON string, whose schema is described
in the accompanying `config_schema.json` file which is in
[JSON schema](http://json-schema.org/) format.

## Quick-start

For running instructions see the `README.md` file in the parent folder.
