import os

from utils import gen_ncu_args

kernels = ["ptp+", "get_level+"]
args = gen_ncu_args(kernels)

log_base = "results/geodesic_distance/"
model_base = "models/"

fns = ['monkey_v31k.ply', 'monkey_v126k.ply', 'monkey_v504k.ply', 'monkey_v2m.ply']

for i in range(len(fns)):
    os.makedirs(log_base, exist_ok=True)
    result_log = f"{log_base}/{fns[i]}"
    model_fn = f"{model_base}/{fns[i]}"
    exe_file = (
        f"python geodesic_distance/geodesic.py --model {model_fn} --arch cuda --profiling"
    )

    cmd = f"ncu --export {result_log} {args} {exe_file}"
    os.system(cmd)
