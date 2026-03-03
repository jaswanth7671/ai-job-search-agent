def new_trace():
    return {"steps": []}

def log_step(trace, step_name, info):
    trace["steps"].append({
        "step": step_name,
        "info": info
    })
