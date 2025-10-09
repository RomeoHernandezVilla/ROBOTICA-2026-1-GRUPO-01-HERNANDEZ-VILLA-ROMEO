#!/usr/bin/env python3

import rclpy
from rclpy.node import Node


class  MyNode(Node):
    def __init__(self):
        super().__init__("mi_nodo")
        self.contador_ = 0
        self.get_logger().info("Bivennidos a ROS 2")
        self.create_timer(1, self.callback_timer)
    
    def callback_timer(self):
        self.contador_ += 1
        self.get_logger().info("Hola " + str(self.contador_))


def main(args=None):
    rclpy.init(args=args)
    node = MyNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__=="__main__":
    main()
    

        
    