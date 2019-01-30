#!/usr/bin/env bash

docker build -f Dockerfile -t roll-one-for-me:dev
docker build -f development.Dockerfile -t roll-one-for-me:env

for repo in purelyapplied us.gcr.io/roll-one-for-me/rofm-images ; do
  for tag in dev env $@ ; do
    docker tag roll-one-for-me:${tag} ${repo}/roll-one-for-me:${tag}
    docker push ${repo}/roll-one-for-me:${tag}
  done
done
