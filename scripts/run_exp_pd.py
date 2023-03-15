import os

from utils import gen_ncu_args

kernels = ["ssvd+", "get_+", "mul+", "dot+", "add+", "update+"]
args = gen_ncu_args(kernels)

log_base = "results/pd/"
model_base = "/home/ljf/playground/tetgen/data/"

fns = ["armadillo_ascii.1.node", "iso_sphere_v245k.1.node", "iso_sphere_v374k.1.node"]
patch_sizes = [256, 512, 1024, 2048, 4096]

def run1():
    global log_base
    log_base = f'{log_base}/profiling/'
    for i in range(len(fns)):
        os.makedirs(log_base, exist_ok=True)
        result_log = f"{log_base}/{fns[i]}"
        model_fn = f"{model_base}/{fns[i]}"
        exe_file = (
            f"python projective_dynamics/pd.py --model {model_fn} --arch cuda --profiling"
        )

        cmd = f"ncu --export {result_log} {args} {exe_file}"
        os.system(cmd)

def run2():
    global log_base
    log_base = f'{log_base}/patch_size/'
    for i in range(len(fns)):
        for p in patch_sizes:
            log_base_ = f'{log_base}/{fns[i]}/'
            os.makedirs(log_base_, exist_ok=True)
            result_log = f"{log_base_}/{fns[i]}_patch_size_{p}"
            model_fn = f"{model_base}/{fns[i]}"
            exe_file = (
                f"python projective_dynamics/pd.py --model {model_fn} --patch {p} --arch cuda --profiling"
            )

            cmd = f"ncu --export {result_log} {args} {exe_file}"
            os.system(cmd)

# run1()
run2()
