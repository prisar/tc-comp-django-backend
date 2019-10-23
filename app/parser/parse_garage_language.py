import math
import io
from contextlib import redirect_stderr

import pandas as pd
import ply.lex as lex
import ply.yacc as yacc
import app.parser.constants as constants

from app.parser.ParserErrors import LexError, YaccError, IncompleteRuleError, IncorrectGrammarError
from app.parser.constants import tokens, reserved, ERROR_TEXT, t_COMMA, t_COMP, t_ignore, t_LPAREN, \
    t_MATH_OPER, t_NUM, t_NUM_FOLD, t_NUMNM, t_NUMUM, t_RPAREN

testgroup_mappings = {'AL2': ['A1']}
test_types = {'EEK50'}
test_mappings = {'A1': ['AAM[1]', 'AAM[2]'], 'key': ['key']}


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')  # Check for reserved words
    return t


def t_PRINT_VAL(t):
    r'\"(([_a-zA-Z0-9%\:\/\,\.\-\(\)])+(\s)?)+\"'
    t.value = t.value[1:-1]
    return t


# Error handling rule
def t_error(t):
    t.lexer.skip(1)
    raise LexError(t.value[0], ERROR_TEXT)


def get_message(msg):
    return 'PROPERTY(\'' + get_test_mappings('key', 0) + '\') = "' + msg + '";\n'


def get_tests_from_group(testgroup):
    return testgroup_mappings[testgroup]


def get_test_mappings(key,
                      num=0):
    global test_mappings
    return test_mappings[key][num]
#    return 'AM[1]'


def get_all_test_mappings_for_key(key):
    global test_mappings
    return test_mappings[key]


def get_all_test_types_for_key(key):
    global test_types
    return test_types[key]


def get_codes_for(measurement,
                  wrap_with=None):
    if wrap_with is None:
        wrap_start = 'PROPERTY('
        wrap_end = ')'
    else:
        wrap_start = wrap_with + '(PROPERTY('
        wrap_end = '))'
    codes = []
    for j, (test, test_type) in enumerate(zip(get_all_test_mappings_for_key(measurement),
                                              get_all_test_types_for_key(measurement))):
        codes.append('%s\'p%s*%s\'%s' % (wrap_start, test_type, test, wrap_end))
    return codes


def get_test_for_absence_for_measurement(test_name,
                                         joiner='AND'):
    codes = get_codes_for(test_name)
    s = ['( %s = \'\')\n' % test for test in codes]
    return ('\n%s\n' % joiner).join(s)


def get_average_for(measurement):
    codes = get_codes_for(measurement)
    s = '(%s)' % '+\n'.join(codes)
    codes = get_codes_for(measurement, 'ISNUMBER')
    s2 = '(%s)' % '+\n'.join(codes)
    return '(%s/\n%s)' % (s, s2)


def get_comparator(comp,
                   num_str):
    new_comp = comp
    if num_str.endswith('UM') or num_str.endswith('NM'):
        if '>' in comp:
            new_comp = comp.replace('>', '<')
        elif '<' in comp:
            new_comp = comp.replace('<', '>')
    return new_comp


def get_num_for_string(c_str):
    if c_str.endswith('NM'):
        num = -math.log10(float(c_str[:-2]) / 1000000000.0)
    elif c_str.endswith('UM'):
        num = -math.log10(float(c_str[:-2]) / 1000000.0)
    else:
        num = float(c_str)
    return num


def p_COMPLETE_IF_THEN2(p):
    """COMPLETE_IF_THEN2 : COMPLETE_IF_THEN OTHERWISE PRINT_VAL"""
    p[0] = '%s\nELSE\n%s' % (p[1], get_message(p[3]))


def p_COMPLETE_IF_THEN(p):
    """COMPLETE_IF_THEN : IF_COMPARISON THEN PRINT_VAL"""
    p[0] = '%s\n%s\n%s' % (p[1], p[2], get_message(p[3]))


def p_IF_COMPARISON(p):
    """IF_COMPARISON : IF COMPARISON
                     | IF2 COMPARISON"""
    p[0] = '%s %s' % (p[1], p[2])


def p_COMPARISON(p):
    """COMPARISON : COMPARISON1
                  | COMPARISON2
                  | COMPARISON3
                  | COMPARISON31
                  | COMPARISON4
                  | COMPARISON41
                  | COMPARISON5
                  | COMPARISON51
                  | COMPARISON511
                  | COMPARISON52
                  | COMPARISON521
                  | COMPARISON6
                  | COMPARISON61
                  | COMPARISON7
                  | COMPARISON711
                  | COMPARISON712
                  | COMPARISON8
                  | COMPARISON81
                  | COMPARISON9
                  | COMPARISON91
                  | COMPARISON10
                  | COMPARISON101
                  | COMPARISON11"""
    p[0] = p[1]


def p_COMPARISON3(p):
    """COMPARISON3 : COMPARISON AND COMPARISON
                   | COMPARISON OR COMPARISON"""
    p[0] = '\n'.join([p[1], p[2], p[3]])


def p_COMPARISON31(p):
    """COMPARISON31 : LPAREN COMPARISON AND COMPARISON RPAREN
                    | LPAREN COMPARISON OR COMPARISON RPAREN"""
    p[0] = '\n'.join([p[1], p[2], p[3], p[4], p[5]])


def p_COMPARISON1(p):
    """COMPARISON1 : THERE IS DATA FOR MEASUREMENT"""
    codes = get_codes_for(p[5])
    s = [' NOT (%s = \'\') ' % test for test in codes]
    p[0] = '(%s)' % '\nOR\n'.join(s)


def p_COMPARISON11(p):
    """COMPARISON11 : THERE IS DATA FOR MEASUREMENT_GROUP"""
    tests = get_tests_from_group(p[5])
    p[0] = '(NOT (%s))' % '\nAND\n'.join([get_test_for_absence_for_measurement(test_name)
                                          for test_name in tests])


def p_COMPARISON2(p):
    """COMPARISON2 : NO DATA FOR MEASUREMENT"""
    codes = get_codes_for(p[4])
    s = ['(%s = \'\')\n' % test for test in codes]
    p[0] = '(%s)' % '\nAND\n'.join(s)


def p_COMPARISON4(p):
    """COMPARISON4 : MEASUREMENT2 COMP NUMUM
                   | MEASUREMENT2 COMP NUMNM
                   | MEASUREMENT2 COMP NUM"""
    s = get_average_for(p[1])
    num = get_num_for_string(p[3])
    p[0] = '( %s %s %f )' % (s, get_comparator(p[2], p[3]), num)


def p_COMPARISON41(p):
    """COMPARISON41 : MEASUREMENT2 COMP NUMUM  COMMA COMP NUMUM
                    | MEASUREMENT2 COMP NUMNM  COMMA COMP NUMUM
                    | MEASUREMENT2 COMP NUM  COMMA COMP NUMUM
                    | MEASUREMENT2 COMP NUMUM  COMMA COMP NUMNM
                    | MEASUREMENT2 COMP NUMNM  COMMA COMP NUMNM
                    | MEASUREMENT2 COMP NUM  COMMA COMP NUMNM
                    | MEASUREMENT2 COMP NUMUM  COMMA COMP NUM
                    | MEASUREMENT2 COMP NUMNM  COMMA COMP NUM
                    | MEASUREMENT2 COMP NUM  COMMA COMP NUM"""
    s = get_average_for(p[1])
    num = get_num_for_string(p[3])
    num2 = get_num_for_string(p[6])
    p[0] = '((%s %s %f) AND (%s %s %f))\n' % (s, get_comparator(p[2], p[3]), num,
                                              s, get_comparator(p[5], p[6]), num2)


def p_COMPARISON711(p):
    """COMPARISON711 : FIFTY_PERCENT_POINT_FOR_ANY_OF_MEASUREMENT COMP NUMNM COMMA COMP NUMUM
                     | FIFTY_PERCENT_POINT_FOR_ANY_OF_MEASUREMENT COMP NUMNM COMMA COMP NUMNM
                     | FIFTY_PERCENT_POINT_FOR_ANY_OF_MEASUREMENT COMP NUMNM COMMA COMP NUM
                     | FIFTY_PERCENT_POINT_FOR_ANY_OF_MEASUREMENT COMP NUM COMMA COMP NUMUM
                     | FIFTY_PERCENT_POINT_FOR_ANY_OF_MEASUREMENT COMP NUM COMMA COMP NUMNM
                     | FIFTY_PERCENT_POINT_FOR_ANY_OF_MEASUREMENT COMP NUM COMMA COMP NUM
                     | FIFTY_PERCENT_POINT_FOR_ANY_OF_MEASUREMENT COMP NUMUM COMMA COMP NUMUM
                     | FIFTY_PERCENT_POINT_FOR_ANY_OF_MEASUREMENT COMP NUMUM COMMA COMP NUMNM
                     | FIFTY_PERCENT_POINT_FOR_ANY_OF_MEASUREMENT COMP NUMUM COMMA COMP NUM"""

    codes = get_codes_for(p[1])
    num = get_num_for_string(p[3])
    num2 = get_num_for_string(p[6])
    s = ['((%s %s %f) AND (%s %s %f))\n' % (test, get_comparator(p[2], p[3]), num, test,
                                            get_comparator(p[5], p[6]), num2)
         for test in codes]
    p[0] = '(%s)' % '\nOR\n'.join(s)


def p_COMPARISON7(p):
    """COMPARISON7 : FIFTY_PERCENT_POINT_FOR_ANY_OF_MEASUREMENT COMP NUMNM
                   | FIFTY_PERCENT_POINT_FOR_ANY_OF_MEASUREMENT COMP NUMUM
                   | FIFTY_PERCENT_POINT_FOR_ANY_OF_MEASUREMENT COMP NUM"""
    codes = get_codes_for(p[1])
    num = get_num_for_string(p[3])
    s = ['( %s %s %f)\n' % (test, get_comparator(p[2], p[3]), num) for test in codes]
    p[0] = '(%s)' % '\nOR\n'.join(s)


def p_COMPARISON712(p):
    """COMPARISON712 : FIFTY_PERCENT_POINT_FOR_ANY_TEST_OF_MEASUREMENT_GROUP COMP NUMNM
                   | FIFTY_PERCENT_POINT_FOR_ANY_TEST_OF_MEASUREMENT_GROUP COMP NUMUM
                   | FIFTY_PERCENT_POINT_FOR_ANY_TEST_OF_MEASUREMENT_GROUP COMP NUM"""
    tests = get_tests_from_group(p[1])
    num = get_num_for_string(p[3])
    cmp = get_comparator(p[2], p[3])
    s = ['( %s %s %f)\n' % (get_average_for(test_name), cmp, num) for test_name in tests]
    p[0] = '(%s)' % '\nOR\n'.join(s)


def p_COMPARISON8(p):
    """COMPARISON8 : FIFTY_PERCENT_POINT_FOR_EVERY_OF_MEASUREMENT COMP NUMUM
                   | FIFTY_PERCENT_POINT_FOR_EVERY_OF_MEASUREMENT COMP NUMNM
                   | FIFTY_PERCENT_POINT_FOR_EVERY_OF_MEASUREMENT COMP NUM"""
    codes = get_codes_for(p[1])
    num = get_num_for_string(p[3])
    cmp = get_comparator(p[2], p[3])
    s = ['(%s %s %f)\n' % (test, cmp, num) for test in codes]
    p[0] = '(%s)' % '\nAND\n'.join(s)


def p_COMPARISON81(p):
    """COMPARISON81 : FIFTY_PERCENT_POINT_FOR_EVERY_TEST_OF_MEASUREMENT_GROUP COMP NUMUM
                    | FIFTY_PERCENT_POINT_FOR_EVERY_TEST_OF_MEASUREMENT_GROUP COMP NUMNM
                    | FIFTY_PERCENT_POINT_FOR_EVERY_TEST_OF_MEASUREMENT_GROUP COMP NUM"""
    tests = get_tests_from_group(p[1])
    num = get_num_for_string(p[3])
    cmp = get_comparator(p[2], p[3])
    s = ['( %s %s %f)\n' % (get_average_for(test_name), cmp, num) for test_name in tests]
    p[0] = '(%s)' % '\nAND\n'.join(s)


def p_COMPARISON9(p):
    """COMPARISON9 : THERE IS LESS THAN NUM FOLD DIFFERENCE BETWEEN FIFTY_PERCENT_POINT IN MEASUREMENT AND FIFTY_PERCENT_POINT IN MEASUREMENT
                   | THERE IS LESS THAN NUM FOLD DIFFERENCE BETWEEN TWENTY_PERCENT_POINT IN MEASUREMENT AND TWENTY_PERCENT_POINT IN MEASUREMENT
                   | THERE IS LESS THAN NUM FOLD DIFFERENCE BETWEEN FIFTY_PERCENT_POINT IN MEASUREMENT AND TWENTY_PERCENT_POINT IN MEASUREMENT
                   | THERE IS LESS THAN NUM FOLD DIFFERENCE BETWEEN TWENTY_PERCENT_POINT IN MEASUREMENT AND FIFTY_PERCENT_POINT IN MEASUREMENT"""
    test1average = get_average_for(p[11])
    test2average = get_average_for(p[15])
    num = math.log10(float(p[5]))
    if num < 0:
        num = -num
    p[0] = '(((%s - %s) < %f) AND ((%s - %s) > -%f))' % (test1average, test2average, num,
                                                         test1average, test2average, num)


def p_COMPARISON91(p):
    """COMPARISON91 : THERE IS MORE THAN NUM FOLD DIFFERENCE BETWEEN FIFTY_PERCENT_POINT IN MEASUREMENT AND FIFTY_PERCENT_POINT IN MEASUREMENT
                   | THERE IS MORE THAN NUM FOLD DIFFERENCE BETWEEN TWENTY_PERCENT_POINT IN MEASUREMENT AND TWENTY_PERCENT_POINT IN MEASUREMENT
                   | THERE IS MORE THAN NUM FOLD DIFFERENCE BETWEEN FIFTY_PERCENT_POINT IN MEASUREMENT AND TWENTY_PERCENT_POINT IN MEASUREMENT
                   | THERE IS MORE THAN NUM FOLD DIFFERENCE BETWEEN TWENTY_PERCENT_POINT IN MEASUREMENT AND FIFTY_PERCENT_POINT IN MEASUREMENT"""
    test1average = get_average_for(p[11])
    test2average = get_average_for(p[15])
    num = math.log10(float(p[5]))
    if num < 0:
        num = -num
    p[0] = '(((%s - %s) > %f) OR ((%s - %s) < -%f))' % (test1average, test2average, num,
                                                        test1average, test2average, num)


def p_COMPARISON5(p):
    """COMPARISON5 : COMPONENT IS AT LEAST NUM_FOLD LESS POWERFUL IN THE MEASUREMENT"""
    # key property
    s = '(' + get_average_for('key test') + '-' + get_average_for(p[10]) + ')'
    p[0] = '( %s > %f )' % (s, math.log10(float(str(p[5])[:-1])))


def p_COMPARISON51(p):
    """COMPARISON51 : FIFTY_PERCENT_POINT FOR MEASUREMENT IS AT LEAST NUM_FOLD LESS POWERFUL THAN FIFTY_PERCENT_POINT FOR MEASUREMENT"""
    # key property
    s = '( %s - %s )' % (get_average_for(p[13]), get_average_for(p[3]))
    p[0] = '( %s >= %f )' % (s, math.log10(float(str(p[7])[:-1])))


def p_COMPARISON511(p):
    """COMPARISON511 : FIFTY_PERCENT_POINT FOR MEASUREMENT IS AT LEAST NUM_FOLD LESS POWERFUL THAN FIFTY_PERCENT_POINT FOR MEASUREMENT_GROUP"""
    # key property
    tests = get_tests_from_group(p[13])
    s1 = get_average_for(p[3])
    num = math.log10(float(str(p[7])[:-1]))
    s = ['( %s - %s >= %f)' % (get_average_for(test_name), s1, num) for test_name in tests]
    p[0] = '(%s)' % '\nAND\n'.join(s)


def p_COMPARISON52(p):
    """COMPARISON52 : FIFTY_PERCENT_POINT FOR MEASUREMENT IS AT LEAST NUM_FOLD MORE POWERFUL THAN FIFTY_PERCENT_POINT FOR MEASUREMENT"""
    # key property
    s = '(%s - %s)' % (get_average_for(p[3]), get_average_for(p[13]))
    p[0] = '( %s >= %f )' % (s, math.log10(float(str(p[7])[:-1])))


def p_COMPARISON521(p):
    """COMPARISON521 : FIFTY_PERCENT_POINT FOR MEASUREMENT IS AT LEAST NUM_FOLD MORE POWERFUL THAN FIFTY_PERCENT_POINT FOR MEASUREMENT_GROUP"""
    # key property
    tests = get_tests_from_group(p[13])
    s1 = get_average_for(p[3])
    num = math.log10(float(str(p[7])[:-1]))
    s = ['( %s - %s >= %f)' % (s1, get_average_for(test_name), num) for test_name in tests]
    p[0] = '(%s)' % '\nAND\n'.join(s)


def p_COMPARISON6(p):
    """COMPARISON6 : NO DATA FOR ANY_OF_MEASUREMENT"""
    p[0] = get_test_for_absence_for_measurement(p[4], joiner='OR')


def p_COMPARISON61(p):
    """COMPARISON61 : NO DATA FOR EVERY_OF_MEASUREMENT"""
    p[0] = get_test_for_absence_for_measurement(p[4])


def p_COMPARISON10(p):
    """COMPARISON10 : NO DATA FOR ANY_TEST_OF_MEASUREMENT_GROUP"""
    tests = get_tests_from_group(p[4])
    p[0] = '(%s)' % '\nOR\n'.join([get_test_for_absence_for_measurement(test_name, 'AND')
                                   for test_name in tests])


def p_COMPARISON101(p):
    """COMPARISON101 : NO DATA FOR EVERY_TEST_OF_MEASUREMENT_GROUP"""
    tests = get_tests_from_group(p[4])
    p[0] = '(%s)' % '\nAND\n'.join([get_test_for_absence_for_measurement(test_name)
                                    for test_name in tests])


def p_FIFTY_PERCENT_POINT_FOR_EVERY_OF_MEASUREMENT(p):
    """FIFTY_PERCENT_POINT_FOR_EVERY_OF_MEASUREMENT : FIFTY_PERCENT_POINT FOR EVERY_OF_MEASUREMENT IS
                                     | TWENTY_PERCENT_POINT FOR EVERY_OF_MEASUREMENT IS"""
    p[0] = p[3]


def p_FIFTY_PERCENT_POINT_FOR_EVERY_TEST_OF_MEASUREMENT_GROUP(p):
    """FIFTY_PERCENT_POINT_FOR_EVERY_TEST_OF_MEASUREMENT_GROUP : FIFTY_PERCENT_POINT FOR EVERY_TEST_OF_MEASUREMENT_GROUP IS
                                                 | TWENTY_PERCENT_POINT FOR EVERY_TEST_OF_MEASUREMENT_GROUP IS"""
    p[0] = p[3]


def p_FIFTY_PERCENT_POINT_FOR_ANY_OF_MEASUREMENT(p):
    """FIFTY_PERCENT_POINT_FOR_ANY_OF_MEASUREMENT : FIFTY_PERCENT_POINT FOR ANY_OF_MEASUREMENT IS
                                   | TWENTY_PERCENT_POINT FOR ANY_OF_MEASUREMENT IS"""
    p[0] = p[3]


def p_FIFTY_PERCENT_POINT_FOR_ANY_OF_MEASUREMENT_GROUP(p):
    """FIFTY_PERCENT_POINT_FOR_ANY_TEST_OF_MEASUREMENT_GROUP : FIFTY_PERCENT_POINT FOR ANY_TEST_OF_MEASUREMENT_GROUP IS
                                               | TWENTY_PERCENT_POINT FOR ANY_TEST_OF_MEASUREMENT_GROUP IS"""
    p[0] = p[3]


def p_MEASUREMENT2(p):
    """MEASUREMENT2 : FIFTY_PERCENT_POINT FOR MEASUREMENT IS
                    | TWENTY_PERCENT_POINT FOR MEASUREMENT IS"""
    p[0] = p[3]


def p_ANY_OF_MEASUREMENT(p):
    """ANY_OF_MEASUREMENT : ANY OF MEASUREMENT"""
    p[0] = p[3]


def p_ANY_TEST_OF_MEASUREMENT_GROUP(p):
    """ANY_TEST_OF_MEASUREMENT_GROUP : ANY TEST OF MEASUREMENT_GROUP"""
    p[0] = p[4]


def p_EVERY_OF_MEASUREMENT(p):
    """EVERY_OF_MEASUREMENT : EVERY OF MEASUREMENT"""
    p[0] = p[3]


def p_EVERY_TEST_OF_MEASUREMENT_GROUP(p):
    """EVERY_TEST_OF_MEASUREMENT_GROUP : EVERY TEST OF MEASUREMENT_GROUP"""
    p[0] = p[4]


def p_MEASUREMENT(p):
    """MEASUREMENT : ID TEST
                   | ID CRITICAL_BREAKDOWN"""
    p[0] = '%s %s' % (p[1], p[2])


def p_MEASUREMENT_GROUP(p):
    """MEASUREMENT_GROUP : ID TESTGROUP"""
    p[0] = '%s %s' % (p[1], p[2])


def p_IF2(p):
    """IF2 : COMPLETE_IF_THEN OTHERWISE IF"""
    p[0] = '%s\nELSIF ' % p[1]


# Error rule for syntax errors
def p_error(p):
    if not p:
        raise IncompleteRuleError(p, ERROR_TEXT)
    else:
        raise IncorrectGrammarError(p, ERROR_TEXT)


def parse_text(desc):
    # Build the parser
    lexer = lex.lex()
    parser = yacc.yacc()
    output = ''
    result = parser.parse(desc, debug=False)
    return result, output


def get_translation(desc):
    """
    Translates the provided text in desc to the desired script language
    :param desc: the text to be translated
    :return: the translated text
    :raise IncompleteGrammarError if the grammar is incorrect
    :raise IncompleteRuleError if the rule parses but is not complete
    """
    result, output = parse_text(desc)
    return result


def get_next_tokens(desc):
    """
    Returns a set containing the next set of allowed tokens after the last token in the provided
    text. The text must conform to the rules and grammar required.
    :param desc: the provided completed or semi-completed rule
    :return: a set containing the set of the next allowed tokens after the last word in the rule.
    If the rule is complete, returns an empty set.
    :raise IncorrectGrammarError if the rule passed in has incorrect grammar
    """
    # Build the parser
    lexer = lex.lex()
    parser = yacc.yacc()
    state_num = -1
    complete = False
    with io.StringIO() as buf, redirect_stderr(buf):
        try:
            parser.parse(desc, debug=True)
            complete = True
        except IncompleteRuleError:
            output = buf.getvalue()
            lines = output.split('\n')
            state_num = -1
            for line in lines:
                if line.startswith('State  :'):
                    w = line.split()
                    state_num = int(w[-1])
    return {} if complete else constants.get_allowed_tokens(state_num)


def get_rule_text(fname='Data/TestMappings.xlsx'):
    rule_text = ''
    df = pd.read_excel(fname, sheet_name='Text')
    for i in range(len(df)):
        linetext = str(df.loc[i, 'Text'])
        if linetext != '' and linetext != 'nan':
            if len(rule_text) > 0:
                rule_text = '%s\n%s' % (rule_text, linetext)
            else:
                rule_text = linetext
    return rule_text


def get_all_tokens():
    """
    Returns a dictionary of all the allowed tokens with the token names as keys and the regular expressions
    corresponding to each token as values
    :return: a dictionary of all the allowed tokens with the token names as keys and the regular expressions
    corresponding to each token as values
    """
    all_tokens = {}
    for key in reserved:
        all_tokens[key] = reserved[key]
    for token in constants.regexp_tokens:
        all_tokens[token] = getattr(constants, 't_%s' % token)
    return all_tokens


def is_complete(rule):
    """
    Returns whether or not the passed in rule is complete
    :param rule: the rule to parse
    :return: True if the rule is valid and complete. False otherwise
    """
    try:
        parse_text(rule.upper())
    except IncompleteRuleError:
        print('Incomplete Rule')
        return False
    except IncorrectGrammarError:
        print('incorrect grammar')
        return False
    return True


def parses(rule):
    """
    Parses the passed in rule and returns whether or not it parses. The rule may or may not be complete.
    :param rule: the rule to parse
    :return: True if the rule parses correctly (even if incomplete). False otherwise.
    """
    try:
        parse_text(rule.upper())
    except IncompleteRuleError:  # parses but is not complete
        print('Incomplete Rule')
        return True
    except IncorrectGrammarError:  # does not parse due to incorrect grammar
        print('Incorrect grammar')
        return False
    return True


def read_test_mappings(input_excelfile='Data/TestMappings.xlsx'):
    global test_types, test_mappings, testgroup_mappings
    df = pd.read_excel(input_excelfile, sheet_name='Mappings')
    df.dropna()
    current_enz = None

    ams = {}
    ats = {}
    agms = {}  # maps testgroup names to tests corresponding to the test group.
    in_group = False

    for i in range(len(df)):
        enz_name = df.loc[i, 'Activity']
        if str(enz_name) != 'nan' and len(str(enz_name).strip()) > 0:
            current_enz = str(enz_name).strip()
            in_group = current_enz.endswith('TESTGROUP')
            if not in_group:
                ams[current_enz] = []
                ats[current_enz] = []
            elif len(current_enz) > 0:
                agms[current_enz] = []
        test = str(df.loc[i, 'Test']).strip()
        if not in_group:
            test_type = str(df.loc[i, 'Test Type'])
            if len(current_enz) > 0:
                if str(test_type) == 'nan':
                    test_type = ''
                ams[current_enz].append(test)
                ats[current_enz].append(test_type.strip())
        else:
            if len(current_enz) > 0:
                agms[current_enz].append(test)

    test_mappings = ams
    test_types = ats
    testgroup_mappings = agms
    return test_mappings, test_types, testgroup_mappings


def get_rule(text,
             ams,
             ats,
             agms):
    global testgroup_mappings
    global test_mappings
    global test_types

    test_mappings = ams
    test_types = ats
    testgroup_mappings = agms
    r, output = parse_text(text.upper())
    return r


def process_rule(xls_filename):
    test_maps, test_typs, testgroup_maps = read_test_mappings(xls_filename)
    text = get_rule_text(xls_filename)
    return get_rule(text, test_maps, test_typs, testgroup_maps)


def get_specific_tests(test_category: str):
    """
    If test_category is specified, returns a set of the specific tests for the test_category, if
    the test_category is valid. Returns None if the test_category is not valid.
    If test_category is not specified, returns a dictionary containing all test_category names
    as keys with a set containing the specific tests for that test category as values.
    :param test_category: the name of the test category for which the specific tests are needed.
    :return: None if the test_category is not valid. A
    Returns a list of strings for the provided token which are in the token map. A set of the specific tests for the
    test_category, if
    the test_category is valid. A dictionary containing all test_category names
    as keys with a set containing the specific tests for that test category as values, if test_category is None.
    """
    global testgroup_mappings, test_mappings, test_types

    if not test_category:
        return test_mappings
    elif test_category in test_mappings:
        return test_mappings[test_category]
    else:
        return None


def delete_specific_test_from_test_category(specific_test: str,
                                            test_category: str):
    """
    Removes a specific test from the list if tests for that test category if that specific test exists in
    the list of tests for the test category.
    Returns True if the specific test does exist and is removed. False otherwise.
    :param test_category: the test category to delete the specific test from.
    :param specific_test: the name of the specific test to delete.
    :return: True if the test category exists, and the specific test exists as a test
    for the test category. False otherwise.
    """
    global testgroup_mappings, test_mappings, test_types

    if test_category in test_mappings:
        inds = [i for i, an in enumerate(test_mappings[test_category]) if an == specific_test]
        if not inds:
            return False
        else:
            inds.reverse()
            for i in inds:
                del test_mappings[test_category][i]
                del test_types[test_category][i]
            return True
    else:
        return False


def add_specific_test_to_test_category(specific_test: str,
                                       test_category: str,
                                       test_type: str = 'FIFTY_PERCENT_POINT'):
    """
    Adds the provided specific test as an additional test to the test category.
    The test type may also be specified
    :param test_type: the test type for the specific test. Defaults to FIFTY_PERCENT_POINT.
    :param test_category: the test category to add the specific test to.
    :param specific_test: the name of the specific test to add.
    :return: True if success. False otherwise. Failure happens if the indicated test_type is not already
    present.
    """
    global testgroup_mappings, test_mappings, test_types

    if test_category in test_mappings:
        if specific_test not in test_mappings[test_category]:
            test_mappings[test_category].append(specific_test)
            test_types[test_category].append(test_type)
        else:
            return False
    else:
        test_mappings[test_category] = [specific_test]
        test_types[test_category] = [test_type]
    return True
