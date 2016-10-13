'''
Created on Sep 28, 2016

@author: 
'''
from enaml.qt.qt_factories import QT_FACTORIES

def occ_box_factory():
    from occ.occ_solid import OccBox
    return OccBox

def occ_cone_factory():
    from occ.occ_solid import OccCone
    return OccCone

def occ_cylinder_factory():
    from occ.occ_solid import OccCylinder
    return OccCylinder

def occ_half_space_factory():
    from occ.occ_solid import OccHalfSpace
    return OccHalfSpace

def occ_one_axis_factory():
    from occ.occ_solid import OccOneAxis
    return OccOneAxis

def occ_prism_factory():
    from occ.occ_solid import OccPrism
    return OccPrism

def occ_revol_factory():
    from occ.occ_solid import OccRevol
    return OccRevol

def occ_revolution_factory():
    from occ.occ_solid import OccRevolution
    return OccRevolution

def occ_sphere_factory():
    from occ.occ_solid import OccSphere
    return OccSphere

def occ_sweep_factory():
    from occ.occ_solid import OccSweep
    return OccSweep

def occ_torus_factory():
    from occ.occ_solid import OccTorus
    return OccTorus

def occ_wedge_factory():
    from occ.occ_solid import OccWedge
    return OccWedge

def occ_common_factory():
    from occ.occ_algo import OccCommon
    return OccCommon

def occ_cut_factory():
    from occ.occ_algo import OccCut
    return OccCut

def occ_fuse_factory():
    from occ.occ_algo import OccFuse
    return OccFuse

def occ_point_factory():
    from occ.occ_draw import OccPoint
    return OccPoint

def occ_vertex_factory():
    from occ.occ_draw import OccVertex
    return OccVertex

def occ_line_factory():
    from occ.occ_draw import OccLine
    return OccLine

def occ_circle_factory():
    from occ.occ_draw import OccCircle
    return OccCircle

def occ_ellipse_factory():
    from occ.occ_draw import OccEllipse
    return OccEllipse

def occ_hyperbola_factory():
    from occ.occ_draw import OccHyperbola
    return OccHyperbola

def occ_parabola_factory():
    from occ.occ_draw import OccParabola
    return OccParabola

def occ_wire_factory():
    from occ.occ_draw import OccWire
    return OccWire

def occ_fillet_factory():
    from occ.occ_algo import OccFillet
    return OccFillet

def occ_chamfer_factory():
    from occ.occ_algo import OccChamfer
    return OccChamfer

def occ_thick_solid_factory():
    from occ.occ_algo import OccThickSolid
    return OccThickSolid


#: Solids
QT_FACTORIES['Box'] = occ_box_factory
QT_FACTORIES['Cone'] = occ_cone_factory
QT_FACTORIES['Cylinder'] = occ_cylinder_factory
QT_FACTORIES['Prism'] = occ_prism_factory
QT_FACTORIES['Sphere'] = occ_sphere_factory
QT_FACTORIES['Sweep'] = occ_sweep_factory
QT_FACTORIES['Torus'] = occ_torus_factory
QT_FACTORIES['Wedge'] = occ_wedge_factory

#: Primatives
QT_FACTORIES['HalfSpace'] = occ_half_space_factory
#QT_FACTORIES['OneAxis'] = occ_one_axis_factory
QT_FACTORIES['Revol'] = occ_revol_factory
QT_FACTORIES['Revolution'] = occ_revolution_factory

#: Operations
QT_FACTORIES['Common'] = occ_common_factory
QT_FACTORIES['Cut'] = occ_cut_factory
QT_FACTORIES['Fuse'] = occ_fuse_factory
QT_FACTORIES['Fillet'] = occ_fillet_factory
QT_FACTORIES['Chamfer'] = occ_chamfer_factory
QT_FACTORIES['ThickSolid'] = occ_thick_solid_factory

#: Draw
QT_FACTORIES['Point'] = occ_point_factory
QT_FACTORIES['Vertex'] = occ_vertex_factory
QT_FACTORIES['Line'] = occ_line_factory
QT_FACTORIES['Circle'] = occ_circle_factory
QT_FACTORIES['Ellipse'] = occ_ellipse_factory
QT_FACTORIES['Hyperbola'] = occ_hyperbola_factory
QT_FACTORIES['Parabola'] = occ_parabola_factory
QT_FACTORIES['Wire'] = occ_wire_factory