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

### Server
Create a self signed certificate:
```
openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes -keyout server.key -out server.crt -subj "/CN=<YOUR IP>" -addext "subjectAltName=IP:<YOUR IP>"
```
> [!NOTE]
> Make sure the `CN` and the `subjectAltName` arguments are the exact ones the clients will use in order to connect to the server.
> i.e. if you want to be accessible across your local network, you must use your IP address in that network (127.0.0.1 will not work).
> Similarly, use your domain name if you want to be accessible globally.

Share the `server.crt` file with the clients.

**IF YOU ARE RUNNING WITHOUT DOCKER:**

Install dependencies:
```
pip install -r requirements.txt
```

Download and install MongoDB and create a database called `Lytecord`, and then run:
```
python -c “from setup_database import create_indexes; create_indexes()”
```

Now start the server with:
```
python -m server
```

**IF YOU ARE RUNNING WITH DOCKER:**

Run
```
docker-compose up -d
```

When you remove the mongodb container, remove the generated `data` directory to avoid problems in the future.

### Client (App)

Install dependencies:
```
pip install -r requirements.txt
```

Receive the `server.crt` file from the server host and place it in the root repo directory.

Open [`src/shared/protocol.py`](./src/shared/protocol.py#L8) and change the HOST global to the server host's address/domain name.

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
