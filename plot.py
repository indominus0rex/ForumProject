import matplotlib.pyplot as plt

x_val = []
y_val = []
z_val = []

# 1. Read the data file downloaded from your ESP32
with open("data.txt", "r") as f:
    for line in f:
        parts = line.strip().split(",")
        if len(parts) == 3:
            x_val.append(float(parts[0]))
            y_val.append(float(parts[1]))
            z_val.append(float(parts[2]))

# 2. Create the plot layout
plt.figure(figsize=(10, 5)) # Set graph window size

# 3. Plot all three axes
plt.plot(x_val, label="X-axis (Tilt Left/Right)", color="red")
plt.plot(y_val, label="Y-axis (Tilt Forward/Back)", color="green")
plt.plot(z_val, label="Z-axis (Gravity/Up-Down)", color="blue")

# 4. Add labels, legend, and titles
plt.title("GY-521 Accelerometer Data Log", fontsize=14)
plt.xlabel("Sample Number", fontsize=12)
plt.ylabel("Acceleration (g)", fontsize=12)
plt.grid(True) # Adds a clean grid background
plt.legend()   # Shows the colored labels box

# 5. EXPORT/SAVE THE GRAPH AS AN IMAGE
plt.savefig("sensor_graph.png", dpi=300) # dpi=300 makes it high resolution
print("Graph exported successfully as 'sensor_graph.png'!")

# 6. Show the graph on screen
plt.show()