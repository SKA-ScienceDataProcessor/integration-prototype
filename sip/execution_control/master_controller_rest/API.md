# Master Controller Interface

This document describes the interface and resources provided by the SIP Master 
Controller (REST variant) 

### State

An interface to obtain or set the SDP state. The SDP is ....

#### Get the current state

Gets the current SDP state.

**HTTP Request**

`GET http://BASE_URL/state`

**Response**

```JSON
{
    "title": "Current state response",
    "type": "object",
    "properties": {
        "state": {"type": "string"}
    } 
}
```

**Sample Response**

```JSON
{
    "state": "STANDBY"
}
```



### Update the state

Trigger an update to the SDP state

**HTTP Request**

`PUT http://BASE_URL/state`

**Request Body**

```JSON
{
    "title": "State update request",
    "type": "object",
    "properties": {
        "state": {"type": "string"}
    }
}
```

**Response**

```JSON
{
    "title": "State update response",
    "type": "object",
    "properties": {
        "message": {"type": "string"}
    }
}
```

**Sample Response**

```JSON
{
    "message": "Accepted state: INIT"
}
```
