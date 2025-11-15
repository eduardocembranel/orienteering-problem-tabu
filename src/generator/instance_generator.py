import random

def generate_instances(rng: int):
    for t_max in range(50, 600, 100):
        n = 300
        max_xy = 2001
        generate_instance(f"cemb_{n}_{t_max}", n, t_max, max_xy, rng)

def generate_instance(instance_name: str, n: int, t_max: int, max_xy: int, rng: int):
    random.seed(rng)
    filename = f"instances/{instance_name}.txt"

    xs = random.sample([round(x, 1) for x in [i * 0.1 for i in range(10, max_xy)]], n)
    ys = random.sample([round(y, 1) for y in [i * 0.1 for i in range(10, max_xy)]], n)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"{t_max} 1\n")

        for i in range(n):
            x = xs[i]
            y = ys[i]

            if i < 2:
                s = 0
            else:
                s = random.choice(range(5, 55, 5))

            f.write(f"{x:.1f} {y:.1f} {s}\n")
