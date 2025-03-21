import unittest
from unittest.mock import MagicMock, patch
from actors.player_only_functions.admin import command_help, command_ranks
import os
class TestAdminCommands(unittest.TestCase):

    @patch('os.listdir', return_value=['command1.txt', 'command2.txt'])
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='help content')
    def test_command_help_logic(self, mock_open, mock_listdir):
        mock_self = MagicMock()
        mock_self.sendLine = MagicMock()

        # Test with empty line
        command_help(mock_self, '')
        mock_self.sendLine.assert_called_once_with('@redNo aaacommand found, here are all commands you can use help on@normal\ncommand1\ncommand2\n')

        # Test with specific command
        mock_self.sendLine.reset_mock()
        command_help(mock_self, 'command1')
        mock_self.sendLine.assert_called_once_with('help content')

    def test_command_help_with_actual_data(self):
        mock_self = MagicMock()
        mock_self.sendLine = MagicMock()

        # Test with empty line
        command_help(mock_self, '')
        files = os.listdir('help')
        files = [f.replace('.txt', '') for f in files]
        expected_output = '@redNo command found, here are all commands you can use help on@normal\n' + '\n'.join(files) + '\n'
        mock_self.sendLine.assert_called_once_with(expected_output)

        # Test with specific command for each file
        for file in files:
            mock_self.sendLine.reset_mock()
            command_help(mock_self, file)
            with open(f'help/{file}.txt', "r") as f:
                content = f.read()
                content = content.replace(' "', ' @yellow"')
                content = content.replace('" ', '"@normal ')
            mock_self.sendLine.assert_called_once_with(content)

    def test_command_ranks(self):
        mock_self = MagicMock()
        mock_self.sendLine = MagicMock()
        mock_self.factory.ranks = [
            {'lvl': 10, 'name': 'Player1', 'exp': 1000, 'date_of_last_login': 1617184800, 'time_in_game': 3600},
            {'lvl': 20, 'name': 'Player2', 'exp': 2000, 'date_of_last_login': 1617184800, 'time_in_game': 7200}
        ]

        command_ranks(mock_self, '')
        mock_self.sendLine.assert_called_once()
        output = mock_self.sendLine.call_args[0][0]
        self.assertIn('Rank', output)
        self.assertIn('Level', output)
        self.assertIn('Name', output)
        self.assertIn('EXP', output)
        self.assertIn('Last Login', output)
        self.assertIn('In game time', output)
        self.assertIn('Player1', output)
        self.assertIn('Player2', output)

if __name__ == '__main__':
    unittest.main()