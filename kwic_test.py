import sys
import re
from collections import Counter
# from spacy.en import English # Used with older version of spacy
from spacy.lang.en import English
from kwic import *

# Example below shows component pieces. For a single top-level call see kwic_test2.py

if __name__ == "__main__":
    # Initializations: create empty dictionary for index, and define width of KWIC window
    kwic_dict = {}
    window_width = 7

    # Initialize text processing
    sys.stderr.write("Initializing spacy\n")
    nlp = English(parser=False) # faster init

    # Create set of terms to be included in the KWIC index
    known_terms = Counter()
    known_terms["test"] = 1
    known_terms["baby_shark"] = 1
    known_terms["emergency_broadcast"] = 1
    known_terms["emergency_broadcast_system"] = 1
    known_terms["not_a_real"] = 1

    # Add an example sentence to KWIC index
    analysis  = nlp('this is a test of the emergency broadcast system and it is only a test not a real emergency')
    tokens    = [token.lower_ for token in analysis
                 if re.search('[^\s_]', token.orth_) is not None # ignore whitespace tokens
                 and not token.orth_.startswith("@")             # ignore twitter handles
                 ]
    add_to_kwic_index(kwic_dict, tokens, known_terms, window_width)

    # Add another example sentence to KWIC index, providing an optional ID for this line
    exampleID = "ID1234"
    analysis  = nlp('this is another test that fortunately is not a real test but only a test example')
    tokens    = [token.lower_ for token in analysis
                 if re.search('[^\s_]', token.orth_) is not None # ignore whitespace tokens
                 and not token.orth_.startswith("@")             # ignore twitter handles
                 ]
    add_to_kwic_index(kwic_dict, tokens, known_terms, window_width, exampleID)

    # Save KWIC index to a file
    save_kwic_index(kwic_dict, "/tmp/kwic_test_index.p")

    # Read KWIC index from a file
    kindex = read_kwic_index("/tmp/kwic_test_index.p")

    # Demonstration of querying the KWIC index: show the entries for all the known terms.
    # Give kwic_query a last argument of True if you want printed ngrams to be space- rather than underscore-separated
    # (but note that all *internal* representations of ngrams in this code are underscore-separated strings)
    for term in sorted(known_terms):
        print("\n" + term)
        kwic_string_list = kwic_query(kindex, term, window_width, True)
        for kwic_string in kwic_string_list:
            print(kwic_string)

