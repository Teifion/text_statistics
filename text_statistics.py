"""
A python implementation of https://github.com/DaveChild/Text-Statistics/. I saw it
and really liked the idea.

All functions take a string and return a Decimal score.

"""
from decimal import Decimal as D
from collections import Counter
from math import sqrt
import re
import sys

def flesch_kincaid_reading_ease(text):
    """https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests
    206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
    """
    text = clean_text(text)
    
    words = _count_words(text)
    sentences = _count_sentences(text)
    syllables = _count_syllables(text)
    
    words_over_sentences = words / sentences
    syllables_over_words = syllables / words
    
    score = D(206.835) - (D(1.015) * words_over_sentences) - (D(84.6) * syllables_over_words)
    
    return score

def flesch_kincaid_grade_level(text):
    """https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests
    0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
    """
    text = clean_text(text)
    
    words = _count_words(text)
    sentences = _count_sentences(text)
    syllables = _count_syllables(text)
    
    words_over_sentences = words / sentences
    syllables_over_words = syllables / words
    
    score = (D(0.39) * words_over_sentences) + (D(11.8) * syllables_over_words) - D(15.59)
    
    return score

def gunning_fog_score(text):
    """https://en.wikipedia.org/wiki/Gunning_fog_index
    0.4 * ((words / sentences) + 100 * (complex_words / words))
    """
    text = clean_text(text)
    
    words = _count_words(text)
    sentences = _count_sentences(text)
    complex_words = _count_complex_words(text)
    
    words_over_sentences = words / sentences
    complex_over_normal = complex_words / words
    
    score = D(0.4) * (words_over_sentences + (100 * complex_over_normal))
    
    return score

def coleman_liau_index(text):
    """https://en.wikipedia.org/wiki/Coleman%E2%80%93Liau_index
    Lower = Easier to read
    
    L = average number of letters per 100 words
    S = average number of sentences per 100 words
    (0.0588 * L) - (0.296 * S) - 15.8
    """
    text = clean_text(text)
    
    words = _count_words(text)
    sentences = _count_sentences(text)
    letters = _count_letters(text)
    
    L = (letters / words) * D(100)
    S = (sentences / words) * D(100)
    
    score = (D(0.0588) * L) - (D(0.296) * S) - D(15.8)
    
    return score

def smog_index(text):
    """https://en.wikipedia.org/wiki/SMOG
    
    1.043 * sqrt(polysyllables * (30 / sentences) + 3.1291)
    """
    text = clean_text(text)
    
    sentences = _count_sentences(text)
    polysyllables = _count_complex_words(text)
    
    score = D(1.043) * D(sqrt(polysyllables * (D(30) / sentences) + D(3.1291)))
    
    return score

def automated_readability_index(text):
    """https://en.wikipedia.org/wiki/Automated_Readability_Index
    
    4.71 * (characters / words) + 0.5 * (words / sentences) - 21.43
    """
    text = clean_text(text)
    
    words = _count_words(text)
    sentences = _count_sentences(text)
    letters = _count_letters(text)
    
    score = D(4.71) * (letters / words) + (D(0.5) * (words / sentences)) - D(21.43)
    
    return score

def clean_text(text):
    return text
    # static $clean = array();

    # if (isset($clean[$strText])) {
    #     return $clean[$strText];
    # }

    # $key = $strText;

    # // all these tags should be preceeded by a full stop.
    # $fullStopTags = array('li', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'dd');
    # foreach ($fullStopTags as $tag) {
    #     $strText = str_ireplace('</'.$tag.'>', '.', $strText);
    # }
    # $strText = strip_tags($strText);
    # $strText = preg_replace('/[",:;()-]/', ' ', $strText); // Replace commas, hyphens, quotes etc (count them as spaces)
    # $strText = preg_replace('/[\.!?]/', '.', $strText); // Unify terminators
    # $strText = trim($strText) . '.'; // Add final terminator, just in case it's missing.
    # $strText = preg_replace('/[ ]*(\n|\r\n|\r)[ ]*/', ' ', $strText); // Replace new lines with spaces
    # $strText = preg_replace('/([\.])[\. ]+/', '$1', $strText); // Check for duplicated terminators
    # $strText = trim(preg_replace('/[ ]*([\.])/', '$1 ', $strText)); // Pad sentence terminators
    # $strText = preg_replace('/ [0-9]+ /', ' ', ' ' . $strText . ' '); // Remove "words" comprised only of numbers
    # $strText = preg_replace('/[ ]+/', ' ', $strText); // Remove multiple spaces
    # $strText = preg_replace_callback('/\. [^ ]+/', create_function('$matches', 'return strtolower($matches[0]);'), $strText); // Lower case all words following terminators (for gunning fog score)

    # $strText = trim($strText);

    # // Cache it and return
    # $clean[$key] = $strText;
    # return text.strip()

_re_count_sentences = re.compile(r'[^\.!?]')
_re_remove_fake_sentences = (
    re.compile(r'[A-Z]\.[A-Z]\.'),
    re.compile(r'Mr\.'),
)
def _count_sentences(text):
    if len(text) == 0:
        return 0
    
    # Remove "words" such as U.K. and Mr.
    for remover in _re_remove_fake_sentences:
        text = remover.sub('', text)
    
    return D(max(1, len(_re_count_sentences.sub('', text))))

_re_count_words = re.compile(r'[^ ]')
def _count_words(text):
    if len(text) == 0:
        return 0
    
    # Will be tripped by em dashes with spaces either side, among other similar characters
    # Space count + 1 is word count
    return D(1 + len(_re_count_words.sub('', text)))

def average_words_per_sentence(text):
    raise Exception("Not implemented")

def _count_syllables(text):
    words = text.split(' ')
    return D(sum(map(syllable_count, words)))

def _count_complex_words(text):
    """Words with 3 or more syllables"""
    
    words = text.split(' ')
    
    long_words = len(tuple(filter(
        lambda w: _count_syllables(w) >= 3,
        words
    )))
    
    return D(long_words)/D(len(words))

_re_letters_and_digits = re.compile(r'[^a-zA-Z0-9]')
def _count_letters(text):
    text = _re_letters_and_digits.sub('', text)
    return len(text)

_syllable_problem_words = {
    'simile': 3,
    'forever': 3,
    'shoreline': 2,
}

# These syllables would be counted as two but should be one
_sub_syllables = (
    re.compile(r'cial'),
    re.compile(r'tia'),
    re.compile(r'cius'),
    re.compile(r'cious'),
    re.compile(r'giu'),
    re.compile(r'ion'),
    re.compile(r'iou'),
    re.compile(r'sia$'),
    re.compile(r'[^aeiuoyt]{2,}ed$'),
    re.compile(r'.ely$'),
    re.compile(r'[cg]h?e[rsd]?$'),
    re.compile(r'rved?$'),
    re.compile(r'[aeiouy][dt]es?$'),
    re.compile(r'[aeiouy][^aeiouydt]e[rsd]?$'),
    re.compile(r'[aeiouy]rse$'), #Purse, hearse
)

# These syllables would be counted as one but should be two
_add_syllables = (
    re.compile(r'ia'),
    re.compile(r'riet'),
    re.compile(r'dien'),
    re.compile(r'iu'),
    re.compile(r'io'),
    re.compile(r'ii'),
    re.compile(r'[aeiouym]bl$'),
    re.compile(r'[aeiou]{3}'),
    re.compile(r'^mc'),
    re.compile(r'ism$'),
    re.compile(r'([^aeiouy])\1l$'),
    re.compile(r'[^l]lien'),
    re.compile(r'^coa[dglx].'),
    re.compile(r'[^gq]ua[^auieo]'),
    re.compile(r'dnt$'),
    re.compile(r'uity$'),
    re.compile(r'ie(r|st)$'),
)

# Single syllable prefixes and suffixes
_syllable_prefix_suffix = (
    re.compile(r'^un'),
    re.compile(r'^fore'),
    re.compile(r'ly$'),
    re.compile(r'less$'),
    re.compile(r'ful$'),
    re.compile(r'ers?$'),
    re.compile(r'ings?$'),
)

_re_syllable_non_word_chars = re.compile(r'[^a-z]')
_re_syllable_word_parts = re.compile(r'[^aeiouy]+')
def syllable_count(text):
    """This is not an easy problem to solve: https://stackoverflow.com/questions/405161/detecting-syllables-in-a-word
    The accepted answer links to a thesis on the problem: http://www.tug.org/docs/liang/
    """
    
    if len(text) == 0: return 0
    
    # We don't care about case, we can assume lowercase for everything make it easier
    text = text.lower()
    
    # Remove all non alpha characters
    text = _re_letters_and_digits.sub('', text)
    
    syllable_count = 0
    
    # Specific common exceptions that don't follow the rule set below are handled individually
    # array of problem words (with word as key, syllable count as value)
    if text in _syllable_problem_words:
        return _syllable_problem_words[text]
    
    # Remove prefixes and suffixes and count how many were taken
    # Interestingly this is a longer piece of code than the PHP version
    prefix_suffix_count = 0
    for pf in _syllable_prefix_suffix:
        prefix_suffix_count += len(pf.findall(text))
        text = pf.sub('', text)
    
    # Remove non-word characters from word
    text = _re_syllable_non_word_chars.sub('', text)
    word_parts = _re_syllable_word_parts.split(text)
    
    word_part_count = 0;
    for word_part in word_parts:
        if word_part != '':
            word_part_count += 1
    
    # Some syllables do not follow normal rules
    syllable_count = word_part_count + prefix_suffix_count
    for re_syllable in _sub_syllables:
        if re_syllable.search(text):
            syllable_count -= 1
    
    for re_syllable in _add_syllables:
        if re_syllable.search(text):
            syllable_count += 1
    
    if syllable_count == 0:
        syllable_count = 1
    
    return D(syllable_count)

if __name__ == '__main__':
    sentence = sys.argv[1]
    print(automated_readability_index(sentence))

# There's Toad Hall,' said the Rat; 'and that creek on the left, where the notice-board says, 'Private. No landing allowed,' leads to his boat-house, where we'll leave the boat. The stables are over there to the right. That's the banqueting-hall you're looking at now - very old, that is. Toad is rather rich, you know, and this is really one of the nicest houses in these parts, though we never admit as much to Toad.

# The foregoing warranties by each party are in lieu of all other warranties, express or implied, with respect to this agreement, including but not limited to implied warranties of merchantability and fitness for a particular purpose. Neither party shall have any liability whatsoever for any cover or setoff nor for any indirect, consequential, exemplary, incidental or punitive damages, including lost profits, even if such party has been advised of the possibility of such damages.