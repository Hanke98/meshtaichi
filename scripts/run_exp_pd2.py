import os

from utils import gen_ncu_args

# kernels = ["get_force+"]
# k = 0
# log_base = "results/pd-search-cache2/"

kernels = ["get_matrix+"]
k = 1
log_base = "results/pd-search-cache-new/"

args = gen_ncu_args(kernels)

model_base = "/home/ljf/playground/tetgen/data/"
fns = ["armadillo_ascii.1.node"]#, "iso_sphere_v245k.1.node", "iso_sphere_v374k.1.node"]
patch_sizes = [256 * i for i in range(12, 17)]


def search():
    global log_base
    log_base = f"{log_base}"

    for i in range(len(fns)):
        for p in patch_sizes:
            log_base_ = f"{log_base}/{kernels[0][:-1]}"
            os.makedirs(log_base_, exist_ok=True)
            for c in range(0, 16):
                result_log = f"{log_base_}/p_{p}_c_{c}"
                model_fn = f"{model_base}/{fns[i]}"

                exe_file = f"python projective_dynamics/pd.py --model {model_fn} --patch {p} --search {c} --kernel {k} --arch cuda --profiling"
                cmd = f"TI_OFFLINE_CACHE=0 ncu --export {result_log} {args} {exe_file}"
                os.system(cmd)
                # break
            # break
        break


search()
