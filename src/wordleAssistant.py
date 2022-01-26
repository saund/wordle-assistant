
#wordleAssistant.py
#Eric Saund
#2022/01/25
#I was going to avoid wasting time on wordle but my friend Don provoked me to do this.
#
#This program is a wordle assistant.
#Given some set of candidate probe words and some constraints provided by responses
#to guesses, this makes a list of remaining allowable answer words, and it scores
#candidate probe words for how good a choice each one would be.
#
#There is no claim of optimal scoring.  In fact, the scoring function produces
#two scores.  One score aims for the smallest average number of guesses, the other
#aims to minimize the number of daily wordle answer words that will not be found
#in time.
#The program performs one-ply search, testing candidate probe words against the
#list of possible remaining answer words, to average out how much information the probe
#word provides.



################################################################################
#
#How to use the program:
#
#1. The program runs in python3.  Make sure python3 is installed on your computer.
#
#2. Download the program and the word list files, wordle-answer-words.text and
#   wordle-probe-words.text to a directory.
#
#3. In a shell window, navigate to the directory where you installed the program
#   and word list file.
#   <your-dir>/> 
#
#4. Run python:
#   <your-dir>/> python
#
#5.>>> import wordleAssistant as wa
#      The import step loads two lists of words, one list of 2,315 words that can be
#      answer words, and another list of 12,970 words that can be probe words.
#      Give these word lists slightly more convenient names:
#
#>>> answer_word_list = wa.gl_answer_word_list  
#>>> len(answer_word_list)
#2315
#>>> probe_word_list = wa.gl_probe_word_list
#>>> len(probe_word_list)
#12970
#
#6. Select a probe word for your wordle game of the day, and enter it in Wordle.
#   From running the function, wa.scoreProbeWords() on all words, this program suggests
#   the following probe words, but you can choose whatever you like.
#
#$$

#
#   Lower score is better because that means on average there will be fewer possible answer
#   words remaining after the game responds to the probe.  You'll want to prune down to the
#   single daily answer word as quickly as possible.
#
#   These are the best probe words if you only want to use candidate answer words as probes.
#
#0   ['raise', 61.00086393088553, 168]
#1   ['arise', 63.72570194384449, 168]
#2   ['irate', 63.7792656587473, 194]
#3   ['arose', 66.02116630669546, 183]
#4   ['alter', 69.99179265658748, 196]
#5   ['saner', 70.12570194384449, 219]
#6   ['later', 70.22332613390928, 196]
#7   ['snare', 71.09762419006479, 219]
#8   ['stare', 71.29460043196545, 227]
#9   ['slate', 71.57278617710583, 221]
#10   ['alert', 71.59870410367171, 196]
#11   ['crate', 72.89978401727862, 246]
#12   ['trace', 74.02030237580993, 246]
#13   ['stale', 75.60388768898488, 221]
#14   ['aisle', 76.18876889848812, 196]
#15   ['learn', 76.64060475161988, 212]
#16   ['alone', 77.16328293736501, 182]
#17   ['leant', 77.26004319654427, 208]
#18   ['least', 78.18963282937365, 221]
#19   ['crane', 78.74168466522679, 263]
#20   ['atone', 78.95939524838013, 191]
#
#
#7. Read out the wordle response, which will be something like,
#   "yellow gray gray green yellow gray"
#
#8. Use this response to compose a function call to ask wordleAssistant to find the
#   remaining words given the wordle response to your probe.
#   This is the form of your first call to the program:
#
#>>> <ok_words>, <char_constraints> = wa.pruneWordsPerProbeResponse(<word_list>,
#                                                                   [<probe_word>, <char_response_list>])
#
#For char_response_list, make it match the wordle response with the following abbreviations:
#   'l' for yeLLow
#   'y' for graY
#   'r' for gReen
#
#   For example, if you use the word, 'story' for your first probe word, your first function
#   call might look like this:
#
##>>> ok_words_1, ccl1 = wa.pruneWordsPerProbeResponse(answer_word_list, ['story', ['l', 'y', 'y', 'r', 'l', 'y']])
#
#9. How many words are still allowable?
#>>> len(ok_words_1)
#
#   ccl1 is a data structure the represents the character constraints obtained from
#   the game responses. Call this function to see the allowable characters for each
#   character position, and the list of required characters:
#
#>>> wa.printCharConstraintList(ccl1)
#
#
#10. Compute scores for these words.
#>>> scores_list_1 = wa.scoreProbeWords(ok_words_1, probe_word_list)
#
#   scores_list_1 will be a list of tuples of the form,
#      (probe_word, ave_words_remaining, max_words_remaining)
#      where probe_word is a candidate for your next wordle entry.
#      By using the second argument, probe_word_list, in the function call, we consider 
#      all words in the wordle lexicon to be candidate probe words, even if they are
#      excluded by the cues. In some cases, the best word to try next is one that
#      cannot be the final answer.
#   ave_words_remaining is the average number of words that will have to be
#      eliminated to find the correct answer word, if you use the probe_word as your next guess.
#   max_words_remaining is the maximum number of words that will have to be
#      eliminated to find the correct answer word, if you use the probe_word as your
#      next guess and the answer word happens to be the buried in a pile of distractors.
#      These scores are not rigorous; they are approximations, as the function looks only
#      one ply deep.
#   Note: this function can take several minutes to run the first time when the remaining answer
#   words (i.e. ok_words_1) numbers in the tens or hundreds. It will get faster later as
#   you reduce this list.
#   This function will print out a list of the 20 best scoring words, along with their scores.
#
#11. Usually you'll want to choose the first of these words as your next probe word.
#
#12. Repeat at step 7 with your next probe word, but this time, use the remaining words
#    in the call to pruneWordsPerProbeResponse(), i.e.
#
#>>> ok_words_2, ccl2 = wa.pruneWordsPerProbeResponse(ok_words_1, [<probe_word>, <char_response_list>])
#
#    After a few iterations, the ok_words... list will be whittled down to the final answer word.
#
#13. Once you have a reduced list of possible answer words in ok_words_1 or ok_words_2,
#    you might want to restrict the probe words to possible answers. This gives you a shot
#    at nailing the answer on the next try. But if your guess is wrong you might not
#    learn as much from it as choosing from among all probe words.
#    To restrict candidate probe words to being only possible answer words,
#    pass the remaining allowable words as the candidate_probe_word_list argument,
#    like this:
##>>> scores_list_2 = wa.scoreProbeWords(ok_words_2, ok_words_2)
#
#14. Hard Mode
#    In Hard Mode, your probe word has to be one that meets the cue constraints already
#    provided by game responses.  Pass the char_constraints you have accumulated so far.
#    To obtain scores for candidate probe words, pass the most recent char_constraints_list
#    as an optional argument to the scoreProbeWords() function:
#
#>>> scores_list_2h = wa.scoreProbeWords(ok_words_2, ok_words_2, cc2)
#
################################################################################



#Program Notes:
#-I tried using numpy arrays to store character constraints for efficiency, but that
# turned out to be slower than just using sets.  I didn't figure out why.



################################################################################
#
#wordleAssistant program
#

gl_char_set = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
               'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
               'u', 'v', 'w', 'x', 'y', 'z')


#word list is a list of remaining candidate answer words.
#cue_list a list of two entries:   [probe_word, char_response_list]
#   where probe_word is a 5-character word
#   and response list is a list of 5 cues in the set { 'r', 'l', 'y' }
#   where 'r' means gReen  - the character is in the right position
#         'l' means yeLLow - the character is in the word but not in that position
#         'y' means graY   - the character is not in the word
#char_constraint_list is a list of list:
#  char_constraint_list[0]-char_constraint_list[4]  are sets of allowed characters
#    in each char position
#  char_constraint_list[5] is a set of characters that must appear somewhere.
#
#This function applies cue_list to adjust char_constraint_list and then filters
#allowable answer words.
#Returns two values:  new_allowable_word_list, new_char_constraint_list
#If you pass in a char_constraint_list that already constrains some of the characters,
#then the new_char_constraint_list returned will add constraints to that based on
#the cue_list.  This allows you to accumulate constraints for filtering qualified
#probe words in hard mode.
#It is not necessary to pass in previous cues (responses to probes) directly because
#we expect that word_list will have filtered any non-allowable words from
#previous probes.  In hard mode, this information is carried in the
#char_constraint_list argument.
def pruneWordsPerProbeResponse(word_list, cue_list, char_constraint_list = None):
    if char_constraint_list == None:
        char_constraint_list = makeCharConstraintList()
    new_char_constraint_list = updateCharConstraintList(cue_list, char_constraint_list)
    ok_words = pruneWordsPerCharConstraints(word_list, new_char_constraint_list)
    return ok_words, new_char_constraint_list



#Run through all words in candidate_probe_word_list and test it as the probe word.
#For each such probe word, run through all words in remaining_word_list pretending
#it is the correct word.  For each hypothesized correct word compute the
#cue_list, and from that, a hypothetical char_constraint_list.
#Using this char_constraint_list, count how many remaining words are allowable.
#Score each probe word by the average and max number of remaining words that
#would be returned if the probe word were entered.
#If probe_word_char_constraint_list is passed, then this is used to filter the probe words
#so that they meet char constraints from previous cues.  This is used for "hard mode"
#in which you can only submit probe words that meet all cues returned by previous
#submissions.
#Returns a list of tuple: (probe_word, ave_words_remaining, max_words_remaining)
def scoreProbeWords(remaining_word_list, candidate_probe_word_list,
                    probe_word_char_constraint_list = None,
                    print_p = False):
    probe_word_score_list = []
    if probe_word_char_constraint_list != None:
        qualified_candidate_probe_word_list = \
             pruneWordsPerCharConstraints(candidate_probe_word_list, probe_word_char_constraint_list)
        print('Hard Mode: pruning candidate_probe_word_list down from ' + str(len(candidate_probe_word_list)) + ' to ' + str(len(qualified_candidate_probe_word_list)) + ' candidates that meet char constraints')
    else:
        qualified_candidate_probe_word_list = candidate_probe_word_list
    probe_word_count = 0
    for probe_word in qualified_candidate_probe_word_list: #consider all candidate probe words, even ones
                                                           #that are not allowable 
        remaining_words_sum = 0
        max_remaining_words = 0
        for hypothetical_correct_word in remaining_word_list:
            char_response_list = markProbeWordAgainstCorrectWord(probe_word, hypothetical_correct_word)
            new_remaining_word_list, new_char_constraint_list = \
                 pruneWordsPerProbeResponse(remaining_word_list,
                                            [probe_word, char_response_list])
            num_remaining_words = len(new_remaining_word_list)
            remaining_words_sum += num_remaining_words
            max_remaining_words = max(num_remaining_words, max_remaining_words)

        ave_remaining_words = remaining_words_sum / len(remaining_word_list)
        probe_word_score = [probe_word, ave_remaining_words, max_remaining_words]
        probe_word_count += 1
        if probe_word_count % 1000 == 0 or print_p:
            print(str(probe_word_count) + '  ' + str(probe_word_score))
        probe_word_score_list.append(probe_word_score)
    probe_word_score_list.sort(key = lambda x: x[1])
    print('top scores:')
    for score in probe_word_score_list[0:20]:
        print(str(score))
    return probe_word_score_list
            

#score_list is a list of tuple:  (word, float average_allowable_words, float max_allowable_words)
#This returns a list of scores that have word in allowable_words.
#This is useful if you want to restrict your probe word to one of the remaining allowable words
#but you want to choose the one with the best score).
def getScoresWithAllowableWords(score_list, allowable_words):
    ok_scores = []
    for score_tup in score_list:
        word = score_tup[0]
        if word in allowable_words:
            ok_scores.append(score_tup)
    return ok_scores

#This is a utility to see what scores some possible probe word have
#prints them in order of average remaining words.
def printScoresForWords(score_list, word_list):
    ok_scores = []
    for score in score_list:
        if score[0] in word_list:
            ok_scores.append(score)
    ok_scores.sort(key = lambda x: x[1])
    for score in ok_scores:
        print(str(score))


#this is a utility to see what score a probe word has
def getScoreForWord(score_list, word):
    for score in score_list:
        if score[0] == word:
            return score

        

#char_constraint_list is a list of list
#  list[0]-list[4]  are sets of allowed characters in each char position
#  list[5] is a set of characters that must appear somewhere
def printCharConstraintList(char_constraint_list):
    for i in range(5):
        print(str(i) + ' ' + str(char_constraint_list[i]))
    print('required: ' + str(char_constraint_list[5]))


        

#returns a list length 5 in the range {'r', 'l', 'y'}
#This emulates what the Wordle game does when you enter a probe word.
def markProbeWordAgainstCorrectWord(probe_word, correct_word):
    char_response_list = []
    for i in range(5):
        probe_char_i = probe_word[i]
        if correct_word[i] == probe_char_i:
            char_response_list.append('r')
        elif correct_word.find(probe_char_i) >= 0:
            char_response_list.append('l')
        else:
            char_response_list.append('y')
    return char_response_list
        



#create an initial char_constraint_list
#Returns: char_constraint_list:  list of length 6
#  The first 5 elements are sets of all chars, meaning that each position is
#  unconstrained and could take any char.
#  Element 6 is an empty set meaning that there is not as of yet any requirement
#  that the word take any char.
def makeCharConstraintList():
    char_constraint_list = []
    for i in range(5):
        char_constraint_list.append(set(gl_char_set))  #the elements are sets for effeciency
    char_constraint_list.append(set())
    return char_constraint_list


#Applies the character constraints in char_constraint_list to filter out unallowable
#words from word_list.
#Returns a list of allowable words.
def pruneWordsPerCharConstraints(word_list, char_constraint_list):
    ok_words = []
    for word in word_list:
        ok_p = True
        for i in range(5):
            if i >= len(word):
                print('word is too short: ' + word + ' i: ' + str(i))
                return
            char_i = word[i]
            if char_i not in char_constraint_list[i]:
                ok_p = False
                break
        for required_char in char_constraint_list[5]:
            if word.find(required_char) < 0:
                ok_p = False
                break
        if ok_p:
            ok_words.append(word)
    return ok_words


#char_constraint_list is a list of list of char
#The first 5 elements are char positions, for chars allowed in that position.
#The 6th is a list of chars that the word must have somewhere.
#cue_list a list of two entries:   [probe_word, char_response_list]
#where char_response_list is a list of 5 strings like   ['y', 'y', 'l', 'r', 'l']
#This returns a new char_constraint_list that updates the char_constraint_list
#passed according to the char_responses in cue_list.
#Does not modify char_constraint_list.
def updateCharConstraintList(cue_list, char_constraint_list):
    new_char_constraint_list = [ set(pos_chrs) for pos_chrs in char_constraint_list ]
    probe_word = cue_list[0]
    char_response_list = cue_list[1]
    for i_pos in range(5):
        probe_char = probe_word[i_pos]
        char_response = char_response_list[i_pos]
        if char_response == 'y':        #gray - remove probe_char entirely
            for i_pos in range(5):
                new_char_constraint_list[i_pos].discard(probe_char)
        elif char_response == 'l':      #yellow - remove probe_char only from i_pos chars
            new_char_constraint_list[i_pos].discard(probe_char)
            new_char_constraint_list[5].add(probe_char)         #but add to required set 
        elif char_response == 'r':      #green - only probe_char allowed in i_pos chars
            new_char_constraint_list[i_pos] = set([probe_char])
            new_char_constraint_list[5].add(probe_char)         #and add to required set   
        else:
            print('unrecognized char_response: ' + str(char_response))
            return
    return new_char_constraint_list




#development
def test1():
    word_list = importWordList()
    
    char_response_list = ['house', ['r', 'r', 'r', 'r', 'r']]
    print('\n' + str(char_response_list))
    ok_words, new_char_constraint_list = pruneWordsPerProbeResponse(word_list, char_response_list)
    print(str(len(ok_words)))
    if len(ok_words) < 20:
        print(str(ok_words))
    printCharConstraintList(new_char_constraint_list)

    char_response_list = ['house', ['l', 'l', 'l', 'l', 'l']]
    print('\n' + str(char_response_list))
    ok_words, new_char_constraint_list = pruneWordsPerProbeResponse(word_list, char_response_list)
    print(str(len(ok_words)))
    if len(ok_words) < 20:
        print(str(ok_words))
    printCharConstraintList(new_char_constraint_list)
    


def importWordList(word_filename = None):
    if word_filename == None:
        word_filename = gl_word_filename
    word_list = []
    with open(word_filename, encoding='utf8') as file:
        for line in file:
            if line.find('#') >= 0:
                continue
            word = line[:-1]
            if len(word) != 5:
                continue
            word_list.append(word)
    return word_list

#Collected from the wordle javascript file
#https://www.powerlanguage.co.uk/wordle/main.e65ce0a5.js
gl_probe_word_filename = 'wordle-probe-words.text'
gl_answer_word_filename = 'wordle-answer-words.text'

gl_probe_word_list = importWordList(gl_probe_word_filename)
gl_answer_word_list = importWordList(gl_answer_word_filename)

#
#
################################################################################
