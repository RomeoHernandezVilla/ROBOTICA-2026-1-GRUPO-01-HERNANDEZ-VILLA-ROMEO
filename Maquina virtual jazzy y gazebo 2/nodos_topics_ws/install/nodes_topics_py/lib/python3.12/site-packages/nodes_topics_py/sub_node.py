#!usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_msgs.msg import Int32, Float64



class SubNode(Node):
  def __init__(self ):
    super().__init__("node_sub")
    self.mensaje_ = 0
    self.subcriber_ = self.create_subscription(Int32,"publish_topic",self.sub_callbck,10)
    self.vel_rad_motor_ = self.create_publisher(Float64,"rad_vel_topic",10)
    self.get_logger().info("Nodo subcriptor activo")

  def sub_callbck(self,msg):
    self.mensaje_ += msg.data
    # self.get_logger().info("El mensaje es " + str(self.mensaje_))
    self.new_msg_ = Float64()
    self.new_msg_.data = self.mensaje_*1.5
    self.vel_rad_motor_.publish(self.new_msg_)

def main(args=None):
  rclpy.init(args=args)
  node = SubNode()
  rclpy.spin(node)
  rclpy.shutdown()

if __name__ == "__main__":
  main()
  