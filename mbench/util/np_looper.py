def np_looper(fn, np_x):
    lambda_fn = lambda _: fn(_)
    return lambda_fn(np_x)
