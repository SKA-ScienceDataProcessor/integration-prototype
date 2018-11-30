# Contributing to SIP

The following is a set of guidelines for contributing to SIP. These are mostly guidelines, not rules! 
Use your best judgement, and feel free to propose changes to this document in a pull request.


## Branches

* Choose *short* and *descriptive* names
* Identifiers from tickets or issues are also good candidates for branch names.
* Consider prefixing the branch name with `feature/`, `fix/` or `update/` to 
  help identify the role of the branch.
* Delete your branch from the upstream repository after it is merged, unless
  there is a specific reason not to. 


## Commits

* Each commit should be a single *logical change*. Don't make several 
  *logical changes* in one commit.
* Don't split a single *logical change* into several commits.
* Commit *early* and *often*. Small, self-contained commits are easier
  to understand and to revert if something goes wrong!
* Commits should be ordered *logically*. For example, if *commit X* depends on 
  changes in *commit Y* then *commit Y* should come before *commit X*.
  
*Note: While working on your local branch that has not yet been pushed, it's
fine to use commits as temporary snapshots of your work. However, apply all of
the above before pushing it.*  

### Commit Messages

* Use the editor, not the terminal when writing a commit message.
  Committing from the terminal encourages a mindset of having to fit 
  everything into a single line which can result in a non-informative,
  ambiguous message. 
    * ie. Use `git commit` not `git commit -m "..."`   
* Limit the first (summary) line to 72 characters or less
* After the summary should be a blank line followed by a more thorough 
  description. This should also be wrapped at 72 characters or less.
* Reference issues, pull requests, and JIRA tickets liberally after the 
  first line
* When only changing documentation include `[ci skip]` in the commit title
* Consider starting the commit message with an applicable emoji:
    * :art: `:art:` when improving the format / structure of the code
    * :racehorse: `:racehorse:` when improving performance
    * :memo: `:memo:` when writing docs
    * :bug: ``:bug:` when fixing a bug
    * :fire: `:fire:` when removing code or files
    * :green_heart: `:green_heart:` when fixing the CI build
    * :white_check_mark: `:white_check_mark:` when adding tests
    * :arrow_up: `:arrow_up:` when upgrading dependencies
    * :arrow_down: `:arrow_down:` when downgrading dependencies
    * :shirt: `:shirt:` when removing linter warnings


## Merging

* see <https://help.github.com/articles/about-pull-request-merges>

## Pull Request Process

1. Follow all instructions in [the template](PULL_REQUEST_TEMPLATE.md)
1. Follow the [style guides](#Style-guides)
1. After you submit your pull request, verify that all 
   [status checks](https://help.github.com/articles/about-status-checks/) are 
   passing 

 
## Style guides
 
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

TODO

