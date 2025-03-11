# cotc-server
Flask web app that displays metrics from different sources (device metrics, weather data).

### To Run
First, navigate to the root directory of this project (`cotc-server`).

If you have `uv` installed, you can use:
```sh
uv venv
source ./.venv/bin/activate
uv pip install -r pyproject.toml
```

If you do not have `uv` installed, you can use:
```sh
py -m venv .venv
source ./.venv/bin/activate
pip install -r pyproject.toml
```

> [!NOTE]  
> It will probably be .\\.venv\Scripts\activate (rather than `source ./.venv/bin/activate`) if you are on Windows.


You should then be able to run `app.py` using 
```sh
uv run -m app
```

or 

```sh
py -m app
```

> [!NOTE]
> This project goes hand-in-hand w/ [this project](https://github.com/darragh0/cotc-client).
