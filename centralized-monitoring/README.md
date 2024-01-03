# Centralized Model Monitoring (private preview)

## pip installs

```
! pip3 install --upgrade --quiet \
    google-cloud-aiplatform \
    google-cloud-bigquery \
    pandas-gbq \
    'tensorflow_data_validation[visualization]<2'

# Model Monitoring Experimental SDK
! gsutil cp gs://cmm-public-data/sdk/google_cloud_aiplatform-1.36.dev20231025+centralized.model.monitoring-py2.py3-none-any.whl .
! pip install --quiet google_cloud_aiplatform-1.36.dev20231025+centralized.model.monitoring-py2.py3-none-any.whl
```