#!/bin/bash

TARGET_PATH=./data
DOWNLOAD_PATH=./download

mkdir $TARGET_PATH
mkdir $DOWNLOAD_PATH
cd $DOWNLOAD_PATH

urls=(
    https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-04-10/comm_use_subset.tar.gz
    https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-04-10/noncomm_use_subset.tar.gz
    https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-04-10/custom_license.tar.gz
    https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-04-10/biorxiv_medrxiv.tar.gz
    https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-04-10/metadata.csv
    https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/antiviral_with_properties.sdf.gz
    https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/2020-04-10/cord19_specter_embeddings_2020-04-10.tar.gz
)

for i in "${urls[@]}"; do
    wget -c "$i"
done

for f in *.tar.gz; do
    tar -v -xzf $f -C ../$TARGET_PATH
done
