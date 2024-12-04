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
