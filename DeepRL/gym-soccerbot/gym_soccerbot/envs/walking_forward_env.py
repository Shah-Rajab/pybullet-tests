import gym
from gym import spaces
from gym.utils import seeding

import os
import pybullet as pb
import pybullet_data
import math
import numpy as np
from pybullet_utils import bullet_client as bc
import logging

logger = logging.getLogger(__name__)


class WalkingForward(gym.Env):
    metadata = {'render.modes': ['human', 'rgb_array'], 'video.frames_per_second': 50}

    def __init__(self, renders=False):
        # start the bullet physics server
        self._renders = renders
        self._render_height = 200
        self._render_width = 320
        self._physics_client_id = -1

        self.prev_lin_vel = np.array([0, 0, 0])
        self.STANDING_HEIGHT = 0.36
        self.goal_xy = [5, 5]

        # TODO Change action space
        self.JOINT_DIM = 18
        joint_limit_high = np.array([np.pi / 2] * self.JOINT_DIM)

        self.action_space = spaces.Box(low=-joint_limit_high, high=joint_limit_high, dtype=np.float32) #, shape=(1, self.JOINT_DIM)

        # TODO Change observation space

        self.POSE_DIM = 3
        self.IMU_DIM = 6
        observation_dim = self.JOINT_DIM + self.IMU_DIM + self.POSE_DIM

        imu_limit_high = np.array([np.inf] * self.IMU_DIM)
        pose_limit_high = np.array([np.inf] * self.POSE_DIM)
        observation_limit = np.concatenate((joint_limit_high, imu_limit_high, pose_limit_high))
        self.observation_space = spaces.Box(low=-observation_limit, high=observation_limit, dtype=np.float32) #shape=(1, observation_dim),

        self.seed()
        #    self.reset()
        self.viewer = None
        self._configure()

    def _configure(self, display=None):
        self.display = display

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def _imu(self):
        p = self._p
        [lin_vel, ang_vel] = p.getBaseVelocity(self.soccerbotUid)
        lin_vel = np.array(lin_vel, dtype = np.float32)
        lin_acc = (lin_vel - self.prev_lin_vel) / self.timeStep
        ang_vel = np.array(ang_vel, dtype=np.float32)
        self.prev_lin_vel = lin_vel

        return np.concatenate((lin_acc, ang_vel))

    def _global_pos(self):
        p = self._p
        pos, _ = p.getBasePositionAndOrientation(self.soccerbotUid)
        return np.array(pos, dtype=np.float32)

    def _feet(self):
        pass

    def step(self, action):
        if self._renders == True:
            sleep(self.timeStep)
        p = self._p
        p.setJointMotorControlArray(bodyIndex=self.soccerbotUid, controlMode=pb.POSITION_CONTROL,
                                     jointIndices=list(range(0, 18, 1)), targetPositions=action)
        p.stepSimulation()
        imu = self._imu()
        joint_states = p.getJointStates(self.soccerbotUid, list(range(0, 18, 1)))
        joints_pos = np.array([state[0] for state in joint_states], dtype=np.float32)

        """
        From core.py in gym:
        Returns:
            observation (object): agent's observation of the current environment
            reward (float) : amount of reward returned after previous action
            done (bool): whether the episode has ended, in which case further step() calls will return undefined results
            info (dict): contains auxiliary diagnostic information (helpful for debugging, and sometimes learning)
        """
        # TODO Observation
        observation = np.concatenate((joints_pos, imu, self._global_pos()))
        # TODO calculate done
        # TODO calculate reward
        if self._global_pos()[2] < (self.STANDING_HEIGHT / 2): # check z component
            done = True
            reward = -1000
        else:
            if np.linalg.norm(self._global_pos()[0:2] - self.goal_xy) < 0.1:
                done = True
                reward = 1 / np.linalg.norm(self._global_pos()[0:2] - self.goal_xy)
            elif np.linalg.norm(self._global_pos()[0:2] - self.goal_xy) > 10:
                done = True
                reward = -100
            else:
                done = False
                reward = 1 / np.linalg.norm(self._global_pos()[0:2] - self.goal_xy)

        info = {}
        return observation, reward, done, info

    def reset(self):
        if self._physics_client_id < 0:
            if self._renders:
                self._p = bc.BulletClient(connection_mode=pb.GUI)
                self._p.configureDebugVisualizer(pb.COV_ENABLE_RENDERING, 1)
            else:
                self._p = bc.BulletClient()
            self._physics_client_id = self._p._client

            p = self._p
            p.resetSimulation()
            # load ramp

            # load soccerbot
            self.soccerbotUid = p.loadURDF("/home/shahryar/PycharmProjects/DeepRL/gym-soccerbot/gym_soccerbot/soccer_description/models/soccerbot_stl.urdf", useFixedBase=False,
                                            basePosition=[0, 0, self.STANDING_HEIGHT],
                                            baseOrientation=[0., 0., 0., 1.],
                                            flags=pb.URDF_USE_INERTIA_FROM_FILE)
                            # |p.URDF_USE_SELF_COLLISION|p.URDF_USE_SELF_COLLISION_EXCLUDE_PARENT)

            urdfRootPath = pybullet_data.getDataPath()
            planeUid = p.loadURDF(os.path.join(urdfRootPath, "plane.urdf"), basePosition=[0, 0, 0])

            # TODO change dynamics ...

            # TODO change timestep ...
            self.timeStep = 1./240
            p.setTimeStep(self.timeStep)

            p.setGravity(0, 0, -9.81)
            p.setRealTimeSimulation(0)  # To manually step simulation later
        p = self._p


        # TODO reset joint state

        #p.resetJointStates(self.soccerbotUid, list(range(0, 18, 1)), 0)
        standing_poses = [0] * self.JOINT_DIM
        for i in range(18):
            p.resetJointState(self.soccerbotUid, i, standing_poses[i])

        # TODO set state???

        # TODO get observation
        imu = self._imu()
        joint_states = p.getJointStates(self.soccerbotUid, list(range(0, 18, 1)))
        joints_pos = np.array([state[0] for state in joint_states], dtype=np.float32)
        start_pos = np.array([0, 0, self.STANDING_HEIGHT], dtype=np.float32)
        observation = np.concatenate((joints_pos, imu, start_pos))

        #pb.resetSimulation()

        # pb.configureDebugVisualizer(pb.COV_ENABLE_RENDERING, 1)
        """
        From core.py in gym:
        Returns: 
            observation (object): the initial observation.
        """
        return observation

    def render(self, mode='human'):
        if mode == "human":
            self._renders = True
        if mode != "rgb_array":
            return np.array([])
        base_pos, orn = self._p.getBasePositionAndOrientation(self.soccerbotUid)
        base_pos = np.asarray(base_pos)
        # TODO tune parameters
        # track the position
        base_pos[1] += 0.3
        rpy = self._p.getEulerFromQuaternion(orn)  # rpy, in radians
        rpy = 180 / np.pi * np.asarray(rpy)  # convert rpy in degrees

        self._cam_dist = 3
        self._cam_pitch = 0.3
        self._cam_yaw = 0
        if not (self._p is None):
            view_matrix = self._p.computeViewMatrixFromYawPitchRoll(
                cameraTargetPosition=base_pos,
                distance=self._cam_dist,
                yaw=self._cam_yaw,
                pitch=self._cam_pitch,
                roll=0,
                upAxisIndex=1)
            proj_matrix = self._p.computeProjectionMatrixFOV(fov=60,
                                                             aspect=float(self._render_width) / self._render_height,
                                                             nearVal=0.1,
                                                             farVal=100.0)
            (_, _, px, _, _) = self._p.getCameraImage(
                width=self._render_width,
                height=self._render_height,
                renderer=self._p.ER_BULLET_HARDWARE_OPENGL,
                viewMatrix=view_matrix,
                projectionMatrix=proj_matrix)
            # self._p.resetDebugVisualizerCamera(
            #   cameraDistance=2 * self._cam_dist,
            #   cameraYaw=self._cam_yaw,
            #   cameraPitch=self._cam_pitch,
            #   cameraTargetPosition=base_pos
            # )
        else:
            px = np.array([[[255, 255, 255, 255]] * self._render_width] * self._render_height, dtype=np.uint8)
        rgb_array = np.array(px, dtype=np.uint8)
        rgb_array = np.reshape(np.array(px), (self._render_height, self._render_width, -1))
        rgb_array = rgb_array[:, :, :3]
        return rgb_array

    def close(self):
        if self._physics_client_id >= 0:
            self._p.disconnect()
        self._physics_client_id = -1
