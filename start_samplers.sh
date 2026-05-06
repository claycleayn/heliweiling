#!/bin/bash
N=5
for i in $(seq 1 $N); do
    mkdir -p "./data/sampler_$i"
    
    docker run -d \
        --name "sampler_$i" \
        -v "$(pwd)/data/sampler_$i:/data" \
        random-sensor \
        /usr/local/bin/random_sensor 50
    
    docker run -d \
        --name "emitter_$i" \
        -v "$(pwd)/data/sampler_$i:/data" \
        -e DEVICE_ID="sampler_$i" \
        sensor-emitter
    
    echo "启动采样机 $i"
done