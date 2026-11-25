import math

class Robot3DOF:
    def __init__(self, l1=120.0, l2=90.0, l3=60.0,
                 theta1=math.radians(60.0), theta2=math.radians(-25.0), theta3=0.0,
                 base=(0.0, 0.0), phi_target=0.0):
        self.base = base
        self.l1 = l1
        self.l2 = l2
        self.l3 = l3
        self.theta1 = theta1
        self.theta2 = theta2
        self.theta3 = theta3
        self.phi_target = phi_target
        self.energy = 0.0
        self.picked = False
        self.held_object = False

    def forward(self):
        x0, y0 = self.base
        x1 = x0 + self.l1 * math.cos(self.theta1)
        y1 = y0 - self.l1 * math.sin(self.theta1)
        x2 = x1 + self.l2 * math.cos(self.theta1 + self.theta2)
        y2 = y1 - self.l2 * math.sin(self.theta1 + self.theta2)
        x3 = x2 + self.l3 * math.cos(self.theta1 + self.theta2 + self.theta3)
        y3 = y2 - self.l3 * math.sin(self.theta1 + self.theta2 + self.theta3)
        return (x0, y0), (x1, y1), (x2, y2), (x3, y3)

    def ik_solve(self, target):
        # target: (x,y) relative to base
        x, y = target
        L1, L2, L3 = self.l1, self.l2, self.l3
        d = math.hypot(x, y)
        if d > (L1 + L2 + L3) or d < abs(L1 - L2 - L3):
            return None, None, None
        # 2DOF solve for theta1, theta2 (elbow-down)
        cos2 = (x*x + y*y - L1*L1 - L2*L2) / (2 * L1 * L2)
        cos2 = max(-1.0, min(1.0, cos2))
        sin2 = math.sqrt(max(0.0, 1.0 - cos2*cos2))
        theta2 = math.atan2(sin2, cos2)
        k1 = L1 + L2 * cos2
        k2 = L2 * sin2
        theta1 = math.atan2(y, x) - math.atan2(k2, k1)
        # 마지막 관절(theta3)으로 end-effector 방향(phi_target) 맞춤
        theta3 = self.phi_target - (theta1 + theta2)
        return theta1, theta2, theta3

    def set_angles(self, t1, t2, t3):
        delta1 = abs(t1 - self.theta1)
        delta2 = abs(t2 - self.theta2)
        delta3 = abs(t3 - self.theta3)
        self.energy += (delta1 + delta2 + delta3) * 2.0
        self.theta1 = t1
        self.theta2 = t2
        self.theta3 = t3

    def reset(self):
        self.theta1 = math.radians(60.0)
        self.theta2 = math.radians(-25.0)
        self.theta3 = 0.0
        self.energy = 0.0
        self.picked = False
        self.held_object = False
        self.phi_target = 0.0
