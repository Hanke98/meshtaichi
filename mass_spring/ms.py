import argparse

import meshtaichi_patcher as Patcher
import taichi as ti

parser = argparse.ArgumentParser()
parser.add_argument("--model", default="models/armadillo0.1.node")
parser.add_argument("--arch", default="gpu")
parser.add_argument("--test", action="store_true")
parser.add_argument("--profiling", action="store_true")
parser.add_argument("--reorder", action="store_true")
parser.add_argument("--patch", type=int, default=256)
parser.add_argument("--block-dim", type=int, default=128)
parser.add_argument("--auto-cache", action="store_true", default=False)
parser.add_argument("--no-cache", action="store_true", default=False)
parser.add_argument("--search", type=int, default=-1)
args = parser.parse_args()
print(args)

auto_cache = args.auto_cache
no_cache = args.no_cache
search_cache = args.search
block_dim = args.block_dim

print(f"auto_cache: {auto_cache}")
print(f"no_cache: {no_cache}")
if no_cache:
    ti.init(
        arch=getattr(ti, args.arch),
        experimental_auto_mesh_local=False,
        device_memory_fraction=0.6,
        default_fp=ti.float32,
    )
else:
    ti.init(
        arch=getattr(ti, args.arch),
        experimental_auto_mesh_local=auto_cache,
        device_memory_fraction=0.6,
        default_fp=ti.float32,
    )

mass = 1.0
stiffness = 5e5
damping = 5
bottom_z = -70.0
dt = 2e-4
eps = 1e-6

mesh = Patcher.load_mesh(
    args.model, relations=["EV", "VV", "CV"], cache=True, patch_size=args.patch
)
mesh.verts.place(
    {"x": ti.math.vec3, "ox": ti.math.vec3, "v": ti.math.vec3, "f": ti.math.vec3},
    reorder=args.reorder,
)


mesh.edges.place({"rest_len": ti.f32})

mesh.verts.x.from_numpy(mesh.get_position_as_numpy())
mesh.verts.ox.copy_from(mesh.verts.x)
mesh.verts.v.fill([0.0, 0.0, -100.0])

attr_lists = [
    [mesh.verts.x],
    [mesh.verts.ox],
    [mesh.verts.v],
    [mesh.verts.x, mesh.verts.ox],
    [mesh.verts.x, mesh.verts.v],
    [mesh.verts.ox, mesh.verts.v],
    [mesh.verts.x, mesh.verts.ox, mesh.verts.v],
]


@ti.kernel
def vv_substep():
    if ti.static(no_cache):
        vv_substep_func()
    elif ti.static(search_cache >= 0):
        ti.mesh_local(*attr_lists[search_cache])
        vv_substep_func()
    elif not ti.static(auto_cache):
        ti.mesh_local(*(attr_lists[3]))
        vv_substep_func()
    else:
        vv_substep_func()


@ti.func
def vv_substep_func():
    for v0 in mesh.verts:
        v0.v *= ti.exp(-dt * damping)
        total_f = ti.Vector([0.0, -98.0, 0.0])

        for v1 in v0.verts:
            disp = v0.x - v1.x
            rest_disp = v0.ox - v1.ox
            total_f += (
                -stiffness
                * (disp.norm(eps) - rest_disp.norm(eps))
                * disp.normalized(eps)
            )

        v0.v += dt * total_f


# @ti.func
# def vv_substep_func():
#     ti.mesh_local(mesh.verts.x, mesh.verts.ox)
#     for v0 in mesh.verts:
#         v0.v *= ti.exp(-dt * damping)
#         total_f = ti.Vector([0.0, -98.0, 0.0])

#         for v1 in v0.verts:
#             disp = v0.x - v1.x
#             rest_disp = v0.ox - v1.ox
#             total_f += (
#                 -stiffness
#                 * (disp.norm(eps) - rest_disp.norm(eps))
#                 * disp.normalized(eps)
#             )
#         v0.v += dt * total_f


@ti.kernel
def ev_substep():
    for v in mesh.verts:
        v.v *= ti.exp(-dt * damping)
        v.f = ti.Vector([0.0, -98.0, 0.0])

    ti.mesh_local(mesh.verts.f, mesh.verts.x)
    for e in mesh.edges:
        v0 = e.verts[0]
        v1 = e.verts[1]
        disp0 = v0.x - v1.x
        spring_force = -stiffness * (disp0.norm() - e.rest_len) * disp0.normalized(eps)
        v0.f += spring_force
        v1.f -= spring_force


@ti.kernel
def advance():
    for v0 in mesh.verts:
        v0.v += dt * v0.f
        if v0.x[1] < bottom_z:
            v0.x[1] = bottom_z
            v0.v[1] = -v0.v[1]
            v0.v[0] = 0
            v0.v[2] = 0
        v0.x += v0.v * dt


indices = ti.field(ti.u32, shape=len(mesh.cells) * 4 * 3)


@ti.kernel
def initIndices():
    for c in mesh.cells:
        ind = [[0, 2, 1], [0, 3, 2], [0, 1, 3], [1, 2, 3]]
        for i in ti.static(range(4)):
            for j in ti.static(range(3)):
                indices[(c.id * 4 + i) * 3 + j] = c.verts[ind[i][j]].id


initIndices()


@ti.kernel
def calcRestlen():
    for e in mesh.edges:
        e.rest_len = (e.verts[0].x - e.verts[1].x).norm()


calcRestlen()
if args.test:
    for frame in range(100):
        for i in range(25):
            advance()
            vv_substep()
    arr = mesh.verts.x.to_numpy()
    assert "%.3f" % arr.mean() == "2.742"
    assert "%.1f" % (arr**2).mean() == "1351.7"
    exit(0)

if args.profiling:
    advance()
    vv_substep()
    exit(0)


window = ti.ui.Window("Mass Spring", (1024, 768))

canvas = window.get_canvas()
scene = ti.ui.Scene()
camera = ti.ui.Camera()
camera.position(-200, -20, -130)
camera.up(0, 1, 0)
camera.lookat(0, -70, 0)
camera.fov(75)


while window.running:
    for i in range(25):
        advance()
        vv_substep()

    camera.track_user_inputs(window, movement_speed=0.03, hold_key=ti.ui.RMB)
    scene.set_camera(camera)
    scene.ambient_light((0.5, 0.5, 0.5))
    scene.mesh(mesh.verts.x, indices, color=(0.5, 0.5, 0.5))
    scene.point_light(pos=(-50, 150, -50), color=(1, 1, 1))
    scene.point_light(pos=(-50, 150, -150), color=(1, 1, 1))
    canvas.scene(scene)
    window.show()
    for event in window.get_events(ti.ui.PRESS):
        if event.key in [ti.ui.ESCAPE]:
            window.running = False
