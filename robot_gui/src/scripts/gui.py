#!/usr/bin/env python3
import math
import rospy
from geometry_msgs.msg import Twist, PoseStamped
from PyQt5 import QtWidgets
from tf.transformations import quaternion_from_euler


class RobotGUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Otonom Robot Kontrol Paneli :)")

        # Publishers
        self.cmd_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
        self.goal_pub = rospy.Publisher("/move_base_simple/goal", PoseStamped, queue_size=10)

        # --- UI ---
        layout = QtWidgets.QVBoxLayout()

        # =========================
        # Goal inputs
        # =========================
        goal_group = QtWidgets.QGroupBox("Hedef Gönder (map frame)")
        g = QtWidgets.QGridLayout()

        self.x_in = QtWidgets.QDoubleSpinBox()
        self.x_in.setRange(-1000, 1000)
        self.x_in.setDecimals(3)

        self.y_in = QtWidgets.QDoubleSpinBox()
        self.y_in.setRange(-1000, 1000)
        self.y_in.setDecimals(3)

        self.yaw_in = QtWidgets.QDoubleSpinBox()
        self.yaw_in.setRange(-180, 180)
        self.yaw_in.setDecimals(1)

        g.addWidget(QtWidgets.QLabel("X (m):"), 0, 0)
        g.addWidget(self.x_in, 0, 1)

        g.addWidget(QtWidgets.QLabel("Y (m):"), 1, 0)
        g.addWidget(self.y_in, 1, 1)

        g.addWidget(QtWidgets.QLabel("Yaw (deg):"), 2, 0)
        g.addWidget(self.yaw_in, 2, 1)

        send_goal_btn = QtWidgets.QPushButton("Hedefi Gönder")
        send_goal_btn.clicked.connect(self.send_goal)
        g.addWidget(send_goal_btn, 3, 0, 1, 2)

        goal_group.setLayout(g)
        layout.addWidget(goal_group)

        # =========================
        # Otonom hız ayarı
        # =========================
        auto_group = QtWidgets.QGroupBox("Otonom Hız Ayarı (move_base)")
        a = QtWidgets.QGridLayout()

        self.auto_lin = QtWidgets.QDoubleSpinBox()
        self.auto_lin.setRange(0.01, 2.0)
        self.auto_lin.setSingleStep(0.05)
        self.auto_lin.setValue(0.20)

        self.auto_ang = QtWidgets.QDoubleSpinBox()
        self.auto_ang.setRange(0.01, 4.0)
        self.auto_ang.setSingleStep(0.1)
        self.auto_ang.setValue(0.80)

        self.status_lbl = QtWidgets.QLabel("Durum: Hazır")

        btn_apply_auto = QtWidgets.QPushButton("Hızı Uygula")
        btn_apply_auto.clicked.connect(self.set_autonomous_speed)

        a.addWidget(QtWidgets.QLabel("Otonom lineer hız (m/s):"), 0, 0)
        a.addWidget(self.auto_lin, 0, 1)

        a.addWidget(QtWidgets.QLabel("Otonom açısal hız (rad/s):"), 1, 0)
        a.addWidget(self.auto_ang, 1, 1)

        a.addWidget(btn_apply_auto, 2, 0, 1, 2)
        a.addWidget(self.status_lbl, 3, 0, 1, 2)

        auto_group.setLayout(a)
        layout.addWidget(auto_group)

        # =========================
        # Manual controls
        # =========================
        teleop_group = QtWidgets.QGroupBox("Manuel Kontrol (/cmd_vel)")
        t = QtWidgets.QGridLayout()

        self.v_lin = QtWidgets.QDoubleSpinBox()
        self.v_lin.setRange(0.0, 2.0)
        self.v_lin.setSingleStep(0.05)
        self.v_lin.setValue(0.2)

        self.v_ang = QtWidgets.QDoubleSpinBox()
        self.v_ang.setRange(0.0, 4.0)
        self.v_ang.setSingleStep(0.1)
        self.v_ang.setValue(0.8)

        t.addWidget(QtWidgets.QLabel("Lineer hız (m/s):"), 0, 0)
        t.addWidget(self.v_lin, 0, 1)

        t.addWidget(QtWidgets.QLabel("Açısal hız (rad/s):"), 1, 0)
        t.addWidget(self.v_ang, 1, 1)

        btn_fwd = QtWidgets.QPushButton("İleri")
        btn_back = QtWidgets.QPushButton("Geri")
        btn_left = QtWidgets.QPushButton("Sol")
        btn_right = QtWidgets.QPushButton("Sağ")
        btn_stop = QtWidgets.QPushButton("DUR")

        btn_fwd.pressed.connect(lambda: self.publish_cmd(self.v_lin.value(), 0.0))
        btn_back.pressed.connect(lambda: self.publish_cmd(-self.v_lin.value(), 0.0))
        btn_left.pressed.connect(lambda: self.publish_cmd(0.0, self.v_ang.value()))
        btn_right.pressed.connect(lambda: self.publish_cmd(0.0, -self.v_ang.value()))
        btn_stop.clicked.connect(lambda: self.publish_cmd(0.0, 0.0))

        t.addWidget(btn_fwd, 2, 1)
        t.addWidget(btn_left, 3, 0)
        t.addWidget(btn_stop, 3, 1)
        t.addWidget(btn_right, 3, 2)
        t.addWidget(btn_back, 4, 1)

        teleop_group.setLayout(t)
        layout.addWidget(teleop_group)

        self.setLayout(layout)

        # Başlangıçta otonom hız parametrelerini yaz
        self.set_autonomous_speed()

    def set_autonomous_speed(self):
        lin = self.auto_lin.value()
        ang = self.auto_ang.value()

        # DWAPlannerROS için
        rospy.set_param("/move_base/DWAPlannerROS/max_vel_x", lin)
        rospy.set_param("/move_base/DWAPlannerROS/max_rot_vel", ang)
        rospy.set_param("/move_base/DWAPlannerROS/min_vel_x", 0.0)

        # TrajectoryPlannerROS için
        rospy.set_param("/move_base/TrajectoryPlannerROS/max_vel_x", lin)
        rospy.set_param("/move_base/TrajectoryPlannerROS/max_vel_theta", ang)
        rospy.set_param("/move_base/TrajectoryPlannerROS/min_vel_x", 0.0)

        msg = f"Durum: Otonom hız uygulandı | Lineer={lin:.2f} m/s, Açısal={ang:.2f} rad/s"
        self.status_lbl.setText(msg)
        rospy.loginfo(msg)

    def send_goal(self):
        x = self.x_in.value()
        y = self.y_in.value()
        yaw_deg = self.yaw_in.value()
        yaw = math.radians(yaw_deg)

        # Hedef göndermeden önce seçili otonom hızı uygula
        self.set_autonomous_speed()

        qx, qy, qz, qw = quaternion_from_euler(0.0, 0.0, yaw)

        goal = PoseStamped()
        goal.header.stamp = rospy.Time.now()
        goal.header.frame_id = "map"
        goal.pose.position.x = x
        goal.pose.position.y = y
        goal.pose.position.z = 0.0
        goal.pose.orientation.x = qx
        goal.pose.orientation.y = qy
        goal.pose.orientation.z = qz
        goal.pose.orientation.w = qw

        rospy.loginfo(f"[GUI] goal connections: {self.goal_pub.get_num_connections()}")
        self.goal_pub.publish(goal)
        rospy.sleep(0.1)
        self.goal_pub.publish(goal)

        rospy.loginfo(
            f"[GUI] Goal sent: x={x:.3f}, y={y:.3f}, yaw={yaw_deg:.1f} deg | "
            f"auto_lin={self.auto_lin.value():.2f}, auto_ang={self.auto_ang.value():.2f}"
        )

        self.status_lbl.setText(
            f"Durum: Hedef gönderildi | X={x:.2f}, Y={y:.2f}, Yaw={yaw_deg:.1f}"
        )

    def publish_cmd(self, lin, ang):
        msg = Twist()
        msg.linear.x = lin
        msg.angular.z = ang
        self.cmd_pub.publish(msg)


def main():
    rospy.init_node("robot_gui", anonymous=True)
    app = QtWidgets.QApplication([])
    w = RobotGUI()
    w.show()
    app.exec_()


if __name__ == "__main__":
    main()
