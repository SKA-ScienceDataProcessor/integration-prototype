# Utilities for the Flask Master Interface Service (Flask API)
** These utilities are out of date with respect to the Flask API
and may no longer work as advertised. **


## On a developer's computer
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
* sdp_root: for reading the root of the flask interface;
* sdp_send: for sending a state change request to the flask interface;
* mkstate: for creating the JSON for pasting into the web browser;
* mkstate1: functionally identical to mkstate;
* flask: interactive menu-driven interface to the flask interface 
for reading and changing the state.

`sdp_state` needs no parameters; `mkstate` (and also `mkstate1`) 
takes an option -0 for off; -1 for on; -d for disable and -s for standby.
With no options it assumes on.
`sdp_send` uses the same options as `mkstate`.
`flask` needs no arguments and should be intuitive.

`mkstate` and `mkstate1` both produce a formatted JSON string to be used
(using cut and paste) in the web interface. `mkstate` uses the `jq`
utility to format the JSON string; `mkstate1` uses the bash builtin printf
instead.

All but two of these require the utility `curl` which I believe is part 
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
## On the P-cubed or other Swarm-enabled computer
On your own machine it is possible to use localhost to access the flask and
Redis services.
With P-cubed you need to use the IP address set up in the DOCKER_HOST 
environment variable, which is set in the `env.sh` file, which can be found
in the same directory as the PEM certificates required to run docker on the
server.
The content of the variable will look something 
like `tcp://10.60.253.14:2375`.
The author assumes the user already has something like this in 
their profile to enable
OpenStack and Docker on the P-cubed server:
```bash
[[ -f $HOME/p3-openrc.shV3 ]] && . $HOME/p3-openrc.shV3
[[ -f $HOME/swarm-creds/env.sh ]] && . $HOME/swarm-creds/env.sh
```
Adding the following lines will strip out the prefix `tcp//` and suffix `:port`
from the DOCKER_HOST variable and assign the IP address to the 
REDIS_HOST environment variable (obvioulsy the profile will 
need to be resourced to allow the change to come into effect):
```bash
REDIS_HOST=${DOCKER_HOST%:*}
REDIS_HOST=${REDIS_HOST#*//}
export REDIS_HOST
```
Similarly the scripts in this directory will use the DOCKER_HOST variable
if it exists to create the URL required for the flask API.
If it doesn't exist the localhost will be used instead.

At the writing of this README the P-cubed server does not have the jq
package installed; it will be necessary to download it from the 
official website to use these utilities. 
The following command will download it to the file `jq`, which can 
then be moved into the user's path:
```bash
wget -O jq https://github.com/stedolan/jq/releases/download/jq-1.5/jq-linux64
```
