import time

def normalize(items):
    return [
        str(item).strip().lower()
        for item in items
        if item is not None
    ]

def precision_at_k(recommended, relevant, k=5):
    recommended = normalize(recommended)
    relevant = normalize(relevant)
    recommended_k = recommended[:k]
    relevant_found = len(
        set(recommended_k) & set(relevant)
    )
    return relevant_found / max(len(recommended_k), 1)

def recall_at_k(recommended, relevant, k=5):
    recommended = normalize(recommended)
    relevant = normalize(relevant)
    recommended_k = recommended[:k]
    relevant_found = len(
        set(recommended_k) & set(relevant)
    )

    if len(relevant) == 0:
        return 0
    return relevant_found / len(relevant)

def hit_rate(recommended, relevant, k=5):
    recommended = normalize(recommended)
    relevant = normalize(relevant)
    recommended_k = recommended[:k]
    return int(
        len(set(recommended_k) & set(relevant)) > 0
    )

def measure_latency(func, *args, **kwargs):
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    latency = round(end - start, 3)
    return result, latency