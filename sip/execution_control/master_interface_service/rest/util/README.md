# Utilties for the Master Interface Service

One can access the Master Interface Service by pointing a web server 
at http://localhost:5000/state and typing in a JSON string.
But there are some disadvantages to this including:

* Having to type the same thing over and over;
* Prone to mistyping;
* Pulling up a web server just to see the status.

It is possible to use command-line utilities like _wget_ or _curl_ 
to fetch the state over; but again you have to type, in this case a 
URL, and the result is not necessarily pretty:

```
$ curl -s http://localhost:5000/state 
{"state": "ON"}$ 
```
As you can see the state is returned in a minimised JSON format; 
and the command prompt is unceremoniously dumped on top, as there 
is no linefeed at the end of the JSON.
The following almost identical invocation uses the utility `jq` to 
reformat the JSON, making it readable:
```
$ curl -s http://localhost:5000/state | jq .
{
  "state": "ON"
}
$
```
To make things simpler for the user 
the following bash shell-scripts have been made available here:

* sdp_state: for reading the current state as above;
* mkstate: for creating the JSON for pasting into the web browser;
* mkstate1: functionally identical to mkstate;
* flask: interactive menu-driven interface to the flask interface 
for reading and changing the state.

`sdp_state` needs no parameters; `mkstate` (and also `mkstate1`) 
takes an option -0 for off; -1 for on; -d for disable and -s for standby.
With no options it assumes on.
`flask` needs no arguments and should be intuitive.

`mkstate` and `mkstate1` both produce a formatted JSON string to be used
(using cut and paste) in the web interface. `mkstate` uses the `jq`
utility to format the JSON string; `mkstate1` uses the bash builtin printf
instead.

Two out of these require the utility `curl` which I believe is part 
of the OSX toolkit. 
For Linux systems it may be necessary to install with (for 
example on Debian-based systems such as Ubuntu):
```
sudo apt install curl
```
All of them (apart from `mkstate1`) require `jq`, a tool described 
by its creators as "a sed for json files".
This may be installed on Debian systems with
```
sudo apt install jq
```
and OSX systems with
```
brew install jq
```
