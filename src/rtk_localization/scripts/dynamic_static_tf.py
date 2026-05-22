#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
import sys

class DynamicStaticTF(Node):
    def __init__(self):
        super().__init__('dynamic_static_tf')
        # 过滤 ROS 2 自动添加的参数
        raw_args = sys.argv[1:]
        clean_args = []
        skip_next = False
        for i, arg in enumerate(raw_args):
            if skip_next:
                skip_next = False
                continue
            if arg.startswith('--ros-args') or arg == '--ros-args':
                continue
            if arg.startswith('-r') or arg == '-r':
                skip_next = True
                continue
            if arg.startswith('__node:=') or arg.startswith('__log:='):
                continue
            clean_args.append(arg)
        
        if len(clean_args) != 8:
            self.get_logger().error(f"Expected 8 arguments, got {len(clean_args)}: {clean_args}")
            self.get_logger().error("Usage: x y z roll pitch yaw parent child")
            raise SystemExit(1)
        
        self.x, self.y, self.z = map(float, clean_args[0:3])
        self.roll, self.pitch, self.yaw = map(float, clean_args[3:6])
        self.parent = clean_args[6]
        self.child = clean_args[7]
        
        self.get_logger().info(f"Publishing dynamic TF: {self.parent} -> {self.child} (x={self.x}, y={self.y}, z={self.z})")
        self.br = TransformBroadcaster(self)  # 改用 TransformBroadcaster
        self.timer = self.create_timer(0.02, self.publish)  # 每0.02秒发布一次

    def publish(self):
        t = TransformStamped()
        # 关键：使用当前时间，而不是静态0
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = self.parent
        t.child_frame_id = self.child
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = self.z
        # 假设无旋转
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0
        self.br.sendTransform(t)
        # 可选：每隔一段时间打印一次，避免日志过多
        # self.get_logger().debug(f"Sent TF {self.parent}->{self.child} at {t.header.stamp}")

def main(args=None):
    rclpy.init(args=args)
    node = DynamicStaticTF()
    rclpy.spin(node)

if __name__ == '__main__':
    main()