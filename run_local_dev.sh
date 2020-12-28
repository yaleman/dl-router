#export FLASK_APP=main.py
#python -m flask run --host 0.0.0.0 --port 5000



APP_PATH=$(pwd)/app
USERDATA_PATH=$(pwd)/userdata.csv
MIRRORS_CONF_PATH=$(pwd)/mirrors.yaml
LISTEN_PORT=5000
CONTAINER_NAME=redirect
DETACH=false

if [ ! -d "${APP_PATH}" ]; then
    echo "Unable to find app dir at ${APP_PATH}, quitting"
    exit 1
fi

if [ ! -f "${USERDATA_PATH}" ]; then
    echo "Unable to find userdata.csv at ${USERDATA_PATH}, quitting"
    exit 1
fi

if [ ! -f "${MIRRORS_CONF_PATH}" ]; then
    echo "Unable to find mirrors.yaml at ${MIRRORS_CONF_PATH}, quitting"
    exit 1
fi

##FIXME CHANGE CONFIG MAP TO YAML WHEN DONE

sudo docker run \
    --rm \
    $([[ ${DETACH} == "true" ]] && echo "-d") \
    -v "${APP_PATH}:/app" \
    -v "${USERDATA_PATH}:/app/userdata.csv" \
    -v "${MIRRORS_CONF_PATH}:/app/mirrors.yaml" \
    -p "${LISTEN_PORT}:80" \
    --name "${CONTAINER_NAME}" \
    quay.io/lanefu/nginx-uwsgi-flask:arm64
