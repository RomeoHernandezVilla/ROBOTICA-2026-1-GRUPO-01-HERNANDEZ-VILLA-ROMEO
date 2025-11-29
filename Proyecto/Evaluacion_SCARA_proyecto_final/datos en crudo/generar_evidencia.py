import sqlite3
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import JointState
import matplotlib.pyplot as plt
import glob
import sys
import math

# --- CONFIGURACIÓN ---
bag_folder = 'datos_reporte'  # Asegúrate que este sea el nombre de tu carpeta
# ---------------------

# 1. Buscar archivo
db_files = glob.glob(f'{bag_folder}/*.db3')
if not db_files:
    print(f"❌ Error: No encontré .db3 en {bag_folder}")
    sys.exit(1)
db_file = db_files[0]

# 2. Leer datos
print(f"📊 Leyendo {db_file}...")
conn = sqlite3.connect(db_file)
cursor = conn.cursor()
cursor.execute("SELECT timestamp, data FROM messages WHERE topic_id = (SELECT id FROM topics WHERE name = '/joint_states')")

# Listas para datos
times = []
pos = [[], [], []] # J1, J2, J3
vel = [[], [], []] # Velocidades J1, J2, J3
acc = [[], [], []] # Aceleraciones J1, J2, J3 (Se calculan después)

start_t = None

for timestamp, data in cursor.fetchall():
    msg = deserialize_message(data, JointState)
    
    t = timestamp / 1e9
    if start_t is None: start_t = t
    rel_t = t - start_t
    
    if rel_t > 8.5: break # Solo los 8s de interés

    # Verificar que el mensaje tenga datos completos
    if len(msg.position) >= 3 and len(msg.velocity) >= 3:
        times.append(rel_t)
        
        # Posición
        pos[0].append(msg.position[0])
        pos[1].append(msg.position[1])
        pos[2].append(msg.position[2])
        
        # Velocidad
        vel[0].append(msg.velocity[0])
        vel[1].append(msg.velocity[1])
        vel[2].append(msg.velocity[2])

conn.close()

# 3. Calcular Aceleración (Derivada numérica: a = dv/dt)
# Empezamos desde el segundo dato porque necesitamos el anterior para restar
for i in range(1, len(times)):
    dt = times[i] - times[i-1]
    if dt == 0: dt = 0.001 # Evitar división por cero
    
    # Aceleración = (Vel_actual - Vel_anterior) / tiempo
    acc0 = (vel[0][i] - vel[0][i-1]) / dt
    acc1 = (vel[1][i] - vel[1][i-1]) / dt
    acc2 = (vel[2][i] - vel[2][i-1]) / dt
    
    acc[0].append(acc0)
    acc[1].append(acc1)
    acc[2].append(acc2)

# Ajustamos el tiempo para aceleración (tiene 1 dato menos)
times_acc = times[1:]

# 4. Generar las 3 Gráficas

# FIGURA 1: POSICIÓN
plt.figure(figsize=(10, 5))
plt.plot(times, pos[0], 'r', label='Junta 1')
plt.plot(times, pos[1], 'g', label='Junta 2')
plt.plot(times, pos[2], 'b', label='Junta 3')
plt.title('Posición Real (Validación)')
plt.xlabel('Tiempo [s]'); plt.ylabel('Rad'); plt.grid(True); plt.legend()
plt.savefig('real_posicion.png')

# FIGURA 2: VELOCIDAD
plt.figure(figsize=(10, 5))
plt.plot(times, vel[0], 'r', label='Vel J1')
plt.plot(times, vel[1], 'g', label='Vel J2')
plt.plot(times, vel[2], 'b', label='Vel J3')
plt.title('Velocidad Real (Validación)')
plt.xlabel('Tiempo [s]'); plt.ylabel('Rad/s'); plt.grid(True); plt.legend()
plt.savefig('real_velocidad.png')

# FIGURA 3: ACELERACIÓN
plt.figure(figsize=(10, 5))
plt.plot(times_acc, acc[0], 'r', label='Acel J1', alpha=0.6)
plt.plot(times_acc, acc[1], 'g', label='Acel J2', alpha=0.6)
plt.plot(times_acc, acc[2], 'b', label='Acel J3', alpha=0.6)
plt.title('Aceleración Real Calculada')
plt.xlabel('Tiempo [s]'); plt.ylabel('Rad/s²'); plt.grid(True); plt.legend()
plt.savefig('real_aceleracion.png')

print("✅ ¡Listo! Se generaron 3 imágenes: real_posicion.png, real_velocidad.png y real_aceleracion.png")
