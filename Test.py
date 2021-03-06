# coding:utf-8
import maya.cmds as mc
import pymel.core as pm
import math
from collections import OrderedDict

selected = mc.ls(sl=True, l=True)


def create_curve(obj):

    if mc.nodeType(obj) != "joint":
        mc.warning("The object is not a joint")
        return
    list_joint = [obj] + list(reversed(mc.listRelatives(obj, f=1, ad=1, typ="joint")))  # 深度遍历

    pos_joint_point = []  # 存取每个骨骼的位置
    for i in list_joint:
        pos_joint_point.append(mc.xform(i, q=True, ws=True, t=True))
    curve_name = mc.curve(p=pos_joint_point, d=1)

    return curve_name, list_joint


def create(obj_list, turn="off"):

    if turn == "on":
        for i in obj_list:
            create_curve(i)
        return

    for i in obj_list:
        if mc.objectType(i) != "joint":
            mc.warning("The object is not a joint")
            continue
        pos_edge = OrderedDict()  # 创建一个无序字典，方便后面的操作
        next_joint_pos = mc.xform(mc.listRelatives(i, c=True, f=True, typ="joint"), q=True, ws=True, t=True)
        plane1 = mc.polyPlane(ch=False, sx=1, sy=1)
        mc.matchTransform(plane1[0], i, piv=True, pos=True, rot=True, scl=True)

        # 获取平均坐标
        for num in range(4):
            obj_edge = pm.PyNode("{}.e[{}]".format(plane1[0], num))
            point_1 = obj_edge.getPoint(0, space="world")
            point_2 = obj_edge.getPoint(1, space="world")
            x = (point_1[0]+point_2[0])/2
            y = (point_1[1]+point_2[1])/2
            z = (point_1[2]+point_2[2])/2
            pos_edge["{}.e[{}]".format(plane1[0], num)] = [x, y, z]

        # 求离下一个骨骼的最短距离
        for value in pos_edge.values():
            x1 = next_joint_pos[0]-value[0]
            y1 = next_joint_pos[1]-value[1]
            z1 = next_joint_pos[2]-value[2]
            pos1 = math.sqrt(x1**2+y1**2+z1**2)
            value.append(pos1)
        distance_edge = [dit[3] for dit in pos_edge.values()]
        close_edge_name = list(pos_edge)[distance_edge.index(min(distance_edge))]  # 最短距离的边

        curve_name, list_joint = create_curve(i)  # 创建曲线，并返回曲线名字以及骨骼List

        mc.polyExtrudeEdge(close_edge_name, curve_name, ch=False, kft=1, d=3*len(list_joint), inc=curve_name)

        mc.delete(curve_name)

        mc.bindSkin(plane1[0], i, ta=True)


create(selected)
