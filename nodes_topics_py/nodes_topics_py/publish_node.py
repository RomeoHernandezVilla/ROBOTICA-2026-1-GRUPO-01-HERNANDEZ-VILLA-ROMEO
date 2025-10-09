#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_msgs.msg import Int32
 

class MyPublish(Node):
  def __init__(self):
    super().__init__("publish_node")
    self.number_ = 2
    self.publihser_ = self.create_publisher(Int32,"publish_topic", 10)
    self.get_logger().info("Nodo publicador activo")
    self.create_timer(0.5,self.subcallback)

  def subcallback(self):
    msg = Int32()
    msg.data = self.number_
    self.publihser_.publish(msg)
    

def main(args=None):
  rclpy.init(args=args)
  node = MyPublish()
  rclpy.spin(node)
  rclpy.shutdown()

if __name__ == '__main__':
  main()
  
