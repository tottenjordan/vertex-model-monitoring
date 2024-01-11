# imports
import os
import sys
import time
import random
import string
import logging
import argparse
import warnings
from typing import List
from google.cloud import bigquery

def monitoring_test(args):
    
    # public available
    TARGET = "churned"
    GROUND_TRUTH="churned"
    DATASET_BQ_URI="bq://mco-mm.bqmlga4.train"
    print(f"DATASET_BQ_URI[5:] {DATASET_BQ_URI[5:]}")
    
    # config these
    REGION = args.region
    PROJECT_ID = args.project_id
    BQ_LOGGING_TABLE = args.bq_logging_table_uri
    EXISTING_ENDPOINT_NAME = f'projects/{args.project_number}/locations/{args.region}/endpoints/{args.endpoint_id}'

    print(EXISTING_ENDPOINT_NAME)

    # =============================================
    # imports
    # =============================================
    # google cloud SDKs
    from google.cloud import bigquery
    import google.cloud.aiplatform as aiplatform

    # # client SDKs
    bq_client = bigquery.Client(project=PROJECT_ID)
    aiplatform.init(project=PROJECT_ID, location=REGION)

    # use existing endpoint
    _endpoint = aiplatform.Endpoint(EXISTING_ENDPOINT_NAME)
    
    # traffic function
    ITER_COUNT = args.iterations      # interations
    MAX_ROWS   = args.max_rows        # instances per interation
    INTERVAL   = args.max_rows/4      # print interval 
    SLEEP_TIME = args.sleep_time      # pause between iters
    MULTIPLIER = args.multiplier
    

    SUBSET_COUNTRY_LIST = [
        # 'Australia', 'Philippines', 
        'South Africa', 'Vietnam'
    ]
    print(SUBSET_COUNTRY_LIST)
    
    ### start
    start_time = time.time()
    total_requests = 0
    multiplier     = args.multiplier
    
    print("starting loop...")
    print(args)

    for i in range(1, args.count):

        start_time_iter = time.time()
        print(f"Start iteration : {i} of {args.count}")
        print(f"multiplier      : {args.multiplier}")

        _table = bigquery.TableReference.from_string(DATASET_BQ_URI[5:])
        rows = bq_client.list_rows(_table, max_results=args.max_rows)
    

        instances = []

        for row in rows:
            instance = {}
            for key, value in row.items():
                if key == TARGET:
                    continue
                if value is None:
                    value = ""
                instance[key] = value

            instance['cnt_ad_reward'] = instance['cnt_ad_reward'] * multiplier
            instance['cnt_level_complete_quickplay'] = instance['cnt_level_complete_quickplay'] * multiplier
            instance['cnt_level_end_quickplay'] = instance['cnt_level_end_quickplay'] * multiplier
            instance['cnt_level_reset_quickplay'] = instance['cnt_level_reset_quickplay'] * multiplier
            instance['cnt_level_start_quickplay'] = instance['cnt_level_start_quickplay'] * multiplier
            instance['cnt_post_score'] = instance['cnt_post_score'] * multiplier
            instance['cnt_user_engagement'] = instance['cnt_user_engagement'] * multiplier
            instance['country'] = random.choice(SUBSET_COUNTRY_LIST)

            instances.append(instance)

        # predict with instances
        print(f"sending skewed traffic...")
        pred_count = 0
        for instance in instances:
            response = _endpoint.predict(instances=[instance])
            pred_count+=1
            # Print progress
            if pred_count % INTERVAL == 0:
                print(f" sent: {pred_count} requests")

        multiplier+=1
        total_requests+=len(instances)       
        print(f"End iteration : {i}")
        print(f"\ntotal_requests  : {total_requests}\n")
        time.sleep(args.sleep_time)

    end_time = time.time()
    full_runtime_mins = int((end_time - start_time) / 60)
    print(f"full_runtime_mins: {full_runtime_mins}")


def send_traffic(args):
    """
    > TODO
    """

    print("logging args....")
    print(args)
    
    print("starting monitoring_test...")
    monitoring_test(args)
    
# ====================================================
# Args
# ====================================================
def parse_args():
    """Parses parameters and hyperparameters for training a policy.

    Args:
      raw_args: A list of command line arguments.

    Re  turns:NETWORK_TYPE
    An argpase.Namespace object mapping (hyper)parameter names to the parsed
        values.
  """
    parser = argparse.ArgumentParser()

    # Path parameters
    parser.add_argument("--project_number", default="934903580331", type=str)
    parser.add_argument("--project_id", default="hybrid-vertex", type=str)
    parser.add_argument("--bucket_name", default="tmp", type=str)
    parser.add_argument("--artifacts_dir", type=str)
    parser.add_argument("--region", default="us-central1", type=str)
    
    parser.add_argument("--endpoint_id", default="6719135348548435968", type=str)
    parser.add_argument("--bq_logging_table_uri", default="bq://hybrid-vertex.churn_production_v5.req_resp", type=str)
    parser.add_argument("--iterations", default=5, type=int)
    parser.add_argument("--max_rows", default=4000, type=int)
    parser.add_argument("--sleep_time", default=1, type=int)
    parser.add_argument("--count", default=1, type=int)
    parser.add_argument("--multiplier", default=2.0, type=float)
    
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    send_traffic(args)
    
if __name__ == '__main__':
    main()