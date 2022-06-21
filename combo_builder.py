fast = [1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 18, 20, 24, 30, 32, 36, 40, 45, 48, 60]
medium = [5, 6, 8, 9, 10, 12, 15, 16, 18, 20, 24, 30, 32, 36, 40, 45, 48, 60, 72, 80, 90, 96, 120]
slow = [10, 12, 15, 16, 18, 20, 24, 30, 32, 36, 40, 45, 48, 60, 72, 80, 90, 96, 120, 144, 160, 180, 240]

combos = []
for x in fast:
    for y in medium:
        if y > x:
            for z in slow:
                if z > y:
                    combos.append([x,y,z])


with open("all-drivers.csv", "w") as f:
    for x in combos:
        f.write(f"{x[0]},{x[1]},{x[2]}\n")
