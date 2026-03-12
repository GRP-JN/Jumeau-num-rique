#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import pandas as pd
import math

class CsvToGazebo(Node):
    def __init__(self):
        super().__init__('csv_to_gazebo')
        
        self.publisher_ = self.create_publisher(
            JointTrajectory, 
            '/arm_controller/joint_trajectory', 
            10
        )
        
        try:
            self.df = pd.read_csv(
                "simulated_robot_data.csv",
                sep=',',      # ✅ virgule comme séparateur de colonnes
                decimal='.'   # ✅ point comme séparateur décimal
            )
            self.get_logger().info(f"Colonnes trouvées : {list(self.df.columns)}")
            self.get_logger().info(f"✅ CSV chargé. {len(self.df)} points détectés.")
        except Exception as e:
            self.get_logger().error(f"❌ Erreur lecture CSV : {e}")
            return

        self.TIMER_PERIOD = 0.04  # 40ms
        self.timer = self.create_timer(self.TIMER_PERIOD, self.timer_callback)
        self.index = 0

    def timer_callback(self):
        if self.index >= len(self.df):
            self.get_logger().info("⏹️ Fin de la trajectoire.")
            self.timer.cancel()
            return

        row = self.df.iloc[self.index]

        msg = JointTrajectory()
        # On force le stamp à 0 pour que Gazebo accepte la trajectoire peu importe l'heure
        msg.header.stamp.sec = 0
        msg.header.stamp.nanosec = 0
        msg.joint_names = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']

        point = JointTrajectoryPoint()

        joints_deg = row[['J1', 'J2', 'J3', 'J4', 'J5', 'J6']].values
        point.positions = [math.radians(float(j)) for j in joints_deg]

        # ✅ CORRECTION ICI : Le temps doit être CUMULÉ
        # Point 0 -> 40ms, Point 1 -> 80ms, etc.
        total_nanosec = int((self.index + 1) * self.TIMER_PERIOD * 1e9)
        
        # On sépare en secondes et nanosecondes
        point.time_from_start.sec = int(total_nanosec // 1e9)
        point.time_from_start.nanosec = int(total_nanosec % 1e9)

        msg.points.append(point)
        self.publisher_.publish(msg)

        if self.index % 100 == 0:
            f"📤 Point {self.index}/{len(self.df)} | "
        f"J1:{joints_deg[0]:.1f} J2:{joints_deg[1]:.1f} J3:{joints_deg[2]:.1f} "
        f"J4:{joints_deg[3]:.1f} J5:{joints_deg[4]:.1f} J6:{joints_deg[5]:.1f}"
    
        self.index += 1


def main(args=None):
    rclpy.init(args=args)
    node = CsvToGazebo()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()