# To build:
export BROKER_USER=broker
export repo_name=menanteau
export TAG=latest
export image=deep_broker
docker build -t $repo_name/$image:$TAG \
       --build-arg BROKER_USER --rm=true .
