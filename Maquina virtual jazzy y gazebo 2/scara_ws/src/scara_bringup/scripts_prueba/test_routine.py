import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
import time

class ScaraRoutine(Node):
    def __init__(self):
        super().__init__('scara_routine_node')
        
        # 1. Creamos los publicadores para cada articulación
        # Asegúrate de que los nombres de los topics sean EXACTOS a los tuyos
        self.pub_j1 = self.create_publisher(Float64, '/joint1/cmd_pos', 10)
        self.pub_j2 = self.create_publisher(Float64, '/joint2/cmd_pos', 10)
        self.pub_j3 = self.create_publisher(Float64, '/joint3/cmd_pos', 10)

        self.get_logger().info('¡Iniciando rutina de prueba SCARA!')

    def move_robot(self, j1_val, j2_val, j3_val):
        """Función auxiliar para publicar en los 3 motores a la vez"""
        msg1 = Float64()
        msg1.data = float(j1_val)
        
        msg2 = Float64()
        msg2.data = float(j2_val)
        
        msg3 = Float64()
        msg3.data = float(j3_val)

        self.pub_j1.publish(msg1)
        self.pub_j2.publish(msg2)
        self.pub_j3.publish(msg3)
        
        self.get_logger().info(f'Enviando -> J1: {j1_val}, J2: {j2_val}, J3: {j3_val}')

def main(args=None):
    rclpy.init(args=args)
    node = ScaraRoutine()

    # --- LISTA DE POSICIONES A PROBAR ---
    # Formato: [Junta1, Junta2, Junta3 (Prismática)]
    waypoints = [
        [0.0,  0.0,  0.0],   # 1. HOME (Centro)
        [0.5,  0.5,  0.1],   # 2. Movimiento suave derecha
        [1.0,  1.0,  0.2],   # 3. Extensión máxima derecha
        [0.0,  0.0,  0.0],   # 4. Regreso al centro
        [-0.5, -0.5, 0.1],   # 5. Movimiento suave izquierda
        [-1.0, -1.0, 0.2],   # 6. Extensión máxima izquierda
        [1.5, -1.5,  0.0],   # 7. Cruce (J1 derecha, J2 izquierda) - Prueba colisiones
        [0.0,  0.0,  0.0]    # 8. Finalizar en Home
    ]

    try:
        # Damos un segundo para que ROS conecte los nodos
        time.sleep(1)

        for point in waypoints:
            # Extraemos los valores
            val_j1, val_j2, val_j3 = point
            
            # Movemos el robot
            node.move_robot(val_j1, val_j2, val_j3)
            
            # --- TIEMPO DE ESPERA ---
            # Aquí definimos cuánto tiempo esperamos entre movimientos.
            # Es vital para observar si hay oscilaciones al frenar.
            time.sleep(3.0) 

    except KeyboardInterrupt:
        print("\nRutina cancelada por el usuario.")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()