docker run --rm -it -v "$(pwd)":/container/src mtranse /bin/bash -c "cd /container/src/ && ./run_ISE_MTransE.sh"


# on Windows
#docker run --rm -it -v "%cd%":/container/src mtranse /bin/bash -c "cd /container/src/ && ./run_ISE_MTransE.sh"