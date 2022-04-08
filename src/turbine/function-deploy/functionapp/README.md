## Functions App
This application serves as an interface between `turbine-py` and `funtime`, the Meroxa Functions Runtime

### Requirements 
```pycon
grpcio             1.44.0
grpcio-tools       1.44.0
```

### Troubleshooting

#### Apple Silicon (M1) issues
mach-o file, but is an incompatible architecture (have 'x86_64', need 'arm64e'))

As of April 8, 2022 the default wheel for grpcio and grpcio-tools is not working on M1 processors. In order to use these tools you may have to force pip to build the wheel locally with the following commands

```bash
pip install --no-binary :all: grpcio grpcio-tools --ignore-installed
```