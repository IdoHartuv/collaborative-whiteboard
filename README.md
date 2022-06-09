# Collaborative Whiteboard
This is my project for Cyber Bagrut.

## Installation
Clone the repo and install its dependencies.

```sh
git clone https://github.com/IdoHartuv/collaborative-whiteboard

cd collaborative-whiteboard

pip install -r requirements.txt
```

## Run
Run server: 
- `--local / -L` (optional): Bind the server to the localhost address. Set to LAN address by default.
```sh
python server.py
```
Run clients:
- `--name <name> / -N <name>` (optional): Give a title to the client's window
- `--local / -L` (optional): Connect the client to the localhost address. Set to LAN address by default.
```sh
python client.py --name/-N <name> --local/-L
```

