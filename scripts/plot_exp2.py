import os
import re

import matplotlib.pyplot as plt
import ncu_report
import numpy as np

occpancy = []
theory_occpancy = []
duration = []
flops = []
no_eligable = []
patch_size = []
sectors_per_prequest = []
shared_mem_bc_per_inst = []
wf_excessive_pct = []

# name = "PD"
# base_dir = "results/pd/patch_size/armadillo_ascii.1.node/"
name='Mass Spring'
base_dir = "results/mass-spring-global-reorder/patch_size/armadillo_ascii.1.node/"


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


def get_patch_size(str):
    pattern = r"node_patch_size_(\d+)"
    match = re.search(pattern, str)
    if match:
        number = int(match.group(1))
        return number
    assert False


fns = os.listdir(base_dir)

for fn in fns:
    my_context = ncu_report.load_report(f"{base_dir}/{fn}")
    print(fn)

    _size = get_patch_size(fn)
    patch_size.append(_size)
    my_range = my_context.range_by_idx(0)
    my_action = my_range.action_by_idx(0)
    occu = my_action["sm__warps_active.avg.pct_of_peak_sustained_active"]
    theo_occu = my_action["sm__maximum_warps_per_active_cycle_pct"]
    dura = my_action["gpu__time_duration.sum"]
    no_eli = my_action["smsp__issue_inst0.avg.pct_of_peak_sustained_active"]
    spp = my_action["l1tex__average_t_sectors_per_request_pipe_lsu.ratio"]
    wf = my_action["memory_l1_wavefronts_shared"].value()
    wf_exce = my_action["derived__memory_l1_wavefronts_shared_excessive"].value()
    wf_excessive_pct.append(wf_exce/wf*100)
    shared_mem_bc = my_action["l1tex__data_bank_conflicts_pipe_lsu_mem_shared.sum"]
    shared_mem_inst = my_action["sm__sass_inst_executed_op_shared.sum"]
    shared_mem_bc_per_inst.append(shared_mem_bc.value()/shared_mem_inst.value())
    sectors_per_prequest.append(spp.value())
    occpancy.append(occu.value())
    theory_occpancy.append(theo_occu.value())
    duration.append(dura.value())
    flops.append(compute_flops(my_action))
    no_eligable.append(no_eli.value())


idx = np.argsort(patch_size)
patch_size = np.array(patch_size)
patch_size = patch_size[idx]

peak_flops = 13.450e12  # TFLOPS

x = np.arange(0, len(occpancy), 1)
duration = np.array(duration) / 1e9
theory_occpancy = np.array(theory_occpancy)
occpancy = np.array(occpancy)
# theory_occpancy -= occpancy
flops /= duration

flops_pct = flops / max(flops) * 100
# flops_pct = flops / flops[0] * 100

duration = duration[idx]
theory_occpancy = theory_occpancy[idx]
occpancy = occpancy[idx]
flops_pct = flops_pct[idx]


def auto_text(ax, rects, pct=False):
    for rect in rects:
        pct_sym = '%' if pct else ''
        text = f'{round(rect.get_height(), 2)}{pct_sym}'
        ax.text(
            rect.get_x(),
            rect.get_height(),
            text,
            ha="left",
            va="bottom",
        )


fig = plt.figure(figsize=(13, 8.5))

ax = fig.add_subplot(111)
x_loc = np.arange(len(occpancy))
x_locs = []

def plot1():
    n_indi = 4
    width = 0.8
    w = width / n_indi

    for k in range(n_indi):
        x_locs.append(x_loc + w * k - width / 2 + w / 2)

    rect1 = ax.bar(x_locs[1], occpancy, label="Occpancy", width=w)
    rect2 = ax.bar(x_locs[0], theory_occpancy, label="Theorectical occpancy", width=w)
    rect3 = ax.bar(x_locs[2], flops_pct, label="Achieved FLOPS to maximum one", width=w)
    rect4 = ax.bar(x_locs[3], no_eligable, label="No eligable", width=w)
    auto_text(ax, rect1)
    auto_text(ax, rect2)
    auto_text(ax, rect3)
    auto_text(ax, rect4)

    ax.set_ylabel("Percentage", fontsize=16)
    ax.set_xlabel("Patch Size", fontsize=16)
    plt.ylim(0, 130)
    plt.xticks(
        np.arange(len(patch_size)),
        patch_size,
        fontsize=16,
    )
    plt.subplots_adjust(left=0.06, right=0.98, top=0.95, bottom=0.08)
    ax.legend()


def plot2():
    global name
    name = f"Coalesing Test {name}"
    n_indi = 3 
    width = 0.8
    w = width / n_indi

    for k in range(n_indi):
        x_locs.append(x_loc + w * k - width / 2 + w / 2)

    ax2 = ax.twinx()
    auto_text(ax, ax.bar(x_locs[0], wf_excessive_pct, label="Excessive WaveFront", width=w, color='orange'), pct=True)
    auto_text(ax2, ax2.bar(x_locs[1], sectors_per_prequest, label="Sectors/Request", width=w))
    auto_text(ax2, ax2.bar(x_locs[2], shared_mem_bc_per_inst, label="Bank Conflicts/Instruction", width=w))

    ax.set_ylabel("Percentage", fontsize=16)
    ax.set_xlabel("Patch Size", fontsize=16)
    ax2.set_ylabel("Ratio", fontsize=16)
    # plt.ylim(0, 130)
    plt.xticks(
        np.arange(len(patch_size)),
        patch_size,
        fontsize=16,
    )
    plt.subplots_adjust(left=0.06, right=0.95, top=0.93, bottom=0.06)
    # ax.legend()
    fig.legend(loc=1)

# plot1()
plot2()

plt.title(name, fontsize=20)
plt.savefig(f"{name}.png")
