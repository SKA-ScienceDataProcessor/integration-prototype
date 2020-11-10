# Pipenv usage

- <https://pipenv.readthedocs.io/en/latest/basics/>
- <https://realpython.com/pipenv-guide/>

```bash
pipenv shell
```

To generate a `requirements.txt` file:

```bash
pipenv lock -r [--dev] > requirements.txt
```

## Interaction with `setup.py`

From <https://realpython.com/pipenv-guide/>

> Here is a recommended workflow for when you are using a `setup.py` as a way
> to distribute your package:
>
> - `setup.py` install_requires keyword should include whatever the package
>   "minimally needs to run correctly".
> - `Pipfile` represents the concrete requirements for your package
> - Pull the minimally required dependencies from `setup.py` by installing
>   your package using `pipenv`:
>   - Use `pipenv install -e .`
>   - That will result in a line in your `pipfile` that looks something
>     like `"e1839a8" = {path = ".", editable = true}`.
> - `Pipfile.lock` contains details for a reproducible environment generated
>   from `pipenv lock`
