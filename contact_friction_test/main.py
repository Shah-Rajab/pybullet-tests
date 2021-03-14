import pybullet as p
import numpy as np
import pybullet_data
from time import sleep


'''
Open cube.urdf file and change the following parameters:
<lateral_friction value="1.0"/>
<rolling_friction value="1.0"/>
<spinning_friction value="1.0"/>
'''

if __name__ == '__main__':
    p.connect(p.GUI)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    useMaximalCoordinates = False
    p.loadURDF("plane.urdf", useMaximalCoordinates=useMaximalCoordinates)

    p.loadURDF("./urdf_files/cube.urdf", [0, 0, 0.5], useMaximalCoordinates=useMaximalCoordinates)

    # Try Sphere?
    # p.loadURDF("sphere2.urdf",[0,0,1])
    # p.loadURDF("sphere2.urdf", [0, 0, 0.5], useMaximalCoordinates=useMaximalCoordinates)


    p.setGravity(10, 0, -9.81) # Change the first value to replicate a force parallel to the ground applied to the cube
    while (1):
      p.stepSimulation()
      sleep(0.004)
      pts = p.getContactPoints()

      print("num pts=", len(pts))
      totalNormalForce = 0
      totalFrictionForce = [0, 0, 0]
      totalLateralFrictionForce = [0, 0, 0]
      for pt in pts:
        #sleep(0.1)
        print("pt.normal=",pt[7])
        print("pt.normalForce=",pt[9])
        totalNormalForce += pt[9]
        print("pt.lateralFrictionA=",pt[10])
        print("pt.lateralFrictionADir=",pt[11])
        print("pt.lateralFrictionB=",pt[12])
        print("pt.lateralFrictionBDir=",pt[13])
        totalLateralFrictionForce[0] += pt[11][0] * pt[10] + pt[13][0] * pt[12]
        totalLateralFrictionForce[1] += pt[11][1] * pt[10] + pt[13][1] * pt[12]
        totalLateralFrictionForce[2] += pt[11][2] * pt[10] + pt[13][2] * pt[12]
        print("-" * 10)

      print("totalNormalForce=", totalNormalForce)
      print("totalLateralFrictionForce=", totalLateralFrictionForce)
      print("#" * 40)