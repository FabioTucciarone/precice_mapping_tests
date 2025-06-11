#!/usr/bin/env python3

import pyvista as pv

pv.global_theme.font.family = 'times'

for scalars in ["Franke", "scaled Eggholder", "scaled cos"]: #"Franke", "scaled Eggholder", "scaled cos"
    plt = pv.Plotter(window_size=[900, 300])

    camera = pv.Camera()
    camera.position    = (0.62,     0.05, 0.49)
    camera.focal_point = (0.62 - 1, 0.05, 0.49)
    
    axes = pv.Axes(show_actor=False, line_width=2)
    plt.add_actor(axes.actor)
    plt.camera = camera

    mesh = pv.read('test/other/eval.vtk')
    mesh.rotate_z(90, point=axes.origin, inplace=True)

    plt.add_mesh(mesh, scalars=scalars, cmap='coolwarm', show_scalar_bar=False)

    _ = plt.add_scalar_bar(scalars, height=0.15, vertical=False, title_font_size=25, label_font_size=25, outline=False, fmt='%10.1f')

    plt.save_graphic(f"turbine-{scalars.lower().replace(' ', '-')}.pdf") 
    plt.show()