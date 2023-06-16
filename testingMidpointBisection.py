from bisect import bisect

years_on_pixels = [75, 106, 138, 169, 200, 232, 263, 295, 326, 357, 389, 420, 452, 483, 514, 546, 577, 609, 640, 672,
                   703, 734, 766, 797, 829, 860, 891]
midpoints = [90.5, 122, 153.5, 184.5, 216, 247.5, 279, 310.5, 341.5, 373, 404.5, 436, 467.5, 498.5,
             530, 561.5, 593, 624.5, 656, 687.5, 718.5, 750, 781.5, 813, 844.5, 875.5]
years = [1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999,
         2000, 2001, 2002, 2003, 2004, 2005, 2006,
         2007, 2008, 2009, 2010, 2011, 2012, 2013,
         2014, 2015, 2016, 2017, 2018]


def find_closest_year(pixel_x):
    i = bisect(midpoints, pixel_x)
    return years[i]


class TestFindClosestYear:

    def test_length_of_years(self):
        assert len(years) == len(years_on_pixels)

    def test_exact_matches(self):
        for i, num in enumerate(years_on_pixels):
            assert find_closest_year(num) == years[i]

    def test_between_matches(self):
        assert find_closest_year(80) == 1992  # between 75 and 106
        assert find_closest_year(135) == 1994  # between 106 and 138

    def test_less_than_smallest(self):
        assert find_closest_year(50) == 1992  # less than 75

    def test_greater_than_largest(self):
        assert find_closest_year(900) == 2018  # greater than 891


TestFindClosestYear().test_length_of_years()
TestFindClosestYear().test_exact_matches()
TestFindClosestYear().test_between_matches()
TestFindClosestYear().test_less_than_smallest()
TestFindClosestYear().test_greater_than_largest()
