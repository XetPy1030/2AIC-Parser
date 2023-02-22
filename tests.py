import os
import unittest

from core.aic import Aic, table_filename


class TestAic(unittest.TestCase):
    def setUp(self) -> None:
        self.aic = Aic()

    def test_download(self):
        self.aic.download()
        self.assertTrue(os.path.exists(table_filename))


if __name__ == '__main__':
    unittest.main()
