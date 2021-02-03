#!/bin/bash

# $1 - semver string
# $2 - level to incr {patch,minor,major} - patch by default
function incr_semver() { 
    IFS='.' read -ra ver <<< "$1"
    [[ "${#ver[@]}" -ne 3 ]] && echo "Invalid semver string" && return 1
    [[ "$#" -eq 1 ]] && level='patch' || level=$2

    patch=${ver[2]}
    minor=${ver[1]}
    major=${ver[0]}

    case $level in
        patch)
            patch=$((patch+1))
        ;;
        minor)
            patch=0
            minor=$((minor+1))
        ;;
        major)
            patch=0
            minor=0
            major=$((major+1))
        ;;
        *)
            echo "Invalid level passed"
            return 2
    esac
    echo "$major.$minor.$patch"
}

for CHART in charts/*/Chart.yaml; do
    echo $CHART
    app_version=$(grep -oP '(?<=^appVersion:\s)[^:]*' $CHART)
    app_version_string=$(grep -oP '(^appVersion:\s)[^:]*' $CHART)
    chart_version=$(grep -oP '(?<=^version:\s)[^:]*' $CHART)
    chart_version_string=$(grep -oP '(^version:\s)[^:]*' $CHART)
    echo "Current app_version of $CHART: $app_version"
    last_version=$(grep -oP '(?<=^appVersion:\s)[^:]*' $CHART | sed -nr 's/^[^0-9]*(([0-9]+\.)*[0-9]+).*/\1/p')
    echo "Clean version: $last_version"
    increased_version=$(incr_semver $last_version 'minor')
    echo "Increased to next minor: $increased_version"
    sed -i "s/$app_version_string/appVersion:\ $increased_version-dev/" $CHART 
    sed -i "s/$chart_version_string/version:\ $increased_version-dev/" $CHART 
    echo
done