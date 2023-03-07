import os

exe_file = "build/shared_mem"

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
    "smsp__warps_launched"
]

metrics_str = ""
for m in metrics:
    metrics_str += m
    metrics_str += ","

metrics_str = metrics_str[:-1]

nsight = "nv-nsight-cu-cli"
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
        -k regex:\"adva*|vv*|calcRe*\"\
        --check-exit-code yes "

# result_log = f"results/iso_sphere_v245k/"
result_log = f"results/iso_sphere_v374k/"
os.makedirs(result_log, exist_ok=True)
# model_fn = '/home/ljf/playground/tetgen/data/armadillo_ascii.1.node'
# model_fn = '/home/ljf/playground/tetgen/data/iso_sphere_v245k.1.node'
model_fn = '/home/ljf/playground/tetgen/data/iso_sphere_v374k.1.node'
exe_file = f"python mass_spring/ms.py --model {model_fn} --arch cuda"
# exe_file = "python tmp/test.py"

for i in range(1):
    cmd = f"{nsight} --export {result_log}log_{i} {args} {exe_file} --profiling"
    # print(cmd)
    os.system(cmd)
