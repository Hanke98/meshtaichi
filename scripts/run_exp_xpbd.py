import os

from utils import gen_ncu_args

kernels = [
    "initialize+",
    "initIndices+",
    "applyExtForce+",
    "update+",
    "preSolve+",
    "postSolve+",
    "solveStretch+",
    "solveBending+",
]
args = gen_ncu_args(kernels)

log_base = "results/xpbd/"

os.makedirs(log_base, exist_ok=True)
result_log = f"{log_base}/xpbd"
exe_file = f"python xpbd_cloth/run_demo.py --arch cuda"

cmd = f"ncu --export {result_log} {args} {exe_file}"
os.system(cmd)
