#!/bin/bash

VERSION=`git describe --abbrev=1 --tags`
NUM_VER=${VERSION:1}
DEB_UPLOAD_KEY=~/.ssh/private-deb-repo-key

cp $DEB_UPLOAD_KEY .
docker build --build-arg VERSION="$NUM_VER" .
rm private-deb-repo-key
