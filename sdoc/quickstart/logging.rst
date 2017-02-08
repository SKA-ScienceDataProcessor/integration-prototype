Customising logging
===================

SIP logging output can be customised by editing the ``default_logging.json``
file found in the ``sip/etc`` folder.

The syntax for this logging file follows the standard Python logging dictionary
configuration schema described in the `standard python documentation
<https://docs.python.org/3.5/library/logging.config.html#dictionary-schema-details>`_,
and summarised in the sections below.

The logging configuration file is a JSON file with the following top level
keys, which are described in the sections below:

- loggers
- formatters
- handlers
- filters

loggers
-------
This dictionary specifies the configuration of Python logger instances.
For SIP, this should consist of a dictionary entry where the key is
``sip.logging_aggregator``, the logging instance used by the SIP logging server,
and the value is a dictionary describing how to configure the logger.

The following keys can be used to configure the logger:

- ``level`` The level of the logger.
- ``handlers`` A list of ids of handlers for this logger.
- ``filters`` A list of ids of the filters for this logger.

handlers
--------
This is a dictionary of handlers where the key is the handler id and the value
is a dictionary describing how to configure the handler instance.

In the default logging SIP configuration, two handlers are defined. One for
messages to stdout and one for logging to a file. These both use basic handler
classes defined in the Python logging library.

The handlers configuration dictionary respects the following default keys:

- ``class`` (required) The name of the handler class.
- ``level`` The level of the handler.
- ``formatter`` The id of the formatter for this handler.
- ``filters`` A list of ids of filters for this handler.

If using a custom handler, other keys may be specified and these are passed
to the constructor of the handler.

formatters
----------
This is used to specify the formatting of log messages. This is a dictionary
of formatters where the key is the formatter id and the value is a dictionary
describing how to configure the formatter.

The dictionary respects the following default keys:

- ``format``
- ``datefmt``

These are both used to specify the formatter instance,
see: `<https://docs.python.org/3.5/library/logging.html#logging.Formatter>`_.

When defining the ``format`` value, in addition to default Python logging
LogRecord attributes (
`<https://docs.python.org/3.5/library/logging.html#logrecord-attributes>`_),
SIP Log records also contain the following attributes which can be used:

- ``%(hostname)s`` The hostname where the logging call was issued.
- ``%(username)s`` The username which issued the logging call.
- ``%(time)s`` The UTC time of the logging call in ISO 8601 format.
- ``%(origin)s`` The origin of the logging call in the form
  `module.function:lineno`.


filters
-------
Used to describe which log messages are displayed by either a handler or logger
instance. The value is a dictionary where the key is the filter id and each
value is a dictionary describing ow to configure the filter instance.

SIP defines two filters, one for filtering logging records by their origin
and one for filtering by the message contents.

OriginFilter
^^^^^^^^^^^^
The origin filter allows log records to be enabled or disabled according to the
module, function and line number from which the logging call was made.
The filter is configured by specifying a list of log record origin strings
as the value of the ``origin`` key of the filter configuration.

Origin filter strings should take the form `module.function:lineno` and this
will be used to match against the log record origin field to determine if it
should be displayed. It should be noted that matching is performed with a
`starts-with` match, so if the filter is specified as `module` all log records
from the specified module will be matched or if the filter is specified as
`module.function` all records from the specified function inside the specified
module will be matched.

Once matched the filter will choose to display or reject log records based on
the value of the ``exclude`` key. If this is true is not specified,
records that match with the filter will be hidden. If it is false, only records
that match the filter will be shown.


MessageFilter
^^^^^^^^^^^^^
The message filter allows log records to be enabled or disabled according to
the matching of a specified sub-string within their message field.
The filter is configured by specifying a list of log message sub-strings as the
value of the ``messages`` key of the filter configuration.

Message filter sub-strings are matched against the message field of the log
record by looking for the sub-string within the message. If a match is found
the record will be displayed or not based on the value of the ``exclude`` key.
If true, or not specified, records that match will be hidden. If it is false,
only records that match will be shown.







