# To build:
export BROKER_USER=broker
export repo_name=menanteau
export TAG=latest
export image=deep_broker
repo_name=registry.gitlab.com/antares-at-ncsa/scimma-alerts-integration-demo
docker build -t $repo_name/$image:$TAG \
       --build-arg BROKER_USER --rm=true .
