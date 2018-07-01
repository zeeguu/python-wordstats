
"""
    script used for generating transformation rules

"""

# apply every possible combination of substitution rules until the least amount of translation is found
from wordstats.config import SEPARATOR_PRIMARY
from wordstats.cognate_evaluation import CognateEvaluation
from wordstats.edit_distance import EditDistance
from collections import defaultdict

"""
two strings, possible options: match, insert, delete, substitute
go through all combinations, combination increases parsing idx
stop criterion: end of both strings or maximum amount of operations reached
return best list if amount of operations is below the current amount


"""

REPLACE_SYMBOL = '~'
"""
    recursive implementation of edit distance measure between two words
    the edits are tracked in the process and returns the least amount of edits needed
    in order to transform one word to the other
"""

def _edit_dist_rec(s1, s2, idx, curdist, maxdist, rule_list, string_alignment):

    #print(s1, s2, idx, curdist, maxdist, rule_list, string_alignment)

    # end of strings reached
    if idx == len(s1) and idx == len(s2):
        #print("evaluate")
        if curdist <= maxdist:
            #print("lower")
            string_alignment = rule_list
            maxdist = curdist

        return (maxdist, string_alignment)

    # maximum amount of operations
    if curdist >= maxdist:
        return (maxdist, string_alignment)

    # substitute
    if len(s1) > idx and len(s2) > idx:
        new_rule = (s1, s2)
        if s1[idx] == s2[idx]:
            (maxdist, string_alignment) = _edit_dist_rec(s1, s2, idx + 1, curdist, maxdist, new_rule,
                                                         string_alignment)
            # due to a constant choice of weights we can return here for faster evaluation
            return (maxdist, string_alignment)
        else:
            (maxdist, string_alignment) = _edit_dist_rec(s1, s2, idx + 1, curdist + 1, maxdist, new_rule,
                                                         string_alignment)

    # delete

    s2new = s2[:idx] + REPLACE_SYMBOL + s2[idx:]
    new_rule = (s1,s2new)
    (maxdist, string_alignment) = _edit_dist_rec(s1, s2new, idx + 1, curdist + 1, maxdist, new_rule,
                                                 string_alignment)

    # insert
    s1new = s1[:idx] + REPLACE_SYMBOL + s1[idx:]
    new_rule = (s1new,s2)
    (maxdist, string_alignment) = _edit_dist_rec(s1new, s2, idx + 1, curdist + 1, maxdist, new_rule,
                                                 string_alignment)


    return (maxdist, string_alignment)

# applies recursive edit_distance measure, as a result two aligned strings are returned
# e.g. ('tochter', 'maid~~~') from which translation rules can be extracted
def edit_distance(s1, s2):

    rule_list = []

    (dist, string_alignment) = _edit_dist_rec(s1, s2, 0, 0, max(len(s1),len(s2)), rule_list, rule_list)

    print(dist, string_alignment, s1 , s2)
    return string_alignment


# extracts translation rules from two aligned strings.
# this is done by taking ngrams from each string and combine them into pairs to form rules
def extract_rules(s1_align, s2_align):
    rules = []

    for i in range(0, len(s1_align)):
        if s1_align[i] == s2_align[i]:
            continue
        else:
            gram = 3

            for gramsize in range(1, gram + 1):
                for offset in range(1 - gramsize, 1):
                    if offset + i + gramsize <= len(s1_align) and offset + i >= 0:
                        rules.append((s1_align[offset + i: offset + i + gramsize],
                                      s2_align[offset + i: offset + i + gramsize]))
                        if offset + i == 0:
                            rules.append(('$' + s1_align[offset + i: offset + i + gramsize],
                                          '$' + s2_align[offset + i: offset + i + gramsize]))
                        if offset + i + gramsize == len(s1_align):
                            rules.append((s1_align[offset + i: offset + i + gramsize] + '$',
                                          s2_align[offset + i: offset + i + gramsize] + '$'))

    rules = [(k.replace(REPLACE_SYMBOL, ""), v.replace(REPLACE_SYMBOL, "")) for (k, v) in rules]

    return list(set(rules))


languageFrom = "de"
languageTo = "en"
cognateInfo = CognateEvaluation.load_from_path(languageFrom, languageTo, EditDistance)

print(len(cognateInfo.whitelist))

rule_list = defaultdict(int)

# glosbe translation cleanup
cognate_pairs = []
for k, values in cognateInfo.whitelist.items():
    translations = []
    for v in values:
        v = v.replace(' -s', '')
        if ' ' not in v and '[' not in v and '(' not in v:
            v = v.lower().replace('-','').replace('...','').replace('.','').replace('”','').replace('“','')
            translations.append(v)
    if len(translations) > 0:
        cognate_pairs.append((k.lower(), translations))

number_of_cognates = 0
applied_rule_frequency = 0

# generate rules, application frequency is stored separately for each rule
i = 0
for key, cogtranslations in cognate_pairs:
    str1 = key
    i += 1
    for str2 in cogtranslations:
        number_of_cognates += 1
        print(number_of_cognates)

        alignment_pairs = edit_distance(str1, str2)
        rules = extract_rules(alignment_pairs[0], alignment_pairs[1])

        for rule in rules:
            applied_rule_frequency += 1
            rule_list[rule] += 1

# determine chi-square of each rule, uniquely evaluated by considering the occurence
# of the right and/or left side of the rule in total compared to right and left side simultaneously
rule_list_score = dict()
for r_from in list(rule_list.keys()):
    lsr = r_from[0]
    rsr = r_from[1]

    if rule_list[r_from] < number_of_cognates/1000:
        rule_list_score[r_from] = 0
        continue

    applicable1 = 0
    applicable2 = 0
    for rule, freq in rule_list.items():

        if lsr == rule[0]:
            applicable1 += freq

        if rsr == rule[1]:
            applicable2 += freq

    expected = (applicable1 * applicable2) / applied_rule_frequency
    observed = rule_list[r_from]

    rule_list_score[r_from] = ((observed-expected)**2)/expected



rules_sorted = sorted(rule_list_score.items(), key=lambda x: x[1], reverse=True)


for rule in rules_sorted:
    print(rule[0][0] + SEPARATOR_PRIMARY + rule[0][1] + " " + str(rule[1]))

if True:
    for rule in rules_sorted:
        print(rule[0][0] + SEPARATOR_PRIMARY + rule[0][1] + '#')

    print("presentation form")
    for rule in rules_sorted:
        print(rule[0][0].replace('$','#') + '/' + rule[0][1].replace('$','#'))

