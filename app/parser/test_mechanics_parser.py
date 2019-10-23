import constants

from parse_garage_language import parse_text, get_next_tokens, get_all_tokens, is_complete, parses, \
    get_specific_tests, delete_specific_test_from_test_category, add_specific_test_to_test_category, \
    get_translation, read_test_mappings, get_rule_text, get_rule, process_rule
from ParserErrors import IncompleteRuleError, IncorrectGrammarError


if __name__ == '__main__':
    input_filename = 'Data/Brake.xlsx'  # sys.argv[1]
    text = get_rule_text(input_filename).upper().replace('\r', ' ').replace('\n', ' ')
    read_test_mappings(input_filename)
    print('parsing text: %s' % text)
    print('%s' % str(constants.read_parser_out_file()))

    print('parsing tokens')
    words = text.split()
    lenw = len(words)
    in_printval = False
    for i, word in enumerate(words):
        if not in_printval:
            if word[0] != '"':
                if i < lenw:
                    new_text = ' '.join(words[:i + 1])
                    print('parsing text %s' % new_text)
                    allowed_tokens = get_next_tokens(new_text)
                    print('\tallowed tokens: %s' % allowed_tokens)
                    if not is_complete(new_text):
                        print('incomplete or incorrect grammar')
                    else:
                        print('parses')

            else:
                in_printval = True
        else:  # in printval
            if word[-1] == '"':
                if i < lenw:
                    new_text = ' '.join(words[:i + 1])
                    print('parsing text in printval %s' % new_text)
                    get_next_tokens(new_text)
                    if not is_complete(new_text):
                        print('incomplete or incorrect grammar')
                    else:
                        print('parses')

                in_printval = False

    print('parsing full text')
    if not is_complete(text):
        print('incomplete or incorrect grammar')
    else:
        print('is complete')

    if not parses(text):
        print('invalid tokens')
    else:
        print('tokens OK')

    print('\n\n--------------\nget_all_tokens')
    print('%s' % get_all_tokens())

    print('\n\n--------------\nget_next_tokens')
    for test_text in ('IF THERE IST', 'IF'):
        print('testing on: %s' % test_text)
        try:
            print('%s' % get_next_tokens(test_text))
        except IncorrectGrammarError:
            print('Incorrect grammar: %s' % test_text)

    print('\n\n--------------\nis_complete')
    test_text = 'IF'
    print('test with incomplete but valid text: %s' % test_text)
    print('%s\n' % is_complete(test_text))

    print('test with complete and valid text: %s' % text)
    print('%s' % is_complete(text))

    print('\n\n--------------\nparses')
    test_text = 'IF THEREH IS'
    print('test with incorrect text: %s' % test_text)
    print('%s' % parses(test_text))

    print('')
    test_text = 'IF THERE IS'
    print('test with correct but incomplete text: %s' % test_text)
    print('%s\n' % parses(test_text))

    print('test with correct and complete text')
    print('%s' % is_complete(text))
    print('Tokens\n%s' % get_all_tokens())

#    print('result from parsing i.e. translation')
#    result = get_translation(text)
#    print('%s' % result)

    print('result from parsing the correct way')
    print('Rule: %s' % process_rule(input_filename))

    print('-------------\n\nget_token_map(None)\n %s' % get_specific_tests(None))
    print('-------------\n\nget_token_map(\'BRAKE_DRUM TEST\')\n %s' %
          get_specific_tests('BRAKE_DRUM TEST'))
    print('-------------\n adding specific test i.ouch/toe-stub to BRAKE_DRUM TEST')
    add_specific_test_to_test_category('i.ouch/toe-stub', 'BRAKE_DRUM TEST')
    test_mappings, test_types, testgroup_mappings = read_test_mappings(input_filename)
    print('--------------\nRule Now:\n%s' % get_rule(text, test_mappings, test_types, testgroup_mappings))
    print('-------------\n deleting specific test i.ouch/toe-stub from BRAKE_DRUM TEST')
    delete_specific_test_from_test_category('i.ouch/toe-stub', 'BRAKE_DRUM TEST')
    print('--------------\nRule Now:\n%s' % get_rule(text, test_mappings, test_types, testgroup_mappings))

