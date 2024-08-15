import wandb
import argparse
import pandas as pd

def parse_args():
    parser = argparse.ArgumentParser(description="Export wandb run metrics")
    parser.add_argument("--run_id", type=str, required=True)

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    api = wandb.Api()

    # run is specified by <entity>/<project>/<run_id>
    run = api.run(f"openkaito/sn5-validators/{args.run_id}")

    metrics_dataframe = pd.DataFrame(run.history())

    # Save the metrics to a CSV file
    with open("metrics.log", "w") as log_file:    
        log_file.write(metrics_dataframe.to_string(index=False))


    print(metrics_dataframe)


# /usr/bin/python3 export_wandb_history.py --run_id 9pg4kr69