# Contributing to SIP

The following is a set of guidelines for contributing to SIP. These are mostly guidelines, not rules! 
Use your best judgement, and feel free to propose changes to this document in a pull request.

## Pull Request Process

1. Follow all instructions in [the template](PULL_REQUEST_TEMPLATE.md)
1. Follow the [style guides](#Style-guides)
1. After you submit your pull request, verify that all 
   [status checks](https://help.github.com/articles/about-status-checks/) are 
   passing 
 
## Style guides

### Git Commit Messages

* Use the present tense
* Use the imperative mood
* Limit the first line to 72 characters or less
* Reference issues, pull requests, and JIRA tickets liberally after the 
  first line
* When only changing documentation include `[ci skip]` in the commit title
* Consider starting the commit message with an applicable emoji:
    * :art: when improving the format / structure of the code
    * :racehorse: when improving performance
    * :memo: when writing docs
    * :bug: when fixing a bug
    * :fire: when removing code or files
    * :green_heart: when fixing the CI build
    * :which_check_mark: when adding tests
    * :arrow_up: when upgrading dependencies
    * :arrow_down: when downgrading dependencies
    * :shirt: when removing linter warnings
 
### Python Style Guide

* All code should adhere to [PEP 8](https://www.python.org/dev/peps/pep-0008/) 
* All docstrings should adhere to [PEP 257](https://www.python.org/dev/peps/pep-0257/)

This can be checked using the tools:

* https://pypi.org/project/pycodestyle
* https://pypi.org/project/pydocstyle
* https://pypi.org/project/pylint

### Documentation

* Use [Markdown](https://guides.github.com/features/mastering-markdown/) 

### Docker Images

* Images should be tagged using [Semantic Versioning](https://semver.org/).
* The latest release should also be tagged with `:latest`
* Images should following the naming pattern `skasip/<prefix>_<image name>`, 
  where `<image name>` should clearly describe the role of the image and 
  `<prefix>` is one of:
    * `ec` for Execution Control images
    * `tc` for Tango Control images
    * `sp` for Science Pipeline Workflow images
    * `pl` for Platform images     

### Published Python packages

* Should use [Semantic Versioning](https://semver.org/).
* The published package name should be prefixed with `skasip-` so that they 
  can easily be found using [pypi](https://pypi.org). e.g. `pip search skasip`
  or <https://pypi.org/search/?q=skasip>.
      
### Issue and pull request labels

Coming soon!

