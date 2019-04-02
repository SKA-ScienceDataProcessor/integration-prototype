# SIP Master Interface Service (REST variant)

## Description

This should be functionally similar to the Tango master but uses a Green
Unicorn/Flask web interface instead of a Tango interface.

Point a web browser to <http://localhost:5000> and see the JSON structure
below:

```json
{
  "message": "Welcome to the SIP Master Controller (flask variant)",
  "_links": {
    "items": [
      {
        "Link": "Health",
        "href": "http://localhost:5000/health"
      },
      {
        "Link": "Version",
        "href": "http://localhost:5000/version"
      },
      {
        "Link": "Allowed target states",
        "href": "http://localhost:5000/allowed_target_sdp_states"
      },
      {
        "Link": "SDP state",
        "href": "http://localhost:5000/state"
      },
      {
        "Link": "SDP target state",
        "href": "http://localhost:5000/state/target"
      },
      {
        "Link": "SDP current state",
        "href": "http://localhost:5000/state/current"
      },
      {
        "Link": "Scheduling Block Instances",
        "href": "http://localhost:5000/scheduling_block_instances"
      },
      {
        "Link": "Processing Blocks",
        "href": "http://localhost:5000/processing_blocks"
      }
    ]
  }
}
```

You are able to select any of the subsequent pages by selecting the appropriate
link. For instance, selecting the health link(<http://localhost:5000/health>)
you will get a new JSON structure:

```json
{
  "service": "TangoControl:FlaskMaster:1.2.0",
  "uptime": "514887.17s"
}
```

Some of these links only allow you to view data; others allow you
to change it. For instance, the link <http://localhost:5000/state/target>
will give the current state and allowed target state.

```json
{
    "current_state": "standby",
    "target_state": "unknown",
    "allowed_target_states": [
        "off",
        "on"
    ],
    "last_updated": "2019-03-08T11:49:18.218949"
}
```

It will also provide a text area to allow you to send a request for a new
target state, such as:

```json
{
  "value": "off"
}
```

If it succeeds you will get back:

```json
{
    "message": "Target state successfully updated to off"
}
```

or an error message if it fails.

Currently only the target SDP state can be modified.

## DB Activities

* Read current SDP state
* Read target state
* Set target (commanded) SDP state
