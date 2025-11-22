# MPC-HC integration for Remote Two and 3

Using [uc-integration-api](https://github.com/aitatoi/integration-python-library)

The driver lets configure your MPC-HC instances. A media player and a remote entity are exposed to the core.

Note : this release requires remote firmware `>= 1.7.10`

### Supported attributes
- To be completed


### Supported commands for Media Player entity
- To be completed


## Installation

- First [go to the release section](https://github.com/albaintor/integration-mpchc/releases) and download the `xxx_aarch64-xxx.tar.gz` file
- On the Web configurator of your remote, go to the `Integrations` tab, click on `Add new` and select `Install custom`
- Select the downloaded file in first step and wait for the upload to finish
- A new integration will appear in the list : click on it and start setup 
- MPC-HC must be running for setup
- Type in the IP of hostname of the device running MPC-HC
- Change the port if necessary or let the default value


### Hint for saving battery life

To save battery life, the integration will stop reconnecting if MPC-HC is not running.
But if any MPC-HC command is sent (cursor pad, turn on, play/pause...), a reconnection will be automatically triggered.


### Backup or restore configuration

The integration lets backup or restore the devices configuration (in JSON format).
To use this functionality, select the "Backup or restore" option in the setup flow, then you will have a text field which will be empty if no devices are configured. 
- Backup : just save the content of the text field in a file for later restore and abort the setup flow (clicking next will apply this configuration)
- Restore : just replace the content by the previously saved configuration and click on next to apply it. Beware while using this functionality : the expected format should be respected and could change in the future.
If the format is not recognized, the import will be aborted and existing configuration will remain unchanged.


## Installation as external integration

- Requires Python 3.11
- Under a virtual environment : the driver has to be run in host mode and not bridge mode, otherwise the turn on function won't work (a magic packet has to be sent through network and it won't reach it under bridge mode)
- Your MPC-HC instance has to be started in order to run the setup flow and process commands.
- Install required libraries:  
  (using a [virtual environment](https://docs.python.org/3/library/venv.html) is highly recommended)

```shell
pip3 install -r requirements.txt
```

For running a separate integration driver on your network for Remote Two, the configuration in file
[driver.json](driver.json) needs to be changed:

- Set `driver_id` to a unique value, `mpchc_driver` is already used for the embedded driver in the firmware.
- Change `name` to easily identify the driver for discovery & setup with Remote Two/3 or the web-configurator.
- Optionally add a `"port": 8090` field for the WebSocket server listening port.
    - Default port: `9090`
    - Also overrideable with environment variable `UC_INTEGRATION_HTTP_PORT`

### Custom installation

```shell
python3 src/driver.py
```

See
available [environment variables](https://github.com/unfoldedcircle/integration-python-library#environment-variables)
in the Python integration library to control certain runtime features like listening interface and configuration
directory.

## Build self-contained binary for Remote Two/3

After some tests, turns out python stuff on embedded is a nightmare. So we're better off creating a single binary file
that has everything in it.

To do that, we need to compile it on the target architecture as `pyinstaller` does not support cross compilation.

### x86-64 Linux

On x86-64 Linux we need Qemu to emulate the aarch64 target platform:

```bash
sudo apt install qemu binfmt-support qemu-user-static
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
```

Run pyinstaller:

```shell
docker run --rm --name builder \
    --platform=aarch64 \
    --user=$(id -u):$(id -g) \
    -v "$PWD":/workspace \
    docker.io/unfoldedcircle/r2-pyinstaller:3.11.6  \
    bash -c \
      "python -m pip install -r requirements.txt && \
      pyinstaller --clean --onefile --name driver src/driver.py"
```

### aarch64 Linux / Mac

On an aarch64 host platform, the build image can be run directly (and much faster):

```shell
docker run --rm --name builder \
    --user=$(id -u):$(id -g) \
    -v "$PWD":/workspace \
    docker.io/unfoldedcircle/r2-pyinstaller:3.11.6  \
    bash -c \
      "python -m pip install -r requirements.txt && \
      pyinstaller --clean --onefile --name driver src/driver.py"
```

## Docker Setup (x86-64 & ARM64)

For easy installation on x86-64 and ARM64 systems using Docker:

### Quick Start

```bash
# Clone repository
git clone https://github.com/albaintor/integration-mpchc.git
cd integration-mpchc

# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

### Using Makefile (recommended)

```bash
# Build and start
make start

# View logs  
make logs

# Stop
make down

# Restart
make restart
```

### Using Pre-built Docker Images

```bash
# Pull and run from Docker Hub
docker run -d \
  --name mpchc-integration \
  --network host \
  -v $(pwd)/config:/app/config \
  -e UC_INTEGRATION_HTTP_PORT=9090 \
  docker.io/your-username/mpchc-integration:latest
```

### Manual Docker Commands

```bash
# Build image locally
docker build -t mpchc-integration .

# Run container
docker run -d \
  --name mpchc-integration \
  --network host \
  -v $(pwd)/config:/app/config \
  -e UC_INTEGRATION_HTTP_PORT=9090 \
  mpchc-integration
```

### Configuration

- Integration runs on port `9090` (configurable via `UC_INTEGRATION_HTTP_PORT`)
- Configuration data is stored in `./config` directory
- `network_mode: host` is required for network discovery and magic packets
- Supports both x86-64 and ARM64 architectures

### Access

After startup, the integration is available at `http://localhost:9090` and can be configured in Remote Two/Three.

### Available Docker Tags

- `latest` - Latest development build from main branch
- `v1.x.x` - Specific version releases
- `main` - Latest commit from main branch

### Docker Hub

Pre-built images are available on Docker Hub with multi-architecture support (x86-64 and ARM64).

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the
[tags and releases in this repository](https://github.com/albaintor/integration-mpchc/releases).

## Changelog

The major changes found in each new release are listed in the [changelog](CHANGELOG.md)
and under the GitHub [releases](https://github.com/albaintor/integration-mpchc/releases).

## Contributions

Please read our [contribution guidelines](CONTRIBUTING.md) before opening a pull request.

## License

This project is licensed under the [**Mozilla Public License 2.0**](https://choosealicense.com/licenses/mpl-2.0/).
See the [LICENSE](LICENSE) file for details.


