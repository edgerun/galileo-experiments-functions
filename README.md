# Galileo Experiments Functions

Build
=====

To support multiple architectures, we rely on the `faas-cli` only to scaffold the build directory
and then start our own container build and publish process.

Functions are not deployed via `faas-cli` but are intended to be used with the accompanying [galileo-experiments](https://github.com/edgerun/galileo-experiments) project.

Therefore, there are build and release scripts for each function in this repository located under `bin/`.

## Build for local developing
If you want to simply build a container for local testing, run:
```bash
    ./bin/<function>/build.sh amd64
```

You can specify the target architecture via parameter, which defaults to `amd64`.
Other available architectures are: `arm64v8` & `arm32v7`.

The final image will be tagged as follows: `edgerun/<function>:<commit-hash>-<arch>` 

## Build and release

If you want to build the function for all architectures, run:

    ./bin/<function>/release.sh <repository> <version>

You have to specify two arguments: the repository name, to which the containers are pushed, and the version.

The manifest will be tagged as follows: `<repository>/<function>:<version>`.
And will include images for all architectures (i.e., `amd64`, `arm64v8` & `arm32v7`).