# Lytecord

A discord clone written in... Python??

![image](https://github.com/blaiyz/Lytecord/assets/139375534/85c49fbc-43e9-4289-8c4b-49e2390c5707)


## How to run

Clone the repo:
```
git clone https://github.com/blaiyz/Lytecord.git
cd Lytecord
```

**Optionally** create a virtual environment:
```
pip install virtualenv
virtualenv venv
source venv/bin/activate
```

Install dependencies:
```
pip install -r requirements.txt
```

### Server
Create a self signed certificate:
```
openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes -keyout server.key -out server.crt -subj "/CN=<YOUR IP>" -addext "subjectAltName=IP:<YOUR IP>"
```


Share the `server.crt` file with the clients.

Open [`src/shared/protocol.py`](./src/shared/protocol.py#L8) and change the HOST global to your need.

Download and install MongoDB and create a database called `Lytecord`, and then run:
```
python -c “from setup_database import create_indexes; create_indexes()”
```

Now start the server with:
```
python -m server
```

### Client (App)
Receive the `server.crt` file from the server host and place it in the root repo directory.

Open [`src/shared/protocol.py`](./src/shared/protocol.py#L8) and change the HOST global to the server host's address.

Now start the app:
```
python -m app
```

## Used Icons

<details>
  <summary><strong>Click here to see the list</strong></summary>
<br>
<table>
  <tr>
    <td><a href="https://www.flaticon.com/free-icons/paper-clip" title="paper clip icons">Paper clip icons created by GOFOX - Flaticon</a></td>
  </tr>
  <tr>
    <td><a href="https://www.flaticon.com/free-icons/community" title="community icons">Community icons created by KP Arts - Flaticon</a></td>
  </tr>
  <tr>
    <td><a href="https://www.flaticon.com/free-icons/image-placeholder" title="image placeholder icons">Image placeholder icons created by Graphics Plazza - Flaticon</a></td>
  </tr>
  <tr>
    <td><a href="https://www.flaticon.com/free-icons/error" title="error icons">Error icons created by Gregor Cresnar - Flaticon</a></td>
  </tr>
  <tr>
    <td><a href="https://www.flaticon.com/free-icons/join" title="join icons">Join icons created by Fathema Khanom - Flaticon</a></td>
  </tr>
  <tr>
    <td><a href="https://www.flaticon.com/free-icons/add" title="add icons">Add icons created by Freepik - Flaticon</a></td>
  </tr>
  <tr>
    <td><a href="https://www.flaticon.com/free-icons/hashtag" title="hashtag icons">Hashtag icons created by Mayor Icons - Flaticon</a></td>
  </tr>
</table>
</details>
