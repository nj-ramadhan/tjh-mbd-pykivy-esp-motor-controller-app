import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# data_theta = range(10,171,10)

n = 115
a = 0
data = np.random.uniform(100.0, 200.0, n)
angle = np.arange(0, n, 1)
theta = np.pi * np.deg2rad(angle)

show_theta = np.array([])
show_data = np.array([])

fig = plt.figure()
ax = fig.add_subplot(111, polar=True)
ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)
ax.set_rmax(200)
ax.set_xticklabels([
    r'$day 1$',
    r'$day 2$',
    r'$day 3$',
    r'$day 4$',
    r'$day 5$',
    r'$day 6$',
    r'$day 7$',
    r'$day 8$',
    ])
ax.grid(True)
ax.set_title("Amp Chart", va='bottom')
ax.plot(theta, data, color='r', linewidth=2)

def animate(i):
    global a
    global theta
    global data
    global show_data
    global show_theta
    ax.clear()
    # ax.plot(xs, ys)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_rmax(200)
    ax.set_xticklabels([
        r'$day 1$',
        r'$day 2$',
        r'$day 3$',
        r'$day 4$',
        r'$day 5$',
        r'$day 6$',
        r'$day 7$',
        r'$day 8$',
        ])
    ax.grid(True)
    ax.set_title("Amp Chart", va='bottom')

    ax.plot(theta[:a], data[:a], color='r', linewidth=2)
    a = a + 1

ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.show()