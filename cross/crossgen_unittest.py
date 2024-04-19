import unittest
from crossgen import CrossGen

class TestCrosswordMethods(unittest.TestCase):
    def test_init(self):
        """Test that init generates list of words correctly
        - same as testing generate_dicts"""
        cg = CrossGen(3) # yes, maybe it should CrossGen(2) and (4) as well, but that's a lot
        # test that the dictionary contains all words when accessed through the amount of substring letters
        self.assertTrue(cg.allwords[1]['t']['h']['o'] == ['author', 'method', 'those', 'though'])
        self.assertTrue(cg.allwords[1]['y']['i']['e'] == ['yield'])
        self.assertTrue(cg.allwords[0] == 3)
    def test_get_words(self):
        cg = CrossGen(3)
        # test that get_words is working the same as accessing the dictionary letter by letter
        self.assertTrue(cg.allwords[1]['t']['h']['o'] == cg.get_words('tho'))

    def test_generate_cross(self):
        """Also tests __generate_cross"""
        cg = CrossGen(3)
        [down, across] = cg.generate_cross()

        # test that the substring really is in the word
        # test that each word in the 'down' and the 'across' are in the dictionary
        for word, substr in down:
            self.assertTrue(substr in word)
            self.assertTrue(word in cg.allwords[1][word[0]][word[1]][word[2]])
        for word, substr in across:
            self.assertTrue(substr in word)
            self.assertTrue(word in cg.allwords[1][word[0]][word[1]][word[2]])
    
    def test_to_str_array(self):
        """Test the conversion of crossword to string array"""
        cg = CrossGen(3)
        test_case = [[('civil', 'civ'), ('sugar', 'uga'), ('shrug', 'shr')], [('focus', 'cus'), ('flight', 'igh'), ('vary', 'var')]]
        # (x spacing, y spacing, number of words in each row/column, result line by line)
        desired_result = (1, 2, 3, ["_ff_", "_ol_", "_civil", "sugar", "_shrug", "__ty"])
        self.assertTrue(cg.to_str_array(test_case) == desired_result)

    # how to test the 'get hint' function? that it just returns anything at all?

    # generate_puzzle is just generate_cross -> to_str_array -> hints

if __name__ == '__main__':
    unittest.main()