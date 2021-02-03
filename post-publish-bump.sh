#!/bin/bash


for CHART in charts/*/Chart.yaml; do
    echo $CHART
    APPVERSION=$(grep -oP '(?<=^appVersion:\s)[^:]*' $CHART)
    echo $APPVERSION
done