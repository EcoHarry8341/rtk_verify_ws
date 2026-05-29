#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2

class TimeRelayNode(Node):
    def __init__(self):
        super().__init__('pc_time_relay')
        self.sub = self.create_subscription(PointCloud2, '/rslidar_points', self.cloud_cb, 10)
        self.pub = self.create_publisher(PointCloud2, '/rslidar_points_nav', 10)
        self.get_logger().info("Nav2 点云时间戳中继已启动 (/rslidar_points -> /rslidar_points_nav)")

    def cloud_cb(self, msg):
        # 修复：将硬件GPS时间戳替换为系统时间
        msg.header.stamp = self.get_clock().now().to_msg()
        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = TimeRelayNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
