#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
import time

class ScaraSimpleController(Node):
    def __init__(self):
        super().__init__('scara_simple_controller')
        
        # 1. PUBLICADORES (Conectados a tu Puente gz_bridge.yaml)
        self.pub1 = self.create_publisher(Float64, '/joint1_cmd', 10)
        self.pub2 = self.create_publisher(Float64, '/joint2_cmd', 10)
        self.pub3 = self.create_publisher(Float64, '/joint3_cmd', 10)
        
        # ---------------------------------------------------------
        # 2. DATOS VALIDADOS EN MATLAB (Copiados de tu Live Script)
        # ---------------------------------------------------------
        self.tf = 8.0  # Tiempo total de la trayectoria
        
        # Ángulos Iniciales [J1, J2, J3] (Radianes)
        self.q_init  = [1.49214, 0.96039, -3.23793]

        # Ángulos Finales [J1, J2, J3] (Radianes)
        self.q_final = [-0.53175, 0.96039, 0.35675]
        # ---------------------------------------------------------

        # Configuración del ciclo de control (100 Hz = 0.01s)
        self.dt = 0.01
        self.timer = self.create_timer(self.dt, self.control_loop)
        self.start_time = None
        
        self.get_logger().info(' Nodo listo. Esperando para iniciar trayectoria...')
        self.get_logger().info(f'   Tiempo estimado: {self.tf} segundos')

    def polinomio_quinto(self, t, q0, qf, tf):
        """Genera el perfil suave de posición (Misma matemática que MATLAB)"""
        # Límites de seguridad
        if t <= 0: return q0
        if t >= tf: return qf
        
        # Ecuación del Polinomio de 5to Grado
        tau = t / tf
        poly = 10 * tau**3 - 15 * tau**4 + 6 * tau**5
        return q0 + poly * (qf - q0)

    def control_loop(self):
        # Iniciar el reloj interno en la primera iteración
        if self.start_time is None:
            self.start_time = self.get_clock().now().nanoseconds / 1e9
        
        # Calcular tiempo transcurrido
        current_real_time = self.get_clock().now().nanoseconds / 1e9
        t = current_real_time - self.start_time
        
        # Verificar si terminó la trayectoria (damos 1 seg extra de margen)
        if t > self.tf + 1.0:
            self.get_logger().info(' Trayectoria finalizada con éxito.')
            # Opcional: Detener el nodo o dejarlo manteniendo posición
            self.timer.cancel() # Deja de publicar
            return

        # 3. CÁLCULO DE POSICIÓN INSTANTÁNEA
        p1 = self.polinomio_quinto(t, self.q_init[0], self.q_final[0], self.tf)
        p2 = self.polinomio_quinto(t, self.q_init[1], self.q_final[1], self.tf)
        p3 = self.polinomio_quinto(t, self.q_init[2], self.q_final[2], self.tf)
        
        # 4. ENVIAR A GAZEBO
        self.pub1.publish(Float64(data=p1))
        self.pub2.publish(Float64(data=p2))
        self.pub3.publish(Float64(data=p3))

def main(args=None):
    rclpy.init(args=args)
    node = ScaraSimpleController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()