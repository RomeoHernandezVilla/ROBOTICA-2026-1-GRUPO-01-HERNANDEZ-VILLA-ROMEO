import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
import time
import math

class ScaraIK(Node):
    def __init__(self):
        super().__init__('scara_ik_node')
        
        # Publicadores para los 3 motores
        self.pub_j1 = self.create_publisher(Float64, '/joint1/cmd_pos', 10)
        self.pub_j2 = self.create_publisher(Float64, '/joint2/cmd_pos', 10)
        self.pub_j3 = self.create_publisher(Float64, '/joint3/cmd_pos', 10)
        
        # --- DIMENSIONES REALES DEL ROBOT (Según tu URDF) ---
        self.L1 = 0.45  # Longitud del Link 1
        self.L2 = 0.45  # Longitud del Link 2

        self.get_logger().info(f'¡IK lista! Longitudes: L1={self.L1}, L2={self.L2}')

    def publish_joints(self, q1, q2, q3):
        """Publica los ángulos en los topics"""
        msg1 = Float64(); msg1.data = float(q1)
        msg2 = Float64(); msg2.data = float(q2)
        msg3 = Float64(); msg3.data = float(q3)
        
        self.pub_j1.publish(msg1)
        self.pub_j2.publish(msg2)
        self.pub_j3.publish(msg3)

    def inverse_kinematics(self, x, y):
        """
        Calcula la Cinemática Inversa (IK) para un brazo plano de 2 eslabones.
        Entrada: Coordenadas (x, y) deseadas.
        Salida: Ángulos (q1, q2) o (None, None) si no alcanza.
        """
        try:
            # 1. Teorema de cosenos para encontrar el ángulo del codo (q2)
            dist_sq = x**2 + y**2
            
            # Ley de cosenos: c^2 = a^2 + b^2 - 2ab*cos(C)
            # Despejando el coseno del ángulo 2:
            cos_q2 = (dist_sq - self.L1**2 - self.L2**2) / (2 * self.L1 * self.L2)
            
            # Verificar si el punto es alcanzable
            if cos_q2 > 1.0 or cos_q2 < -1.0:
                return None, None

            # Seno del ángulo 2 (+ para configuración codo abajo)
            sin_q2 = math.sqrt(1 - cos_q2**2)
            
            q2 = math.atan2(sin_q2, cos_q2)

            # 2. Calcular ángulo de la base (q1)
            k1 = self.L1 + self.L2 * cos_q2
            k2 = self.L2 * sin_q2
            q1 = math.atan2(y, x) - math.atan2(k2, k1)

            return q1, q2

        except ValueError:
            return None, None

    def draw_circle(self):
        """Genera puntos de un círculo y mueve el robot"""
        # Configuración del círculo
        center_x = 0.5   # Centro del círculo en X
        center_y = 0.0   # Centro del círculo en Y
        radius = 0.15    # Radio del círculo (15 cm)
        
        steps = 300      # Suavidad (más pasos = más lento pero más suave)
        
        for i in range(steps):
            # Parametrización (0 a 2PI)
            theta = (i / steps) * 2 * math.pi
            
            # Calcular coordenada objetivo
            target_x = center_x + radius * math.cos(theta)
            target_y = center_y + radius * math.sin(theta)
            
            # Calcular ángulos necesarios (IK)
            q1, q2 = self.inverse_kinematics(target_x, target_y)
            
            if q1 is not None:
                # q3 se manda fijo porque es muñeca rotacional
                self.publish_joints(q1, q2, 0.0)
            
            # Pequeña pausa para dar tiempo al PID de actuar
            time.sleep(0.02)

def main(args=None):
    rclpy.init(args=args)
    node = ScaraIK()

    try:
        # Esperar a que todo conecte
        time.sleep(1)
        
        node.get_logger().info('Yendo a la posición inicial...')
        
        # 1. Ir al inicio del círculo
        start_x = 0.5 + 0.15
        start_y = 0.0
        q1, q2 = node.inverse_kinematics(start_x, start_y)
        
        if q1 is not None:
            node.publish_joints(q1, q2, 0.0)
            time.sleep(3) # Esperar a que llegue y estabilice
        
        node.get_logger().info('¡Dibujando!')
        
        # 2. Bucle de dibujo infinito
        while rclpy.ok():
            node.draw_circle()
            
    except KeyboardInterrupt:
        node.get_logger().info('Deteniendo...')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()