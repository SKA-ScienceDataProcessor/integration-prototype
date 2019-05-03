# SIP Documentation

This folder contains documentation and technical notes related to SIP code
which we choose to keep in the code repository (rather than on Confluence).

## Building Sphinx documentation

Documentation is build automatically by the CI/CD **(TODO!)** script on pushes
to the Github repository. It can also be build manually using the
following commands (this assumes all dependencies have been installed -
eg. `pipenv shell`!):

Building the HTML documentation is as simple as running the following command
from the `docs/` folder.

```bash
make html
```

This will render HTML documentation into the `docs/build/html` directory. To
view these open `docs/build/html/index.html` in a web browser.

If developing documentation the
[`sphinx-autobuild`](https://github.com/GaretJax/sphinx-autobuild) Python
package can also be very useful. This will rebuild the documentation
automatically every time a change is made and serve it at the address
<http://localhost:8000/>. If using the provided `pipenv`, this tool is already
installed and can be used with the following command, run from the top level
repository directory:

```bash
sphinx-autobuild docs/src docs/build/html
```

### Publishing to [`Read the Docs`](https://readthedocs.org/)

...
