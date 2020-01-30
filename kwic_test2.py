import sys
import re
from collections import Counter
from spacy.en import English
from kwic import *


if __name__ == "__main__":

    # For a single top-level call, use:
    #
    #   create_kwic_index(nlp, corpus, term_counts_file, kwic_index_file, window_width)
    #
    # which will create the index and write it to kwic_index_file suitable for
    # reading using read_kwic_index(kwic_index_file) and then querying as below
    # using kwic_query.
    
    # Initializations for this test
    window_width = 11
    corpusfile   = "test.in"
    kwicfile     = "/tmp/test_kwic_index.p"
    countfile    = "/tmp/test_term_counts_file.p"

    # Initialize KWIC index
    kwic_dict = {}
    
    # Specify terms to include in this KWIC index and mock up a counts file
    # Notice that corpus size doesn't matter in this test; setting to 0
    # Also notice that ngrams should be underscore-separated, not space-separated
    known_terms = Counter()
    known_terms["line"] = 1
    known_terms["identifier"] = 1
    known_terms["another_sentence"] = 1
    pickle.dump( [known_terms, 0], open( countfile, "wb" ) )
    
    # Initialize text processing
    sys.stderr.write("Initializing spacy\n")
    nlp = English(parser=False) # faster init

    # Create the KWIC index
    sys.stderr.write("Creating KWIC index file " + kwicfile + "\n")
    create_kwic_index(nlp, corpusfile, countfile, kwicfile, window_width)

    # Read KWIC index from a file
    sys.stderr.write("Reading KWIC index\n")
    kindex = read_kwic_index(kwicfile)

    # Demonstration of querying the KWIC index: show the entries for all the known terms.
    # Give kwic_query a last argument of True if you want printed ngrams to be space- rather than underscore-separated
    # (but note that all *internal* representations of ngrams in this code are underscore-separated strings)
    for term in sorted(known_terms):
        print("\n" + term)
        kwic_string_list = kwic_query(kindex, term, window_width, True)
        for kwic_string in kwic_string_list:
            print(kwic_string)

