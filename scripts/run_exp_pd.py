import os

nsight = "ncu"

metrics = [
    "smsp__sass_thread_inst_executed_op_fadd_pred_on",
    "smsp__sass_thread_inst_executed_op_fmul_pred_on",
    "smsp__sass_thread_inst_executed_op_ffma_pred_on",
    "sm__warps_launched",
    "sm__ctas_launched",
    "sm__ctas_active",
    "sm__warps_active.sum.per_cycle_active",
    "smsp__warps_active.avg.per_cycle_active",
    "smsp__warps_active.sum.per_cycle_active",
    "smsp__warps_active.max.per_cycle_active",
    "smsp__warps_active.min.per_cycle_active",
    "smsp__warps_launched",
]

metrics_str = ""
for m in metrics:
    metrics_str += m
    metrics_str += ","
metrics_str = metrics_str[:-1]


def get_kernel_reg(_ker):
    regx = ""
    if len(_ker) > 0:
        regx = f'-k regex:"'
        for k in _ker:
            regx += "^" 
            regx += k
            regx += "|"

        regx = regx[:-1] + '"'
    return regx


kernels = ["ssvd+", "get_+", "mul+", "dot+", "add+", "update+"]
kernel_regx = get_kernel_reg(kernels)

args = f"--force-overwrite \
        --target-processes application-only \
        --replay-mode kernel \
        --kernel-name-base function \
        --launch-skip-before-match 0 \
        --section ComputeWorkloadAnalysis \
        --section InstructionStats \
        --section LaunchStats \
        --section MemoryWorkloadAnalysis \
        --section MemoryWorkloadAnalysis_Chart \
        --section MemoryWorkloadAnalysis_Tables \
        --section Nvlink_Tables \
        --section Nvlink_Topology \
        --section Occupancy \
        --section SchedulerStats \
        --section SourceCounters \
        --section SpeedOfLight \
        --section SpeedOfLight_RooflineChart \
        --section WarpStateStats \
        --sampling-interval auto \
        --sampling-max-passes 5 \
        --sampling-buffer-size 33554432 \
        --profile-from-start 1 \
        --cache-control all \
        --clock-control base \
        --apply-rules yes \
        --import-source no \
        --metrics {metrics_str} \
        {kernel_regx} \
        --check-exit-code yes "

log_base = "results/pd/"
model_base = "/home/ljf/playground/tetgen/data/"

fns = ["armadillo_ascii.1.node", "iso_sphere_v245k.1.node", "iso_sphere_v374k.1.node"]

for i in range(len(fns)):
    os.makedirs(log_base, exist_ok=True)
    result_log = f"{log_base}/{fns[i]}"
    model_fn = f"{model_base}/{fns[i]}"
    exe_file = f"python projective_dynamics/pd.py --model {model_fn} --arch cuda --profiling"

    cmd = f"{nsight} --export {result_log} {args} {exe_file}"
    os.system(cmd)
