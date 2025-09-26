import polars as pl
import time

def time_function(func, *args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    return result, end_time - start_time

_, polars_time = time_function(pl.read_csv, 'api/data/metrics.csv')

print(f"Polars read time: {polars_time:.4f} seconds")