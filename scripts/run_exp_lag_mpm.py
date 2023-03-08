import os

from utils import gen_ncu_args

kernels = ["buildPid+", "computeForce+", "precomputeTetMat+", "initColor+"]
args = gen_ncu_args(kernels)

log_base = "results/lag_mpm/"
model_base = "/home/ljf/playground/projects/meshtaichi/lag_mpm/models/armadillo0/"

fns = ['armadillo0.1.node']

for i in range(len(fns)):
    os.makedirs(log_base, exist_ok=True)
    result_log = f"{log_base}/{fns[i]}"
    print(result_log)
    model_fn = f"{model_base}/{fns[i]}"
    exe_file = (
        f"python lag_mpm/run.py --model {model_fn} --arch cuda --profiling"
    )

    cmd = f"ncu --export {result_log} {args} {exe_file}"
    os.system(cmd)
