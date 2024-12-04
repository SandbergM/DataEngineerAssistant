def read_data(file_name):
    with open(f"{file_name}.txt", 'r') as file:
        content = file.read()
        data = content.split('\n')
        return data

def is_diagonal(data, idx, jdx):

    cords = [
        [
            [idx, idx-1, idx-2, idx-3],
            [jdx, jdx-1, jdx-2, jdx-3]
        ],
        [
            [idx, idx-1, idx-2, idx-3],
            [jdx, jdx+1, jdx+2, jdx+3]
        ],
    ]

    ans = 0
    for cord in cords:

        conditions = [
            min(cord[0]) >= 0,
            min(cord[1]) >= 0,
            max(cord[0]) < len(data),
            max(cord[1]) < len(data[idx])
        ]

        if all(conditions):
            s = "".join([
                data[cord[0][0]][cord[1][0]],
                data[cord[0][1]][cord[1][1]],
                data[cord[0][2]][cord[1][2]],
                data[cord[0][3]][cord[1][3]]
            ])

            if "XMAS" in [s, s[::-1]]:
                ans +=1
    return ans


def is_horizontal(data, idx, jdx):
    
        cords_a = [idx, idx, idx, idx]
        cords_b = [jdx, jdx-1, jdx-2, jdx-3]
    
        ans = 0
    
        if jdx-3 >= 0:
            s = "".join([
                data[cords_a[0]][cords_b[0]],
                data[cords_a[1]][cords_b[1]],
                data[cords_a[2]][cords_b[2]],
                data[cords_a[3]][cords_b[3]]
            ])
    
            if "XMAS" in [s, s[::-1]]:
                ans +=1
    
        return ans


def is_vertical(data, idx, jdx):
        
    cords_a = [idx, idx-1, idx-2, idx-3]
    cords_b = [jdx, jdx, jdx, jdx]

    ans = 0

    if idx-3 >= 0:
        s = "".join([
            data[cords_a[0]][cords_b[0]],
            data[cords_a[1]][cords_b[1]],
            data[cords_a[2]][cords_b[2]],
            data[cords_a[3]][cords_b[3]]
        ])

        if "XMAS" in [s, s[::-1]]:
            ans +=1

    return ans


def part_2(data):

    ans = 0

    def safe_read(data, idx, jdx):
        try:
            return data[idx][jdx]
        except:
            return ""

    for idx in range(len(data)):
        for jdx in range(len(data[idx])):
            if data[idx][jdx] == "A":

                cross_a = "".join([
                    safe_read(data, idx-1, jdx-1),
                    "A",
                    safe_read(data, idx+1, jdx+1),
                ])

                cross_b = "".join([
                    safe_read(data, idx-1, jdx+1),
                    "A",
                    safe_read(data, idx+1, jdx-1),
                ])

                ans += all([ cross_a in ["MAS", "SAM"], cross_b in ["MAS", "SAM"] ])

    return ans


print("Example 2 : ", part_2(read_data("example")))
print("Part 2 : ", part_2(read_data("data")))
