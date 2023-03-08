import os

from utils import gen_ncu_args

kernels = ["ssvd+", "get_+", "mul+", "dot+", "add+", "update+"]
args = gen_ncu_args(kernels)

log_base = "results/pd/"
model_base = "/home/ljf/playground/tetgen/data/"

fns = ["armadillo_ascii.1.node", "iso_sphere_v245k.1.node", "iso_sphere_v374k.1.node"]

for i in range(len(fns)):
    os.makedirs(log_base, exist_ok=True)
    result_log = f"{log_base}/{fns[i]}"
    model_fn = f"{model_base}/{fns[i]}"
    exe_file = (
        f"python projective_dynamics/pd.py --model {model_fn} --arch cuda --profiling"
    )

    cmd = f"ncu --export {result_log} {args} {exe_file}"
    os.system(cmd)