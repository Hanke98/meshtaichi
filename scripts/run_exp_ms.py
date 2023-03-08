import os

from utils import gen_ncu_args

kernels = ["advance+", "vv_substep+", "calcRestlen+"]
args = gen_ncu_args(kernels)

log_base = "results/mass-spring/"
use_reorder = ""

log_base = "results/mass-spring-global-reorder/"
use_reorder = "--reorder"

model_base = "/home/ljf/playground/tetgen/data/"
fns = ["iso_sphere_v374k.1.node", "armadillo_ascii.1.node", "iso_sphere_v245k.1.node"]

for i in range(len(fns)):
    os.makedirs(log_base, exist_ok=True)
    result_log = f"{log_base}/{fns[i]}"
    model_fn = f"{model_base}/{fns[i]}"
    exe_file = f"python mass_spring/ms.py --model {model_fn} --arch cuda --profiling {use_reorder}"

    cmd = f"ncu --export {result_log}log_{i} {args} {exe_file}"
    os.system(cmd)
