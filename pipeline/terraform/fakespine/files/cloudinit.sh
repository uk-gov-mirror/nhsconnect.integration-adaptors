  #!/bin/bash
# vim: set syntax=sh tabstop=2 softtabstop=2 shiftwidth=2 expandtab smarttab :

# -u          :: Fail on unbounded variable usage
# -o pipefail :: Report failures that occur elsewhere than just the last command in a pipe
# set -uo pipefail

# Just for logging. Because rsyslog is not running before userdata.
log_file='/tmp/bootstrap.log';

function log() {
  echo -e "$(date) ${1}" \
    | tee -a "${log_file}";
}

function error() {
  echo -e "$(date) ERROR: ${1}" \
    | tee -a "${log_file}";
  exit 1;
};

export aws="$(which aws || echo '/usr/bin/aws')";
export curl="$(which curl || echo '/usr/bin/curl')";

# log "installing EPEL"
# yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
# yum-config-manager --enable epel

log "Installing docker, git, ssh"

yum makecache
yum install -y docker git ssh

log "Installing docker compose"
curl -L "https://github.com/docker/compose/releases/download/1.25.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

service docker start

log "Cloning the NHS repo"

mkdir -p /opt/NHS
cd /opt/NHS
git clone https://github.com/nhsconnect/integration-adaptors.git
cd integration-adaptors
git fetch
git checkout feature/NIAD-132-fake-spine-vnp-deploy

log "Building the image"
BUILD_TAG=foo
docker build -t local/fake-spine:${BUILD_TAG} ./integration-tests/fake_spine/Dockerfile .

log "Starting the image"
./integration-tests/setup_component_test_env.sh
. ./component-test-source.sh
. /var/variables-source.sh
BUILD_TAG=foo docker-compose -f docker-compose.yml f docker-compose.ec2.override.yml up -d fakespine

log "Wait 20s"
wait 20s

log "Show the logs of started container"
C_ID=`docker ps -n 1 --format '{{.ID}}'`
docker logs ${C_ID}


