from app.exceptions.http import HttpException
from app.serializers.query import QuerySerializer
from app.serializers.rule_function import RuleFunctionSerializer
from app.parser import constants, parse_garage_language as parser, ParserErrors
from app.config import Config


class RuleFunctionService:
    """
    rule function service

    parse_rule_text(): parse ruleText according to function
    get_test_by_category(): get specific tests with category
    """
    def __init__(self):
        """
        init parser and constants
        """
        parser.read_test_mappings(Config.TEST_MAPPING_PATH)
        constants.read_parser_out_file()

    def parse_rule_text(self, data, function):
        rule_text = data.get('ruleText')

        if rule_text is None or rule_text == '':
            raise HttpException(400, 'ruleText is not exists')

        try:
            if function == 'next-tokens':
                # get next tokens
                tokens = parser.get_next_tokens(rule_text)
                return RuleFunctionSerializer(next_tokens=tokens)

            elif function == 'translation':
                # get translation
                translation = parser.get_translation(rule_text)
                return RuleFunctionSerializer(translation=translation)

            elif function == 'parses':
                # get parse state
                parses = parser.parses(rule_text)
                return RuleFunctionSerializer(parses=parses)

            elif function == 'is-complete':
                # get complete state
                is_complete = parser.is_complete(rule_text)
                return RuleFunctionSerializer(is_complete=is_complete)

            else:
                # invalid endpoint
                raise HttpException(404, 'Endpoint not found ' + function)

        except ParserErrors.IncompleteRuleError:
            # incomplete
            raise HttpException(400, 'Rule text is incomplete')

        except ParserErrors.IncorrectGrammarError:
            # incorrect
            raise HttpException(400, 'Rule text is incorrect')

    def get_test_by_category(self, query, function):
        """
        get rule by category
        :param query: query
        :param function: function
        :return: dictionary
        """
        # get query
        query = QuerySerializer(query)

        if function == 'specific-tests':
            # get result
            return parser.get_specific_tests(query.get('category'))
        else:
            # invalid endpoint
            raise HttpException(404, 'Endpoint not found ' + function)

