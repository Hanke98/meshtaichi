default_metrics = [
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
    "sm__sass_inst_executed_op_shared",
    "l1tex__t_bytes",
    "l1tex__data_pipe_lsu_wavefronts_mem_shared",
    "l1tex__average_t_sectors_per_request_pipe_lsu",
    "l1tex__data_bank_conflicts_pipe_lsu",
    "l1tex__data_bank_reads",
    "l1tex__data_bank_writes",
    "launch__shared_mem_per_block_static"
]

default_metrics = [
    "launch__shared_mem_per_block_static"
    "l1tex__t_sector_hit_rate.pct",
    "lts__t_sector_hit_rate.pct",
 ]


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

def get_metric_strings(_met):
    metrics_str = ""
    for m in _met:
        metrics_str += m
        metrics_str += ","
    metrics_str = metrics_str[:-1]
    return metrics_str

def gen_ncu_args(_ker, _met=default_metrics):
    metrics_str = get_metric_strings(_met)
    kernel_regx = get_kernel_reg(_ker)
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
    return args
