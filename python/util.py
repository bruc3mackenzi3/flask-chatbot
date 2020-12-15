from typing import Dict, List, Tuple, Union


class Util:
    @staticmethod
    def build_substring_query(
            query_terms: List[str],
            column: str
    ) -> Tuple[List, List]:
        # Build parameter list by mapping query terms into SQL wildcards
        parameters = [f"%{term}%" for term in query_terms]

        # Build where clause by duplicating the condition by the number of search terms
        where = " and ".join([f"{column} LIKE ?"] * len(parameters))

        return (where, parameters)

    @staticmethod
    def to_sql_list(l: List) -> str:
        """
        Utility method to convert Python list to string with SQL list syntax.

        E.g.,
            [1, 2, 3] -> "(1,2,3)"
        """
        # Convert to list of strings
        l_str = [str(item) for item in l]
        # Join with comma and enclose in brackets
        return "(" + ",".join(l_str) + ")"

    @staticmethod
    def search_nested_dict_values(
            obj: Union[Dict, List],
            term: str,
            omit_keys: List=[]
    ) -> bool:
    """
    Recursive search algorithm to search nested dictionary values to contain
    term.

    Note: term is matched with a case-insensitive substring match

    Returns: True if a match was found, False otherwise
    """
        if type(obj) == list:
            for item in obj:
                if type(item) in [list, dict]:
                    result = Util.search_nested_dict_values(item, term, omit_keys)
                    if result == True:
                        return True
                    # else keep searching
                else:
                    # Skip other values in lists because the search is
                    # performed on included values only!
                    continue
            return False

        elif type(obj) == dict:
            for key, val in obj.items():
                if key in omit_keys:
                    continue
                elif type(val) in [list, dict]:
                    result = Util.search_nested_dict_values(val, term, omit_keys)
                    if result == True:
                        return True
                    # else keep searching
                elif term.lower() in str(val).lower():
                    return True
                # else keep searching`
            return False
        raise ValueError(f"bad type {type(obj)} value {obj}")
