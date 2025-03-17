import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from tempfile import TemporaryDirectory

from mopp.modules.utils import (
    check_folder_nonexistent,
    create_folder_without_clear,
    create_folder,
    clear_folder,
    pool_processes,
)

class TestUtils(unittest.TestCase):

    def test_check_folder_nonexistent(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            check_folder_nonexistent(temp_path / "nonexistent_folder")

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            # Should raise an exception
            with self.assertRaises(Exception) as context:
                check_folder_nonexistent(temp_path)
            self.assertTrue("Output directory already exists." in str(context.exception))

    def test_create_folder_without_clear(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            new_folder = temp_path / "new_folder"
            create_folder_without_clear(new_folder)
            self.assertTrue(new_folder.exists() and new_folder.is_dir())

            # Test when the folder already exists
            create_folder_without_clear(new_folder)
            self.assertTrue(new_folder.exists() and new_folder.is_dir())

    def test_create_folder(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            new_folder = temp_path / "new_folder"
            create_folder(new_folder)
            self.assertTrue(new_folder.exists() and new_folder.is_dir())

            # Test when the folder already exists
            (new_folder / "test_file.txt").touch()
            create_folder(new_folder)
            self.assertTrue(new_folder.exists() and new_folder.is_dir())
            self.assertEqual(len(list(new_folder.iterdir())), 0)  # Folder should be cleared

    def test_clear_folder(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            test_folder = temp_path / "test_folder"
            test_folder.mkdir()
            (test_folder / "file1.txt").touch()
            (test_folder / "file2.txt").touch()
            subfolder = test_folder / "subfolder"
            subfolder.mkdir()
            (subfolder / "file3.txt").touch()

            
            clear_folder(test_folder)
            self.assertTrue(test_folder.exists() and test_folder.is_dir())
            self.assertEqual(len(list(test_folder.iterdir())), 0) 

    @patch('mopp.modules.utils.Pool')
    def test_pool_processes(self, mock_pool):
        
        mock_pool_instance = MagicMock()
        mock_pool.return_value.__enter__.return_value = mock_pool_instance

        
        def test_func(x):
            return x * 2

        function_list = [
            (test_func, [1, 2, 3]),
            (test_func, [4, 5, 6]),
        ]

        
        pool_processes(2, function_list)

        
        mock_pool.assert_called_once_with(processes=2)

        
        mock_pool_instance.map_async.assert_any_call(test_func, [1, 2, 3])
        mock_pool_instance.map_async.assert_any_call(test_func, [4, 5, 6])

      
        mock_pool_instance.close.assert_called_once()
        mock_pool_instance.join.assert_called_once()


if __name__ == "__main__":
    unittest.main()
