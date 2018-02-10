# Processing Controller Interface (REST variant)

This document describes the interface and resources provided by the SIP 
Processing Controller Interface (REST variant) 

This interface exposes the following resources:

* Scheduling block list
* Scheduling block detail
* Processing block list
* Processing block detail 


### Scheduling Block List

An interface to obtain the list of registered Scheduling Blocks.

#### Get the Scheduling Block list

Gets the current list of scheduling blocks .

**HTTP Request**

`GET http://BASE_URL/scheduling-blocks`

**Response**

```JSON
{
    "title": "Current Scheduling block list",
    "type": "object",
    "properties": {
        "last_update": {"type": "string"},
        "scheduling_blocks": {"type": "array"}
    } 
}
```

**Sample Response**

```JSON
{
    "last_update": "",
    "scheduling_blocks": [
        {
            "id": "sb-01",
            "processing_blocks": []
        },
        {
            "id": "sb-02",
            "processing_blocks": []
        }
    ]
}
```



### Add a new Scheduling Block

Add a new Scheduling Block to the list

**HTTP Request**

`POST http://BASE_URL/scheduling-blocks`

**Request Body**

```JSON
{
    "title": "Scheduling block request object",
    "type": "object",
    "properties": {
        "processing_blocks": {"type": "array"}
    }
}
```

**Response**

```JSON
{
    "title": "Scheduling block created response",
    "type": "object",
    "properties": {
        "message": {"type": "string"},
        "id": {"type": "string"},
        "_links": {"type": "object"}
    }
}
```

**Sample Response**

```JSON
TODO!
```
