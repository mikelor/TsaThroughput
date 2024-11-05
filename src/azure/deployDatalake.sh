# $1 - subscriptionName
# $2 - projectName
# $3 - projectEnvironment [dev, qa, prod]
az account set -s $1
az group create -l westus2 -g $2-$3-grp
az deployment group create -g $2-$3-grp  \
  --template-file datalake.json \
  --parameters "{\"pProjectName\": {\"value\": \"$2\"}, \"pEnvironment\": {\"value\": \"$3\"} }"