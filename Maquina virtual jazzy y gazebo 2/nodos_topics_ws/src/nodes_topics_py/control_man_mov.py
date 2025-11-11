#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from std_msgs.msg import Float64

# Se ha eliminado el import time

class ControlRobot(Node):
    def __init__(self):
        super().__init__("control_robot_node")

        # Configuración de tópicos
        topic_movil = "/cmd_vel"
        topic_joint0="joint0/cmd_pos"
        topic_joint1="joint1/cmd_pos"

        # Creación de Publishers
        self.movil_publisher_ = self.create_publisher(Twist, topic_movil,10)
        self.joint0_publisher_ = self.create_publisher(Float64, topic_joint0,10)
        self.joint1_publisher_ = self.create_publisher(Float64, topic_joint1,10)

        # 🤖 Inicialización de la máquina de estados
        # Usamos esta variable para saber qué rutina ejecutar.
        self.current_step = 0
        
        # El timer se ejecuta cada 2.0 segundos. Este es el tiempo que dura cada rutina.
        self.timer = self.create_timer(2.0, self.control_callback) 
        self.get_logger().info("Nodo de control del robot activo")

    def control_callback(self):
        # Los mensajes se redefinen en cada llamada
        msg_movil = Twist()
        msg_joint0 = Float64()
        msg_joint1 = Float64()
        
        # 🚦 Lógica de la máquina de estados (secuencia de movimientos)
        if self.current_step == 0:
            # Rutina 1: Avanzar recto y mover el joint1 a 1.57 rad
            self.get_logger().info("Paso 1: Ejecutando Rutina 1")
            msg_movil.linear.x = 0.2
            msg_movil.angular.z = 0.0
            msg_joint0.data = 0.0
            msg_joint1.data = 1.57

        elif self.current_step == 1:
            # Rutina 2: Avanzar girando y mover el joint0 a 1.57 rad
            self.get_logger().info("Paso 2: Ejecutando Rutina 2")
            msg_movil.linear.x = 0.2
            msg_movil.angular.z = 0.2
            msg_joint0.data = 1.57
            # Aseguramos que sea un flotante
            msg_joint1.data = 0.0 

        elif self.current_step == 2:
            # Rutina 3: Detener el robot y retornar los joints a 0.0
            self.get_logger().info("Paso 3: Ejecutando Rutina 3 (Parada)")
            msg_movil.linear.x = 0.0
            msg_movil.angular.z = 0.0
            msg_joint0.data = 0.0
            msg_joint1.data = 0.0
        
        else:
            # Estado final: El robot permanece detenido y se detienen las logs de rutina
            if self.current_step == 3:
                 self.get_logger().info("Secuencia de 3 pasos completada. Robot en reposo.")
            
            msg_movil.linear.x = 0.0
            msg_movil.angular.z = 0.0
            msg_joint0.data = 0.0
            msg_joint1.data = 0.0
            
            # Puedes descomentar la siguiente línea si quieres que la rutina se repita:
            # self.current_step = -1 


        # Publicar los mensajes de la rutina actual
        self.movil_publisher_.publish(msg_movil)
        self.joint0_publisher_.publish(msg_joint0)
        self.joint1_publisher_.publish(msg_joint1)

        # ⬆️ Avanzar al siguiente paso de la secuencia
        self.current_step += 1


def main(args=None):
    rclpy.init(args=args)
    node = ControlRobot()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()