# Running Locally with Docker

Set the required `LIBRARYLITE_VERSION` environment variable (you can use any version you like, e.g. `1.0.5`):

#### Linux/macOS

````bash
export LIBRARYLITE_VERSION=1.0.5
````

#### Windows PowerShell

````powershell
$env:LIBRARYLITE_VERSION="1.0.5"
````

Start the containers:

````bash
docker-compose up --build
````

The app will be available at: <http://localhost:8000>.

**Note:** `LIBRARYLITE_VERSION` must be set, otherwise Docker Compose will fail.
