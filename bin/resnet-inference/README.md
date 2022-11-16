#Usage

Build images:

    ./build.sh
    

Build and release:

    ./release.sh


Manually start the docker container:

    docker run -e SET_GPU_MEMORY_LIMIT=false -e MODEL_STORAGE='local' -e IMAGE_STORAGE='request' -e exec_timeout=5m -d resi5/resnet-inference:<tagname>

Get a bash shell inside the running container:
 
    docker exec -it <container_id> /bin/bash

Curl command for testing the function (run within container shell): 

    curl -d "@data.json" -L -X POST http://localhost:8080
