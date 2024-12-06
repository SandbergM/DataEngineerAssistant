def read_data(file_name):
    with open(f'{file_name}.txt') as f:
        return [list(x) for x in f.read().split("\n")]

import time

data = read_data("data")

def run_this_stupid_fucking_puzzle(data):

    steps = {   
        "^" : (-1, 0),
        ">" : (0, 1),
        "v" : (1, 0),
        "<" : (0, -1)
    }

    directions = {
        "^" : ">",
        ">" : "v",
        "v" : "<",
        "<" : "^"
    }

    __idx = max([idx if "^" in data[idx] else 0 for idx in range(len(data))])
    __jdx = data[__idx].index("^")

    direction = data[__idx][__jdx]

    ans = 0

    for i in range(len(data)):

        for j in range(len(data[i])):

            data_copy = read_data("data")

            _direction = direction
            data_copy[i][j] = "O"

            idx = __idx
            jdx = __jdx

            while True:

                _i, _j = idx, jdx

                idx += steps[_direction][0]
                jdx += steps[_direction][1]

                if idx < 0 or idx >= len(data_copy) or jdx < 0 or jdx >= len(data_copy[idx]):
                    break

                if data_copy[idx][jdx] in ["#", "O"]:
                    _direction = directions[_direction]
                    idx, jdx = _i, _j
                    continue

                if data_copy[idx][jdx] == _direction:
                    ans += 1
                    break

                data_copy[idx][jdx] = _direction

    return ans
    
start_time = time.time()
print(run_this_stupid_fucking_puzzle(data))
end_time = time.time()
print(f"Execution time: {(end_time - start_time) * 1000:.2f} ms")
