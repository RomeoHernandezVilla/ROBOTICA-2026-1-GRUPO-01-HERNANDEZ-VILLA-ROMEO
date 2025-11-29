import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64
import time
import math

class ScaraSmooth(Node):
    def __init__(self):
        super().__init__('scara_smooth_node')
        
        # Publicadores
        self.pub_j1 = self.create_publisher(Float64, '/joint1/cmd_pos', 10)
        self.pub_j2 = self.create_publisher(Float64, '/joint2/cmd_pos', 10)
        self.pub_j3 = self.create_publisher(Float64, '/joint3/cmd_pos', 10)
        
        # Guardamos la posición actual del robot (Asumimos que empieza en 0)
        self.current_j1 = 0.0
        self.current_j2 = 0.0
        self.current_j3 = 0.0

        self.get_logger().info('¡Controlador de Trayectorias Suaves listo!')

    def publish_pos(self, j1, j2, j3):
        msg1 = Float64()
        msg1.data = float(j1)
        self.pub_j1.publish(msg1)
        
        msg2 = Float64()
        msg2.data = float(j2)
        self.pub_j2.publish(msg2)
        
        msg3 = Float64()
        msg3.data = float(j3)
        self.pub_j3.publish(msg3)

    def move_smooth(self, target_j1, target_j2, target_j3, duration=3.0):
        """
        Mueve el robot desde donde está hasta el objetivo interpolando suavemente.
        duration: Tiempo en segundos que debe durar el movimiento.
        """
        self.get_logger().info(f'Iniciando movimiento suave hacia: {target_j1}, {target_j2}, {target_j3}')

        # Configuración de la interpolación
        frequency = 50.0  # Hz (50 veces por segundo)
        period = 1.0 / frequency
        steps = int(duration * frequency)

        # Posiciones iniciales (desde donde arranca este movimiento)
        start_j1 = self.current_j1
        start_j2 = self.current_j2
        start_j3 = self.current_j3

        # Diferencia a recorrer
        diff_j1 = target_j1 - start_j1
        diff_j2 = target_j2 - start_j2
        diff_j3 = target_j3 - start_j3

        # BUCLE DE TRAYECTORIA
        for i in range(steps + 1):
            # 't' va de 0.0 a 1.0 a lo largo del bucle
            t = i / float(steps)

            # --- FORMULA MÁGICA: SMOOTH STEP ---
            # Esto crea una curva en forma de S (aceleración suave)
            # Si usáramos solo 't', sería lineal (robótico)
            smooth_t = t * t * (3 - 2 * t)
            # -----------------------------------

            # Calculamos la posición intermedia exacta
            next_j1 = start_j1 + (diff_j1 * smooth_t)
            next_j2 = start_j2 + (diff_j2 * smooth_t)
            next_j3 = start_j3 + (diff_j3 * smooth_t)

            # Publicamos
            self.publish_pos(next_j1, next_j2, next_j3)

            # Esperamos el tiempo del ciclo para mantener la velocidad
            time.sleep(period)

        # Actualizamos nuestra memoria interna
        self.current_j1 = target_j1
        self.current_j2 = target_j2
        self.current_j3 = target_j3
        
        self.get_logger().info('Movimiento finalizado.')

def main(args=None):
    rclpy.init(args=args)
    node = ScaraSmooth()

    # --- RUTINA DE MOVIMIENTOS ---
    try:
        # Esperar conexión
        time.sleep(1)

        # Movimiento 1: Ir a una posición extendida (en 4 segundos)
        node.move_smooth(1.0, 0.8, 0.2, duration=4.0)
        
        time.sleep(1.0) # Pausa breve

        # Movimiento 2: Ir al otro lado (en 3 segundos)
        node.move_smooth(-1.0, -0.8, 0.1, duration=3.0)

        time.sleep(1.0)

        # Movimiento 3: Volver a casa suavemente (en 5 segundos)
        node.move_smooth(0.0, 0.0, 0.0, duration=5.0)

    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()