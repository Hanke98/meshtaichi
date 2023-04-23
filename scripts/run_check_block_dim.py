import os

from utils import gen_ncu_args

# kernels = ["advance+", "vv_substep+", "calcRestlen+"]
kernels = ["vv_substep+"]
args = gen_ncu_args(kernels)

# log_base = "results/mass-spring/"
# use_reorder = ""

# log_base = "results/mass-spring-global-reorder-new/"
use_reorder = "--reorder"

# log_base = "results/mass-spring-no-cache/"
# use_reorder = "--reorder"

# log_base = "results/mass-spring-auto-cache/"
# use_reorder = "--reorder"

# log_base = "results/mass-spring-search-cache/"
# use_reorder = "--reorder"

# log_base = "results/mass-sprint-cache-test2"
# log_base = "results/mass-sprint-cache-test"

# log_base = "results/mass-sprint-cache-test-1024"

model_base = "/home/ljf/playground/tetgen/data/"
fns = ["armadillo_ascii.1.node", "iso_sphere_v245k.1.node", "iso_sphere_v374k.1.node"]
# patch_sizes = [256, 512, 1024, 2048, 4096]
patch_sizes = [256, 512]


def run1():
    global log_base
    log_base = f"{log_base}/profiling/"

    for i in range(len(fns)):
        os.makedirs(log_base, exist_ok=True)
        result_log = f"{log_base}/{fns[i]}"
        model_fn = f"{model_base}/{fns[i]}"
        exe_file = f"python mass_spring/ms.py --model {model_fn} --arch cuda --profiling {use_reorder}"

        cmd = f"ncu --export {result_log}log_{i} {args} {exe_file}"
        os.system(cmd)


def run2(use_auto_cache=False, no_cache=False):
    global log_base
    log_base = f"{log_base}/patch_size/"
    auto_cache_str = "--auto-cache" if use_auto_cache else ""
    no_cache_str = "--no-cache" if no_cache else ""
    for i in range(len(fns)):
        for p in patch_sizes:
            log_base_ = f"{log_base}/{fns[i]}/"
            os.makedirs(log_base_, exist_ok=True)
            result_log = f"{log_base_}/patch_size_{p}_block_dim_{p}"
            model_fn = f"{model_base}/{fns[i]}"
            exe_file = f"python mass_spring/ms.py --model {model_fn} --block-dim {p} --patch {p} --arch cuda {no_cache_str} {auto_cache_str} --profiling {use_reorder}"

            cmd = f"ncu --export {result_log}log {args} {exe_file}"
            os.system(cmd)
        break


log_base = "results/mass-spring-check-block-dim"

run2()
