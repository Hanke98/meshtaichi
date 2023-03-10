import matplotlib.pyplot as plt
import ncu_report
import numpy as np
import os


def compute_flops(action):
    metrics = [
        "smsp__sass_thread_inst_executed_op_fadd_pred_on.sum",
        "smsp__sass_thread_inst_executed_op_fmul_pred_on.sum",
        "smsp__sass_thread_inst_executed_op_ffma_pred_on.sum",
    ]
    weights = [1, 1, 2]
    res = 0.0
    for i, m in enumerate(metrics):
        res += weights[i] * action[m].value()
    return res


peak_bandwith = 0.616 #TBPS
peak_flops = 13.450 #TFLOPS

bases = ['./results/pd/', './results/mass-spring', './results/lag_mpm']
labels = ['pd', 'mass-spring', 'lag_mpm']
kernels = [2, 2, 3]

fig = plt.figure()
ax = fig.add_subplot(111)
ridge_point = peak_flops/peak_bandwith
plt.xscale('log')
plt.yscale('log')


for idx, base in enumerate(bases):
    fns = os.listdir(base)
    occpancy = []
    theory_occpancy = []
    duration = []
    flops = []
    no_eligable = []
    dram_bytes = []

    for fn in fns:
        my_context = ncu_report.load_report(f'{base}/{fn}')

        my_range = my_context.range_by_idx(0)
        my_action = my_range.action_by_idx(kernels[idx])

        occu = my_action["sm__warps_active.avg.pct_of_peak_sustained_active"]
        theo_occu = my_action["sm__maximum_warps_per_active_cycle_pct"]
        dura = my_action["gpu__time_duration.sum"]
        no_eli = my_action["smsp__issue_inst0.avg.pct_of_peak_sustained_active"]
        mem_in = my_action["dram__bytes_read.sum"]
        mem_out = my_action["dram__bytes_write.sum"]
        occpancy.append(occu.value())
        theory_occpancy.append(theo_occu.value())
        duration.append(dura.value())
        flops.append(compute_flops(my_action))
        dram_bytes.append(mem_in.value() + mem_out.value())
        no_eligable.append(no_eli.value())

    x = np.arange(0, len(occpancy), 1)
    duration = np.array(duration) / 1e9
    theory_occpancy = np.array(theory_occpancy)
    occpancy = np.array(occpancy)
    dram_bytes = np.array(dram_bytes)
    flop = flops
    arith_intensity = flop / dram_bytes
    flops /= duration
    print(arith_intensity, flops)
    plt.scatter(arith_intensity, flops/1e12, label=labels[idx])
    plt.legend()
    plt.ylim(1e-2, 3.8e1)
    plt.xlim(1e-2, 1e4)

plt.plot([0, ridge_point, 1e4], [0, peak_flops, peak_flops], '-r')
plt.ylabel("FLOPS/(1e12)", fontsize=16)
plt.xlabel("Arithmetic(FLOP/Bytes)", fontsize=16)
plt.title("Roofline", fontsize=16)

plt.grid()

plt.subplots_adjust(left=0.12, right=0.98, top=0.92, bottom=0.12)
plt.savefig('roofline.png')


