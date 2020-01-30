import pickle
import os
import sys
import codecs
import re

def read_corpus(arg):
    if os.path.isdir(arg):
        # If a directory, grab lines from every file in the directory
        lines = []
        for filename in [os.path.join(arg, f) for f in os.listdir(arg)]:
            sys.stderr.write("Reading " + filename + "\n")
            with codecs.open(arg, 'r', encoding='utf-8', errors='ignore') as fp:
                file_lines = fp.read().split('\n')
            for line in file_lines:
                lines.append(line)
    else:
        # If a file, grab lines from this file
        sys.stderr.write("Reading " + arg + "\n")
        with codecs.open(arg, 'r', encoding='utf-8', errors='ignore') as fp:
            lines = fp.read().split('\n')

    sys.stderr.write("Processed " + str(len(lines)) + " lines from " + arg + "\n")
    return(lines)

def create_kwic_index(nlp, corpus, term_counts_file, kwic_index_file, window_width=11):
    # Given a corpus build and save KWIC index for terms that are present in term counts file.
    # A corpus is a filename with one item per line, or name of a directory containing such files.
    # Each line can optionally start with an identifier, which must be __alphanumeric, e.g. __ABC123.
    # Uses initialized spacy nlp object to tokenize.
    # Returns the KWIC index, in addition to creating and saving to file.
    lines                = read_corpus(corpus)
    counter, corpus_size = tuple( pickle.load( open( term_counts_file, "rb" ) ) )
    kwic_index           = {}
    progress_counter     = 0

    sys.stderr.write("Creating KWIC index for " + corpus + " using terms counted in " + term_counts_file + "\n")
    for line in lines:
        first_tok = line.split(' ')[0]
        analysis  = nlp(line)
        tokens    = [token.lower_ for token in analysis
                     if re.search('[^\s_]', token.orth_) is not None # ignore whitespace tokens
                     and not token.orth_.startswith("@")             # ignore twitter handles
                    ]
        if first_tok.startswith("__"):
            # If the original line starts with a token that starts with __, include that token as line ID
            add_to_kwic_index(kwic_index, tokens, counter, window_width, first_tok)
        else:
            add_to_kwic_index(kwic_index, tokens, counter, window_width, "")

    sys.stderr.write("Saving KWIC index to " + kwic_index_file + "\n")
    save_kwic_index(kwic_index, kwic_index_file)
    return kwic_index

    
def add_to_kwic_index(kwic_dict, line_tokens, known_terms, width=5, line_id=""):
    # KWIC index kwic_dict is a dict mapping from a term to list of windows with the term at its center.
    # A window has an ID string paired with a list of terms (which MUST have an odd numbered width or results will be wrong). 
    # List line_tokens contains (unigram) tokens from the input line we're adding to the KWIC index.
    # Counter known_terms contains {1,2,3}-gram terms we can include in the index; otherwise ignore.
    # This fn adds {1,2,3}-grams from line_tokens to kwic_dict (which is mutable and therefore does
    # not need to be returned) as long as they are in the known_terms set (which is a Counter).
    padded_tokens = ["_"]*width + line_tokens + ["_"]*width
    center        = width // 2                 # Index (counting from 0) of center of window
    context_size  = width - center - 1         # Size of contexts to left/right of center
    window_list   = [padded_tokens[i:i+width+context_size] for i in range(len(padded_tokens)-width+1)]
    
    for window in window_list:
        
        unigram = window[center]
        if unigram in known_terms:
            unigram_window = window[0:context_size] + [unigram] + window[center+1:center+1+context_size]
            add_term_window_pair(kwic_dict, unigram, unigram_window, line_id)
        
        bigram = window[center] + "_" + window[center+1]
        if bigram in known_terms:
            bigram_window = window[0:context_size] + [bigram] + window[center+2:center+2+context_size]
            add_term_window_pair(kwic_dict, bigram, bigram_window, line_id)

        trigram = window[center] + "_" + window[center+1] + "_" + window[center+2]
        if trigram in known_terms:
            trigram_window = window[0:context_size] + [trigram] + window[center+3:center+3+context_size]
            add_term_window_pair(kwic_dict, trigram, trigram_window, line_id)
        
def add_term_window_pair(kwic_dict, term, window, line_id):
    # Add term => window mapping to kwic_dict
    if term not in kwic_dict:
        kwic_dict[term] = [[line_id,window]]
    else:
        kwic_dict[term].append([line_id,window])

def kwic_query(kwic_dict, term, window_width, replace_underscores=False):
    # Returns list of pretty-printed (properly justified) strings for KWIC windows
    # with term at the center. Returns empty list if term not found in index.
    # ID is at left of string if present.
    # If replace_underscores is true, replace _ with space everywhere in window content.
    kwic_string_list = []
    center = window_width // 2
    try:
        window_list = kwic_dict[term]
        for window in window_list:
            line_id        = window[0]
            window_content = window[1]
            outstring = ' '.join(window_content[:center]).rjust(window_width*center)
            outstring += str(window_content[center]).center(len(window_content[center])+6)
            outstring += ' '.join(window_content[(center+1):])
            if replace_underscores:
                outstring = outstring.translate(str.maketrans("_", " ")) # tr/_/ /
            kwic_string_list.append(line_id + " " + outstring)
        return kwic_string_list
    except:
        return []

def save_kwic_index(kwic_dict, filename):
    pickle.dump( kwic_dict, open( filename, "wb" ) )

def read_kwic_index(filename):
    kwic_dict = pickle.load( open( filename, "rb" ) )
    return kwic_dict
        
