def calculate_midpoints(numbers):
    midpoints = []
    for i in range(len(numbers) - 1):
        midpoint = (numbers[i] + numbers[i + 1]) / 2
        midpoints.append(midpoint)
    return midpoints


class TestMidpoints:
    def test_calculate_midpoints(self):
        numbers = [0, 75, 106, 138, 169, 200, 232, 263, 295, 326, 357, 389, 420, 452, 483, 514, 546, 577, 609, 640, 672,
                   703, 734, 766, 797, 829, 860, 891, 1000]
        ground_truth = [37.5, 90.5, 122, 153.5, 184.5, 216, 247.5, 279, 310.5, 341.5, 373, 404.5, 436, 467.5, 498.5,
                        530, 561.5, 593, 624.5, 656, 687.5, 718.5, 750, 781.5, 813, 844.5, 875.5, 945.5]
        assert (calculate_midpoints(numbers) == ground_truth)


TestMidpoints().test_calculate_midpoints()
