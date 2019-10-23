# MOA_EnglishToExcel

English To Excel parser for MOA1 Rules

Note that this is currently evolving work in progress. Email 
ragu@nyrasta.com if you have questions.

Needs: 

1.  Anaconda python3 
2.  the ply module (installed via "pip3 install ply" or "conda -c conda-forge install ply")


To run: 
python parse_garage_language.py

This reads test info from the sheet 'Mappings' in Data/Brake.xlsx and the rule from the sheet 'Text' in the same file and creates a rule. Also does a few more modifications (shows autocomplete feature, language change feature etc. documented below). Read parse_garage_language.py to learn the full details.

Also ask me questions (you will have many) or if you feel you need any other API addition which may not be included.

NOTES on the interface (needed for the UI):

def get_next_tokens(desc):
    """
    Returns a set containing the next set of allowed tokens after the last token in the provided 
    text. The text must conform to the rules and grammar required.
    :param desc: the provided completed or semi-completed rule
    :return: a set containing the set of the next allowed tokens after the last word in the rule.
    If the rule is complete, returns an empty set.
    :raise IncorrectGrammarError if the rule passed in has incorrect grammar
    """



def get_translation(desc):
    """
    Translates the provided text in desc to the desired script language
    :param desc: the text to be translated
    :return: the translated text
    :raise IncompleteGrammarError if the grammar is incorrect
    :raise IncompleteRuleError if the rule parses but is not complete
    """


def parses(rule):
    """
    Parses the passed in rule and returns whether or not it parses. The rule may or may not be complete.
    :param rule: the rule to parse
    :return: True if the rule parses correctly (even if incomplete). False otherwise.
    """



def is_complete(rule):
    """
    Returns whether or not the passed in rule is complete
    :param rule: the rule to parse
    :return: True if the rule is valid and complete. False otherwise
    """


def get_specific_tests(test_category: str):
    """
    If test_category is specified, returns a set of the specific tests for the test_category, if
    the test_category is valid. Returns None if the test_category is not valid.
    If test_category is not specified, returns a dictionary containing all test_category names
    as keys with a set containing the specific tests for that test category as values.
    :param test_category: the name of the test category for which the specific tests are needed.
    :return: None if the test_category is not valid. A
    Returns a list of strings for the provided token which are in the token map. A set of the specific tests for the test_category, if
    the test_category is valid. A dictionary containing all test_category names
    as keys with a set containing the specific tests for that test category as values, if test_category is None.
    """


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

