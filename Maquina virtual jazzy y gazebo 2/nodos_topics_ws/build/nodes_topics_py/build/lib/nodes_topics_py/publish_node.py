#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_msgs.msg import Int64
 

class NumberPub(Node):
  def __init__(self):
    super().__init__("publish_node")

    self.number_ = 2
    self.publihser_ = self.create_publisher(Int64,"publish_topic", 1)
    self.timer = self.create_timer(1.0,self.publis_number)
    self.get_logger().info("Nodo publicador activo" )
 

  def subcallback(self):
    msg = Int64()
    msg.data = self.number_
    self.publihser_.publish(msg)
    

def main(args=None):
  rclpy.init(args=args)
  node = NumberPub()
  rclpy.spin(node)
  rclpy.shutdown()

if __name__ == '__main__':
  main()
  
