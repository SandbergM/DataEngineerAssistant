from itertools import product
import time


def read_data(file_name):

    with open(f"{file_name}.txt", 'r') as file:
        lines = file.read().split('\n')
        result = []
        for line in lines:
            if line:
                first_value, values = line.split(': ')
                values_list = list(map(int, values.split()))
                result.append((int(first_value), values_list))
        return result

data = read_data('data')
operators = ['+', '*', "||"]

ans = 0

start = time.time()

for idx, tup in enumerate(data):
    res = tup[0]
    nums = tup[1]

    for ops in product(operators, repeat=len(nums) - 1):

        result = nums[0]

        for num, op in zip(nums[1:], ops):

            if op == '+':
                result += num

            elif op == '*':
                result *= num
                
            elif op == "||":
                result = int(f"{result}{num}")

            if result > res:
                break

        if result == res:
            ans += result
            break

end = time.time()
print(ans)
print(f"Time taken: {(end - start) * 1000} ms")
