#!/bin/bash

if [[ -d charts ]]; then 
  ls -la 
else
  echo "No charts directory found" 
fi

# # install helm
# curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3
# chmod 700 get_helm.sh
# ./get_helm.sh

# create clean repo cache dir
[[ -d "chart-repo-cache" ]] && rm -rf chart-repo-cache
mkdir -p ./chart-repo-cache

# add SKA Helm Repository
helm repo add skatelescope $HELM_HOST/repository/helm-chart --repository-cache ./chart-repo-cache
helm repo list
helm repo update
helm search repo skatelescope
helm search repo skatelescope >> ./chart-repo-cache/before

# Package charts
[ -z "$CHARTS_TO_PUBLISH" ] && export CHARTS_TO_PUBLISH=$(cd charts; ls -d */)
NEW_CHART_COUNT=0
for chart in $CHARTS_TO_PUBLISH; do
  echo "######## Packaging $chart #########"
  helm package charts/"$chart" --dependency-update --destination ./chart-repo-cache
  echo "######## Status $? ##"
  NEW_CHART_COUNT=$((NEW_CHART_COUNT+1))
done

# ls -la ./chart-repo-cache
# echo "cat chart-repo-cache/skatelescope-index.yaml"
# cat ./chart-repo-cache/skatelescope-index.yaml

# check for pre-existing files
for file in $(cd chart-repo-cache; ls *.tgz); do
  echo "Checking if $file is already in index:"
  cat ./chart-repo-cache/skatelescope-index.yaml | grep "$file" && rm ./chart-repo-cache/$file && NEW_CHART_COUNT=$((NEW_CHART_COUNT - 1)) || echo "Not found in index 👍";
done

# exit script if no charts are to be uploaded
echo Found $NEW_CHART_COUNT charts ready to add to the SKA repository.
(( $NEW_CHART_COUNT > 0 ))

# rebuild index
helm repo index ./chart-repo-cache --merge ./chart-repo-cache/skatelescope-index.yaml

for file in ./chart-repo-cache/*.tgz; do
  echo "######### UPLOADING ${file##*/}";
  curl -v -u $HELM_USERNAME:$HELM_PASSWORD --upload-file ${file} $HELM_HOST/repository/helm-chart/${file##*/};
done
# Nexus index.yaml updates the index file somehow - not all helm repos do that. TODO: figure out how.
# curl -v -u $HELM_USERNAME:$HELM_PASSWORD --upload-file ./chart-repo-cache/index.yaml $HELM_HOST/repository/helm-chart/index.yaml;

sleep 2

helm repo update
helm search repo skatelescope >> ./chart-repo-cache/after
helm search repo skatelescope

echo "This publishing step brought about the following changes:"
diff ./chart-repo-cache/before ./chart-repo-cache/after --color

rm -rf ./chart-repo-cache
