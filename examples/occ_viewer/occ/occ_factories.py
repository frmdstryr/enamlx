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

QT_FACTORIES['Box'] = occ_box_factory
QT_FACTORIES['Cone'] = occ_cone_factory
QT_FACTORIES['Cylinder'] = occ_cylinder_factory
QT_FACTORIES['HalfSpace'] = occ_half_space_factory
#QT_FACTORIES['OneAxis'] = occ_one_axis_factory
QT_FACTORIES['Prism'] = occ_prism_factory
QT_FACTORIES['Revol'] = occ_revol_factory
QT_FACTORIES['Revolution'] = occ_revolution_factory
QT_FACTORIES['Sphere'] = occ_sphere_factory
QT_FACTORIES['Sweep'] = occ_sweep_factory
QT_FACTORIES['Torus'] = occ_torus_factory
QT_FACTORIES['Wedge'] = occ_wedge_factory


QT_FACTORIES['Common'] = occ_common_factory
QT_FACTORIES['Cut'] = occ_cut_factory
QT_FACTORIES['Fuse'] = occ_fuse_factory
